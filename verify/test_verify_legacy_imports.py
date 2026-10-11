"""Zero-network integrity and negative-case tests for staged CN score mirror."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_legacy_imports import run


class MirrorTests(unittest.TestCase):
    def make_repo(self, root: Path, issue: int = 27, market_structure=None):
        scorepath = "scores/2026/W40/CN27/CANONICAL_PUBLIC_SCORECARD.json"
        record = {
            "contract": "CN_PUBLIC_WEEKLY_SCORECARD_v1",
            "public_issue_number": issue,
            "forecast_week": "2026-W40",
            "market_structure_precision": market_structure,
            "combined_score": None,
            "price_range_precision": {"score": 82.05}
        }
        blob = json.dumps(record, sort_keys=True).encode()
        target = root / scorepath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        git_sha = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        index = {
            "contract": "CN_LEGACY_IMPORT_INDEX_v1",
            "entries": [{
                "public_issue_number": 27,
                "forecast_week": "2026-W40",
                "source_blob_sha1": git_sha,
                "copy": scorepath
            }]
        }
        (root / "LEGACY_IMPORT_INDEX.json").write_text(json.dumps(index), encoding="utf-8")
        return target

    def test_valid_staged_copy_is_not_ex_ante_verified(self):
        with TemporaryDirectory() as d:
            self.make_repo(Path(d))
            result = run(Path(d), False)
            self.assertEqual(result["error_count"], 0, result)
            self.assertEqual(result["status"], "STAGED_BYTE_INTEGRITY_PASS_NOT_INDEPENDENT_PROOF")
            self.assertFalse(result["verified_independent_ex_ante_proof"])

    def test_tampered_bytes_fail(self):
        with TemporaryDirectory() as d:
            target = self.make_repo(Path(d))
            obj = json.loads(target.read_text())
            obj["price_range_precision"]["score"] = 99.99
            target.write_text(json.dumps(obj))
            result = run(Path(d), False)
            self.assertIn("BLOB_HASH_MISMATCH_CN27", result["errors"])

    def test_wrong_public_issue_fails_even_if_bytes_are_hash_matched(self):
        with TemporaryDirectory() as d:
            self.make_repo(Path(d), issue=28)
            result = run(Path(d), False)
            self.assertIn("WRONG_SERIES_IDENTITY_CN27", result["errors"])

    def test_forbidden_post_26_structure_percentage_fails(self):
        with TemporaryDirectory() as d:
            self.make_repo(Path(d), market_structure=81)
            result = run(Path(d), False)
            self.assertIn("FORBIDDEN_POST_CN26_MARKET_STRUCTURE_SCORE_CN27", result["errors"])

    def test_missing_copy_fails(self):
        with TemporaryDirectory() as d:
            target = self.make_repo(Path(d))
            target.unlink()
            result = run(Path(d), False)
            self.assertTrue(any(x.startswith("READ_OR_JSON_FAIL") for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()
