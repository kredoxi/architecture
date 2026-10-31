#!/usr/bin/env python3
"""Validate architecture contracts using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORE_REPOSITORY = "https://api.github.com/repos/kredoxi/kredoxi"
CORE_PR_NUMBER = 1
REFERENCE_PREFIX = "kredoxi://v1/"
SEGMENT_PATTERN = r"[a-z][a-z0-9-]{0,31}"
REFERENCE_RE = re.compile(
    rf"{re.escape(REFERENCE_PREFIX)}{SEGMENT_PATTERN}/{SEGMENT_PATTERN}/{SEGMENT_PATTERN}",
    re.ASCII,
)
REQUIRED_PACKS = {
    "core/baseline",
    "core/carl",
    "core/cognition-governance",
    "core/dependency",
    "core/identity",
    "core/memory-cache",
    "core/pr-contract",
    "core/security",
    "core/tool-permission-tiers",
    "languages/go",
    "platform/cicd",
}
EVENT_FIELDS = {
    "schema_version",
    "timestamp",
    "event_type",
    "request_id",
    "authentication_method",
    "policy_decision",
    "provider_id",
    "status",
    "agent_version",
    "mode",
}
EVENT_OPTIONAL_FIELDS = {"principal_id", "reference_id", "error_category"}
CORE_STATUSES = {
    "started",
    "stopped",
    "resolved",
    "invalid_request",
    "invalid_reference",
    "authentication_denied",
    "policy_denied",
    "secret_not_found",
    "provider_unavailable",
    "broker_busy",
    "internal_failure",
    "canceled",
    "delivery_failed",
    "transport_failure",
}

_PRIVATE_KEY_MARKER = "-----BEGIN " + "PRIVATE KEY-----"
_SECRET_PATTERNS = [
    ("private-key", re.compile(re.escape(_PRIVATE_KEY_MARKER))),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "credential-assignment",
        re.compile(
            r"""(?i)\b(?:password|client[_-]?secret|api[_-]?key|access[_-]?token)\b"""
            r"""\s*[:=]\s*(['"])([^'"\r\n]{24,})\1"""
        ),
    ),
]


def strict_json_loads(text: str) -> Any:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def fenced_blocks(text: str, language: str) -> list[str]:
    return re.findall(
        rf"^```{re.escape(language)}\s*\n(.*?)^```",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )


def validate_reference(reference: str) -> bool:
    return len(reference.encode("ascii", errors="ignore")) == len(reference) and bool(
        REFERENCE_RE.fullmatch(reference)
    )


def anchor_slug(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading.lower())
    heading = re.sub(r"[^\w -]", "", heading)
    return re.sub(r"\s+", "-", heading.strip())


def markdown_problems(markdown_files: list[Path]) -> list[str]:
    problems: list[str] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        prose = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
        for destination in link_pattern.findall(prose):
            destination = destination.strip().split(maxsplit=1)[0].strip("<>")
            if destination.startswith(("https://", "http://", "mailto:")):
                continue
            target_text, separator, fragment = destination.partition("#")
            target = (path.parent / target_text).resolve() if target_text else path
            if not target.is_file():
                problems.append(f"{path.relative_to(ROOT)}: missing link target {destination}")
                continue
            if separator:
                headings = re.findall(
                    r"^#{1,6}\s+(.+?)\s*#*\s*$",
                    target.read_text(encoding="utf-8"),
                    flags=re.MULTILINE,
                )
                if fragment not in {anchor_slug(heading) for heading in headings}:
                    problems.append(f"{path.relative_to(ROOT)}: missing anchor {destination}")
    return problems


def secret_matches(text: str) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in _SECRET_PATTERNS:
            if pattern.search(line):
                findings.append((line_number, name))
    return findings


def scan_for_secrets() -> list[str]:
    findings: list[str] = []
    ignored = {".git", "__pycache__", ".venv", "venv"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, name in secret_matches(text):
            findings.append(f"{path.relative_to(ROOT)}:{line_number}: {name}")
    return findings


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "kredoxi-architecture-ci"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read(1_000_001).decode("utf-8")


def pinned_core_revision(contracts: str) -> str:
    pinned = re.search(
        r"https://github\.com/kredoxi/kredoxi/blob/([0-9a-f]{40})/docs/protocol\.md",
        contracts,
    )
    if pinned is None:
        raise ValueError("Architecture contracts must pin the reviewed Core protocol source")
    return pinned.group(1)


def current_core_protocol(contracts: str) -> tuple[str, str]:
    main_url = "https://raw.githubusercontent.com/kredoxi/kredoxi/main/docs/protocol.md"
    try:
        return "main", fetch_text(main_url)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise

    pull = strict_json_loads(fetch_text(f"{CORE_REPOSITORY}/pulls/{CORE_PR_NUMBER}"))
    if pull.get("state") != "open":
        revision = pinned_core_revision(contracts)
        url = f"https://raw.githubusercontent.com/kredoxi/kredoxi/{revision}/docs/protocol.md"
        return f"pinned Core revision {revision}", fetch_text(url)
    revision = pull["head"]["sha"]
    url = f"https://raw.githubusercontent.com/kredoxi/kredoxi/{revision}/docs/protocol.md"
    return revision, fetch_text(url)


def json_examples(contracts: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    examples = [strict_json_loads(block) for block in fenced_blocks(contracts, "json")]
    policy = next((item for item in examples if isinstance(item, dict) and "allow" in item), None)
    request = next((item for item in examples if isinstance(item, dict) and "reference" in item), None)
    event = next(
        (
            item
            for item in examples
            if isinstance(item, dict) and "schema_version" in item and "request_id" in item
        ),
        None,
    )
    if not all((policy, request, event)):
        raise ValueError("contracts.md must contain policy, request and event JSON examples")
    return policy, request, event


def require_contains(source: str, phrases: set[str], context: str) -> None:
    missing = sorted(phrase for phrase in phrases if phrase not in source)
    if missing:
        raise ValueError(f"{context} is missing: {', '.join(missing)}")


def validate_core_contract(core: str, contracts: str, adr: str) -> None:
    core_segment = re.search(r"(?m)^segment\s*=\s*(.+?)\s*$", core)
    if core_segment is None:
        raise ValueError("Core protocol does not document a reference segment grammar")
    if "[a-z][a-z0-9-]{0,31}" not in contracts or core_segment.group(1) != "[a-z][a-z0-9-]{0,31}":
        raise ValueError("Architecture reference grammar diverges from Core")

    policy, request, event = json_examples(contracts)
    core_json = [strict_json_loads(block) for block in fenced_blocks(core, "json")]
    core_policy = next((item for item in core_json if isinstance(item, dict) and "allow" in item), None)
    core_request = next((item for item in core_json if isinstance(item, dict) and "reference" in item), None)
    if policy != core_policy:
        raise ValueError("Architecture policy example diverges from Core")
    if request != core_request or set(request) != {"reference"}:
        raise ValueError("Architecture resolve request diverges from Core")
    if not validate_reference(request["reference"]):
        raise ValueError("Architecture resolve request contains an invalid reference")

    compact_contract = re.sub(r"\s+", " ", contracts)
    compact_core = re.sub(r"\s+", " ", core)
    require_contains(
        compact_contract,
        {"Resolve(context.Context, Reference) (string, error)", "POST /v1/resolve"},
        "Architecture protocol",
    )
    require_contains(
        compact_core,
        {
            "type Provider interface",
            "Resolve(context.Context, Reference) (string, error)",
            "Loopback IPv4 only",
            "TLS 1.3",
            "Cache-Control: no-store",
            "connection closure",
            "no environment proxy support",
        },
        "Core protocol",
    )
    status_pairs = [
        ("200", "none"),
        ("400", "invalid_request"),
        ("400", "invalid_reference"),
        ("401", "authentication_denied"),
        ("403", "policy_denied"),
        ("503", "secret_not_found"),
        ("503", "provider_unavailable"),
        ("503", "canceled"),
        ("503", "broker_busy"),
        ("503", "telemetry_unavailable"),
    ]
    for status, category in status_pairs:
        category_pattern = r"none" if category == "none" else rf"`{re.escape(category)}`"
        if not re.search(rf"\|\s*{status}\s*\|[^|\n]*{category_pattern}", contracts):
            raise ValueError(f"Architecture status table missing {status}/{category}")
        if category != "none" and category not in core:
            raise ValueError(f"Core protocol status table missing {category}")
    if not re.search(r"\|\s*403\s*\|\s*`policy_denied`", contracts):
        raise ValueError("Policy denial must remain 403")
    if not re.search(r"\|\s*503\s*\|\s*`secret_not_found`", contracts):
        raise ValueError("Allowed but absent secrets must remain 503")
    require_contains(
        contracts,
        {
            "unallowlisted reference",
            "without querying whether that reference exists",
            "already authorized",
            "secret_not_found",
            "RFC3339Nano",
            "HMAC-SHA256",
        },
        "Enumeration, event and timestamp contract",
    )

    limit_pairs = (
        ("16", "16 live pre-TLS connections"),
        ("8", "8 active handler resolutions"),
        ("4096", "4 KiB header setting"),
        ("1024 bytes", "1 KiB request body"),
        ("2048 bytes", "2 KiB response parsing bound"),
        ("Depth 8", "JSON nesting depth 8"),
        ("1 / 2 / 4 / 2 seconds", "Header timeout 1s, read timeout 2s, write timeout 4s, idle timeout 2s"),
        ("2 / 8 / 5 seconds", "provider deadline 2s, client overall timeout 8s, graceful shutdown budget 5s"),
    )
    for documented, source in limit_pairs:
        if documented not in contracts or source not in core:
            raise ValueError(f"Configured Core resource bound diverges: {documented}")

    missing_event_fields = EVENT_FIELDS - set(event)
    if missing_event_fields:
        raise ValueError(f"Architecture event example omits: {', '.join(sorted(missing_event_fields))}")
    if not set(event).issubset(EVENT_FIELDS | EVENT_OPTIONAL_FIELDS):
        raise ValueError("Architecture event example contains fields outside Core schema")
    if event["mode"] != "enforcement" or event["provider_id"] != "synthetic":
        raise ValueError("Architecture event example diverges from Core enumerations")
    if not all(status in core for status in CORE_STATUSES) or not all(
        status in contracts for status in CORE_STATUSES
    ):
        raise ValueError("Architecture event status set diverges from Core")
    require_contains(
        adr,
        {"Status: **Proposed**", "policy-before-provider", "policy_denied", "secret_not_found"},
        "ADR acceptance and enumeration decision",
    )


def validate_carl(effective_path: Path, status_path: Path, doctor_path: Path) -> None:
    effective = strict_json_loads(effective_path.read_text(encoding="utf-8-sig"))
    actual = {pack["id"] for pack in effective.get("packs", [])}
    if actual != REQUIRED_PACKS:
        raise ValueError(
            f"Unexpected cARL effective pack set; missing={sorted(REQUIRED_PACKS - actual)}, "
            f"extra={sorted(actual - REQUIRED_PACKS)}"
        )
    status = status_path.read_text(encoding="utf-8-sig")
    if not re.search(r"(?m)^Status:\s+Healthy\s*$", status):
        raise ValueError("cARL status did not report Healthy")
    doctor = doctor_path.read_text(encoding="utf-8-sig")
    if re.search(r"(?m)^(?:ERROR|WARNING)\b", doctor):
        raise ValueError("cARL doctor reported an error or warning")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in (ROOT / "docs").rglob("*.md")
        if path.is_file()
    ) + [ROOT / "README.md"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--effective", type=Path, required=True)
    parser.add_argument("--carl-status", type=Path, required=True)
    parser.add_argument("--carl-doctor", type=Path, required=True)
    parser.add_argument("--core-protocol", type=Path)
    arguments = parser.parse_args()

    try:
        markdown = markdown_files()
        problems = markdown_problems(markdown)
        problems.extend(scan_for_secrets())
        if problems:
            raise ValueError("\n".join(problems))

        contracts = (ROOT / "docs" / "contracts.md").read_text(encoding="utf-8")
        adr = (ROOT / "docs" / "adr" / "0001-explicit-local-resolution.md").read_text(
            encoding="utf-8"
        )
        if arguments.core_protocol:
            core = arguments.core_protocol.read_text(encoding="utf-8-sig")
            revision = "provided local Core protocol snapshot"
        else:
            revision, core = current_core_protocol(contracts)
        validate_core_contract(core, contracts, adr)
        pinned_protocol = fetch_text(
            f"https://raw.githubusercontent.com/kredoxi/kredoxi/{pinned_core_revision(contracts)}/docs/protocol.md"
        )
        validate_core_contract(pinned_protocol, contracts, adr)
        validate_carl(arguments.effective, arguments.carl_status, arguments.carl_doctor)

        reference_rows = re.findall(
            r"(?m)^\|\s*`([^`]+)`\s*\|\s*(Valid|Reject|Unsupported)",
            contracts,
        )
        if not reference_rows:
            raise ValueError("No reference grammar examples found")
        for value, expected in reference_rows:
            valid = validate_reference(value)
            if valid != (expected == "Valid"):
                raise ValueError(f"Reference example disagrees with grammar: {value}")

        print(f"PASS: {len(markdown)} Markdown files and relative links")
        print(f"PASS: reference grammar ({len(reference_rows)} acceptance/rejection examples)")
        print("PASS: policy, request, event examples and Core protocol/status/resource contract")
        print(f"PASS: Core protocol source ({revision}) and pinned cross-repository reference")
        print("PASS: cARL healthy status and exact effective policy")
        print("PASS: obvious-secret scan")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, urllib.error.URLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
