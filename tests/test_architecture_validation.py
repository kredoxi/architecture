import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_architecture import secret_matches, strict_json_loads, validate_reference


class ArchitectureValidationTests(unittest.TestCase):
    def test_reference_grammar_boundaries(self):
        self.assertTrue(validate_reference("kredoxi://v1/a/b/c"))
        self.assertTrue(validate_reference("kredoxi://v1/a-/b9/c-"))
        self.assertTrue(validate_reference("kredoxi://v1/" + "/".join(["a" * 32] * 3)))
        for value in (
            "kredoxi://v1/" + "/".join(["a" * 33] * 3),
            "kredoxi://v1/A/b/c",
            "kredoxi://v1/a/b-/c?version=1",
            "kredoxi://v1/a/../c",
            "kredoxi://v1/a/%62/c",
            "prefix-kredoxi://v1/a/b/c",
        ):
            with self.subTest(value=value):
                self.assertFalse(validate_reference(value))

    def test_strict_json_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            strict_json_loads('{"reference":"a","reference":"b"}')

    def test_secret_scanner_detects_only_obvious_credentials(self):
        fixtures = (
            'key: "-----BEGIN ' + "PRIVATE KEY-----" + '"',
            "token=ghp_" + ("A" * 40),
            "access_token='" + ("x" * 30) + "'",
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture[:12]):
                self.assertTrue(secret_matches(fixture))
        self.assertFalse(secret_matches("DATABASE_PASSWORD=kredoxi://v1/demo/example/password"))
        self.assertFalse(secret_matches('token="${TOKEN_FROM_RUNTIME}"'))


if __name__ == "__main__":
    unittest.main()
