from __future__ import annotations
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_cn_v2_claims import evaluate

H = "a" * 64
E = "b" * 64
ISSUED = "2026-10-12T07:05:00Z"
START = "2026-10-12T08:00:00Z"
END = "2026-10-13T08:00:00Z"
BASE = {
    "claim_id": "CN29-W42-PB-24H-001", "public_issue_number": 29,
    "forecast_week": "2026-W42", "source_sha256": H, "issued_at_utc": ISSUED,
    "evaluation_start_utc": START, "evaluation_end_utc": END,
    "metric_source_id": "BTC_USD_HOURLY_V1",
    "family": "PULLBACK_EDGE", "kind": "EVENT_OCCURRENCE",
    "threshold_pct": 5, "asset": "BTC", "expected_event": False,
    "statement_da": "Ingen materialt pullback på mindst 5% i næste 24h.",
    "statement_en": "No material >=5% BTC pullback in next 24h.",
}
OUTCOME = {
    "claim_id": BASE["claim_id"], "metric_source_id": BASE["metric_source_id"],
    "coverage": "COMPLETE", "source_sha256": E,
    "source_reference": "03_DAILY_CAPTURE_LOGS/hourly/BTC.csv#2026-10-12",
    "outcome": {"event_occurred": False, "event_threshold_pct": 5},
}
BUNDLE = {
    "contract": "CN_V2_FROZEN_CLAIMS_v1",
    "scoring_contract": "CN_EDGE_BINARY_v2_0",
    "public_issue_number": 29, "forecast_week": "2026-W42",
    "issued_at_utc": ISSUED, "source_sha256": H,
    "claims": [BASE],
}
ACTUAL = {"contract": "CN_V2_OUTCOME_OBSERVATIONS_v1", "records": [OUTCOME]}


def run(claims=None, observations=None, asof="2026-10-13T08:01:00Z"):
    claims = claims or deepcopy(BUNDLE)
    observations = observations if observations is not None else deepcopy(ACTUAL)
    return evaluate(claims, observations, cutoff_utc=asof)


class BinaryClaims(unittest.TestCase):
    def test_valid_no_warning_true_negative(self):
        x = run()
        self.assertEqual(x["outcomes"][0]["score"], 100)
        self.assertEqual(x["tally"]["SUPPORTED"], 1)
        self.assertEqual(x["coverage_pct"], 100)
        self.assertEqual(x["score_evidence_class"], "PROVISIONAL_UNLESS_EXTERNALLY_ATTESTED")

    def test_no_warning_with_real_pullback_is_missed_event_zero(self):
        o = deepcopy(ACTUAL)
        o["records"][0]["outcome"]["event_occurred"] = True
        x = run(observations=o)
        self.assertEqual(x["outcomes"][0]["score"], 0)
        self.assertEqual(x["tally"]["REFUTED"], 1)

    def test_warning_when_no_event_is_false_alarm_zero(self):
        b = deepcopy(BUNDLE)
        b["claims"][0]["expected_event"] = True
        x = run(claims=b)
        self.assertEqual(x["outcomes"][0]["score"], 0)

    def test_warning_before_event_is_hit(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0]["expected_event"] = True
        o["records"][0]["outcome"]["event_occurred"] = True
        self.assertEqual(run(b, o)["outcomes"][0]["score"], 100)

    def test_before_maturity_is_pending_not_free_100(self):
        x = run(asof="2026-10-12T20:00:00Z")
        self.assertIsNone(x["outcomes"][0]["score"])
        self.assertEqual(x["tally"]["PENDING"], 1)
        self.assertIsNone(x["claimed_accuracy_pct"])

    def test_no_coverage_is_null_not_negative(self):
        o = deepcopy(ACTUAL)
        o["records"][0]["coverage"] = "PARTIAL"
        x = run(observations=o)
        self.assertEqual(x["tally"]["NOT_EVALUABLE"], 1)
        self.assertIsNone(x["outcomes"][0]["score"])

    def test_missing_evidence_remains_null(self):
        x = run(observations={"contract": "CN_V2_OUTCOME_OBSERVATIONS_v1", "records": []})
        self.assertEqual(x["tally"]["NOT_EVALUABLE"], 1)

    def test_unknown_prediction_is_abstention_not_no_warning(self):
        b = deepcopy(BUNDLE)
        b["claims"][0]["declared_state"] = "UNKNOWN"
        x = run(claims=b)
        self.assertEqual(x["tally"]["ABSTAIN"], 1)
        self.assertIsNone(x["outcomes"][0]["score"])

    def test_late_forecast_cannot_be_scored(self):
        b = deepcopy(BUNDLE)
        b["claims"][0]["issued_at_utc"] = b["issued_at_utc"] = "2026-10-12T08:01:00Z"
        with self.assertRaisesRegex(ValueError, "forecast_not_prospective"):
            run(claims=b)

    def test_migrated_historical_issue_not_eligible(self):
        b = deepcopy(BUNDLE)
        b["public_issue_number"] = 28
        b["claims"][0]["public_issue_number"] = 28
        with self.assertRaisesRegex(ValueError, "unsupported_preprospective_issue_identity"):
            run(claims=b)

    def test_source_mismatch_rejected(self):
        b = deepcopy(BUNDLE)
        b["claims"][0]["source_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "claim_source_or_issuance_mismatch"):
            run(claims=b)

    def test_source_data_mismatch_null(self):
        o = deepcopy(ACTUAL)
        o["records"][0]["metric_source_id"] = "OTHER_V1"
        self.assertEqual(run(observations=o)["outcomes"][0]["status"], "NOT_EVALUABLE")

    def test_duplicate_evidence_rejected(self):
        o = deepcopy(ACTUAL)
        o["records"].append(deepcopy(o["records"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate_outcome_evidence"):
            run(observations=o)

    def test_older_21_day_claim_remains_pending_as_new_week_progresses(self):
        b = deepcopy(BUNDLE)
        b["claims"][0]["evaluation_end_utc"] = "2026-11-02T08:00:00Z"
        self.assertEqual(run(claims=b, asof="2026-10-19T10:00:00Z")["outcomes"][0]["status"], "PENDING")

    def test_rotational_threshold_supported(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(family="DIRECTION_ROTATION_CLAIMS",kind="METRIC_COMPARISON",metric_source_id="ETHBTC_SETTLED_V1",
                               operator="LTE",threshold=0.032,statement_da="ETHBTC lukker under",statement_en="ETHBTC closes below")
        o["records"][0].update(metric_source_id="ETHBTC_SETTLED_V1",outcome={"metric_value":0.031})
        self.assertEqual(run(b, o)["outcomes"][0]["score"], 100)

    def test_unfrozen_altcoin_basket_cannot_get_a_hit(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(kind="ALTCOIN_IMPACT",expected_impact="HIGH",metric_source_id="ALT_BASKET_TEST_V1")
        o["records"][0].update(metric_source_id="ALT_BASKET_TEST_V1",outcome={"impact_class":"HIGH"})
        x=run(b,o)
        self.assertEqual(x["outcomes"][0]["status"], "ABSTAIN")
        self.assertIsNone(x["outcomes"][0]["score"])

    def test_right_censored_pullback_end_not_falsely_scored(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(kind="END_WINDOW",earliest_utc="2026-10-12T12:00:00Z",latest_utc="2026-10-13T07:00:00Z")
        o["records"][0]["outcome"]={"right_censored":True}
        self.assertEqual(run(b,o)["outcomes"][0]["status"], "RIGHT_CENSORED")

    def test_pullback_start_outside_predicted_window_is_refuted(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(kind="START_WINDOW",earliest_utc="2026-10-12T10:00:00Z",latest_utc="2026-10-12T18:00:00Z")
        o["records"][0]["outcome"]={"onset_utc":"2026-10-13T06:00:00Z"}
        self.assertEqual(run(b,o)["outcomes"][0]["score"], 0)

    def test_predicted_start_never_occurred_is_false_alarm_not_missing(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(kind="START_WINDOW",earliest_utc="2026-10-12T10:00:00Z",latest_utc="2026-10-12T19:00:00Z")
        o["records"][0]["outcome"]={"event_occurred":False}
        result=run(b,o)
        self.assertEqual(result["outcomes"][0]["score"],0)
        self.assertEqual(result["outcomes"][0]["status"],"REFUTED")

    def test_predicted_end_without_an_event_is_false_alarm(self):
        b, o = deepcopy(BUNDLE), deepcopy(ACTUAL)
        b["claims"][0].update(kind="END_WINDOW",earliest_utc="2026-10-12T12:00:00Z",latest_utc="2026-10-13T07:00:00Z")
        o["records"][0]["outcome"]={"event_occurred":False}
        self.assertEqual(run(b,o)["outcomes"][0]["score"],0)

    def test_missing_metric_source_identifier_is_bad_claim(self):
        b=deepcopy(BUNDLE)
        b["claims"][0]["metric_source_id"]=""
        with self.assertRaisesRegex(ValueError, "missing_metric_source_identity"):
            run(b)


if __name__ == "__main__":
    unittest.main()
