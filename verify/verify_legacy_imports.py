#!/usr/bin/env python3
"""CN public score mirror integrity check. Not independent ex-ante proof.

Usage: python3 verify/verify_legacy_imports.py [--root .] [--online]
Requires Python stdlib only. Reads staged local score copies, checks their
canonical Git blob SHA-1 and semantic public-series identity. The optional
online mode compares exact bytes with current source public GitHub main,
but a mutable Git source is NOT a time or immutability attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import urllib.request


def git_blob_sha1(blob: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\\0" + blob).hexdigest()


def run(root: pathlib.Path, online: bool) -> dict:
    index = json.loads((root / "LEGACY_IMPORT_INDEX.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    checked = []
    if index.get("contract") != "CN_LEGACY_IMPORT_INDEX_v1":
        errors.append("INVALID_INDEX_CONTRACT")
    for entry in index.get("entries", []):
        issue = entry["public_issue_number"]
        week = entry["forecast_week"]
        path = root / entry["copy"]
        if not path.resolve().is_relative_to(root.resolve()):
            errors.append(f"OUTSIDE_ROOT_CN{issue}")
            continue
        try:
            blob = path.read_bytes()
            card = json.loads(blob)
        except (FileNotFoundError, ValueError) as e:
            errors.append(f"READ_OR_JSON_FAIL_CN{issue}:{type(e).__name__}")
            continue
        expected = entry["source_blob_sha1"]
        actual = git_blob_sha1(blob)
        if actual != expected:
            errors.append(f"BLOB_HASH_MISMATCH_CN{issue}")
        if card.get("public_issue_number") != issue or card.get("forecast_week") != week:
            errors.append(f"WRONG_SERIES_IDENTITY_CN{issue}")
        if issue >= 27 and card.get("market_structure_precision") is not None:
            errors.append(f"FORBIDDEN_POST_CN26_MARKET_STRUCTURE_SCORE_CN{issue}")
        pr = card.get("price_range_precision")
        score = pr.get("score") if isinstance(pr, dict) else None
        if score is not None and (not isinstance(score, (float, int)) or isinstance(score, bool) or not 0 <= score <= 100):
            errors.append(f"INVALID_PRICE_RANGE_SCORE_CN{issue}")
        if card.get("combined_score") is not None and issue >= 27:
            errors.append(f"UNSUPPORTED_COMBINED_SCORE_CN{issue}")
        if online:
            # This read-back confirms current byte equality only, NOT ex-ante existence.
            suffix = f"05_CYCLE_NAVIGATOR/public_scorecards/{week[:4]}/{week[5:]}/CN{issue}_PUBLIC_SCORECARD.json"
            url = "https://raw.githubusercontent.com/" + index["source_repo"] + "/main/" + suffix
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    source_bytes = response.read()
                if source_bytes != blob:
                    errors.append(f"SOURCE_MISMATCH_CN{issue}")
            except (OSError, ValueError) as e:
                errors.append(f"SOURCE_FETCH_FAILED_CN{issue}:{type(e).__name__}")
        checked.append({"public_issue_number": issue, "forecast_week": week, "git_blob_sha1_valid": actual == expected,
                        "price_range_score": score, "proof_status": "LEGACY_ATTESTED"})
    return {
        "contract": "CN_LEGACY_MIRROR_CHECK_v1",
        "status": "STAGED_BYTE_INTEGRITY_PASS_NOT_INDEPENDENT_PROOF" if not errors else "FAIL",
        "checked_count": len(checked),
        "error_count": len(errors),
        "errors": errors,
        "records": checked,
        "verified_independent_ex_ante_proof": False,
        "warning": "A passing mirrored-scorecard integrity check is NOT a historical prediction skill, independent time attestation or immutable-release verification.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    parser.add_argument("--online", action="store_true", help="compare bytes with mutable source main; not ex-ante verification")
    args = parser.parse_args()
    result = run(args.root, args.online)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["error_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
