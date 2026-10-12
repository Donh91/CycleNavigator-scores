"""Verify W42 public score index readback and settled pre-v2 CN28, not ex-ante proof."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def material(root: Path):
    index = json.loads((root / "v2/scorebook-index.json").read_text(encoding="utf-8"))
    receipt = json.loads((root / "v2/source-receipts/2026/W42/CN29_PROVISIONAL_SOURCE_READBACK.json").read_text(encoding="utf-8"))
    card = json.loads((root / "scores/2026/W41/CN28/CANONICAL_PUBLIC_SCORECARD.json").read_text(encoding="utf-8"))
    return index, receipt, card


def validate(index: dict, receipt: dict, card: dict) -> None:
    assert index["contract"] == "CN_V2_PUBLIC_SCORE_INDEX_v1"
    assert index["first_eligible_public_issue_number"] == 29
    assert receipt["contract"] == "CN_V2_SOURCE_READBACK_PROVISIONAL_v1"
    freeze = index["current_frozen_forecast"]
    assert freeze["source_issue_number"] == 29
    assert freeze["forecast_week"] == "2026-W42"
    assert freeze["source_issue_number"] == receipt["public_issue_number"]
    assert freeze["forecast_week"] == receipt["forecast_week"]
    assert freeze["source_weekly_issued_at_utc"] == receipt["frozen_at_utc"]
    assert freeze["scoring_valid_from_utc"] == receipt["first_eligible_hour_utc"]
    assert freeze["source_manifest_sha256"] == receipt["original_manifest_sha256"]
    assert receipt["source_git_blob_sha1"] == "798a0d193a3ee0d5914d1d4d1c3501bf0aabe341"
    assert freeze["source_claim_count"] == receipt["claims_total"] == 10
    assert freeze["eligible_binary_claims"] == receipt["binary_eligible_claims"] == 0
    assert freeze["abstained_claims"] == receipt["abstained_claims"] == 10
    assert freeze["original_source_risk_state"] == receipt["pullback_risk_at_freeze"] == "BUILDING"
    assert freeze["v2_score"] is None
    assert index["latest_matured_score"] is None
    assert receipt["settled_v2_results"] == 0
    assert receipt["independent_forecast_before_outcome_proof"] is False
    assert receipt["immutable_release_verified"] is False
    assert receipt["external_timestamp_anchor_confirmed"] is False
    assert receipt["mirror_publication_timestamp_proves_pre_window"] is False
    assert index["verification"]["immutable_release_enabled_and_verified"] is False
    assert index["verification"]["external_anchor_confirmed"] is False
    assert index["verification"]["independent_outcome_reproduction"] is False
    assert index["latest_completed_price_range_before_v2"]["public_issue_number"] == 28
    assert index["latest_completed_price_range_before_v2"]["forecast_week"] == "2026-W41"
    assert card["contract"] == "CN_PUBLIC_WEEKLY_SCORECARD_v1"
    assert card["public_issue_number"] == 28
    assert card["forecast_week"] == "2026-W41"
    assert card["market_structure_precision"] is None
    assert card["combined_score"] is None
    price = card["price_range_precision"]
    assert price["formula"] == "70pct_containment_plus_30pct_jaccard"
    assert price["score"] == index["latest_completed_price_range_before_v2"]["score"] == 49.56
    assert price["actuals_hourly_coverage"] == 168
    assert len(price["rows"]) == 6
    assert sorted((row["asset"], row["window"]) for row in price["rows"]) == sorted(
        (asset, window) for asset in ("BTC", "ETH")
        for window in ("day_1_2", "day_3_4", "day_5_7")
    )
    assert all(0 <= row["score"] <= 100 and row["actual_low"] <= row["actual_high"]
               and row["forecast_low"] < row["forecast_high"] for row in price["rows"])
    assert index["score_families"]["DIRECTION_ROTATION_CLAIMS"]["status"] == "W42_FROZEN_QUALITATIVE_ONLY_ALL_ABSTAIN"
    assert index["score_families"]["PULLBACK_EDGE"]["status"] == "W42_PULLBACK_BUILDING_IS_WATCH_NOT_NUMERIC_WARNING_ABSTAIN"


class PublicReadbackTests(unittest.TestCase):
    def test_actual_readback_integrity_and_era(self):
        validate(*material(ROOT))

    def test_no_fake_binary_precision(self):
        i, r, c = material(ROOT)
        i["current_frozen_forecast"]["v2_score"] = 100
        with self.assertRaises(AssertionError):
            validate(i, r, c)

    def test_abstain_not_automatically_true_negative(self):
        i, r, c = material(ROOT)
        r["binary_eligible_claims"] = 10
        with self.assertRaises(AssertionError):
            validate(i, r, c)

    def test_wrong_maturity_or_public_cn_fails(self):
        i, r, c = material(ROOT)
        c["public_issue_number"] = 29
        with self.assertRaises(AssertionError):
            validate(i, r, c)

    def test_same_week_score_forbidden(self):
        i, r, c = material(ROOT)
        c["forecast_week"] = "2026-W42"
        with self.assertRaises(AssertionError):
            validate(i, r, c)

    def test_claimed_independent_proof_rejected(self):
        i, r, c = material(ROOT)
        r["external_timestamp_anchor_confirmed"] = True
        with self.assertRaises(AssertionError):
            validate(i, r, c)

    def test_old_structure_percentage_rejected(self):
        i, r, c = material(ROOT)
        c["market_structure_precision"] = 91
        with self.assertRaises(AssertionError):
            validate(i, r, c)


if __name__ == "__main__":
    unittest.main()
