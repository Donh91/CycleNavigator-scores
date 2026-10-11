#!/usr/bin/env python3
"""CN v2 prospective binary claim evaluator (public, stdlib-only).

This does NOT generate market predictions, detect events, attest source time,
or compute official price-range scores. It deterministically grades typed,
already-frozen, evidence-backed claims with explicit abstentions/coverage.
Use exact input bytes/source witnesses for independent research validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

KINDS = {
    "METRIC_COMPARISON",
    "DIRECTIONAL_CLOSE",
    "EVENT_OCCURRENCE",
    "START_WINDOW",
    "END_WINDOW",
    "SEVERITY_CLASS",
    "ALTCOIN_IMPACT",
}
PULLBACK_KINDS = {"EVENT_OCCURRENCE", "START_WINDOW", "END_WINDOW", "SEVERITY_CLASS", "ALTCOIN_IMPACT"}
METRIC_KINDS = {"METRIC_COMPARISON", "DIRECTIONAL_CLOSE"}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
UTC = timezone.utc


def utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("bad_timestamp")
    v = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if v.tzinfo is None or v.utcoffset() is None:
        raise ValueError("timestamp_not_tz_aware")
    return v.astimezone(UTC)


def comparable(a: float, op: str, b: float) -> bool:
    return {
        "LT": lambda: a < b, "LTE": lambda: a <= b,
        "GT": lambda: a > b, "GTE": lambda: a >= b,
        "EQ": lambda: a == b,
    }[op]()


def safe_numeric(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def reject_or_null(out: dict, reason: str, status: str = "NOT_EVALUABLE") -> dict:
    return {**out, "status": status, "score": None, "reason": reason}


def grade_one(claim: dict, evidence: dict | None, *, cutoff: datetime) -> dict:
    cid = claim.get("claim_id")
    kind = claim.get("kind")
    family = claim.get("family")
    out = {"claim_id": cid, "family": family, "kind": kind, "status": "PENDING",
           "score": None, "reason": "NOT_YET_MATURED", "verification_status": "PROVISIONAL",
           "outcome_source_sha256": None}
    if not isinstance(cid, str) or not cid or kind not in KINDS:
        raise ValueError("invalid_claim_identity_or_kind")
    if (family == "PULLBACK_EDGE") != (kind in PULLBACK_KINDS):
        raise ValueError("claim_family_kind_mismatch")
    if family not in {"PULLBACK_EDGE", "DIRECTION_ROTATION_CLAIMS"}:
        raise ValueError("claim_family_invalid")
    start, end, issued = (utc(claim[k]) for k in
                          ("evaluation_start_utc", "evaluation_end_utc", "issued_at_utc"))
    if not issued < start < end:
        raise ValueError("forecast_not_prospective")
    if not HASH_RE.fullmatch(str(claim.get("source_sha256", ""))):
        raise ValueError("missing_original_source_digest")
    if not claim.get("statement_da") or not claim.get("statement_en"):
        raise ValueError("missing_bilingual_frozen_statement")
    if not claim.get("metric_source_id"):
        raise ValueError("missing_metric_source_identity")
    if claim.get("declared_state") in {"ABSTAIN", "UNKNOWN", "UNAVAILABLE"}:
        return reject_or_null(out, "DECLARED_NO_ELIGIBLE_PREDICTION", "ABSTAIN")
    if cutoff < end:
        return out
    if evidence is None:
        return reject_or_null(out, "OUTCOME_EVIDENCE_NOT_AVAILABLE")
    if evidence.get("claim_id") != cid:
        raise ValueError("outcome_claim_identity_mismatch")
    if evidence.get("metric_source_id") != claim["metric_source_id"]:
        return reject_or_null(out, "SOURCE_METRIC_ID_MISMATCH")
    if evidence.get("coverage") != "COMPLETE":
        return reject_or_null(out, "INCOMPLETE_OUTCOME_COVERAGE")
    digest = evidence.get("source_sha256")
    if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
        return reject_or_null(out, "MISSING_OUTCOME_SOURCE_DIGEST")
    if not evidence.get("source_reference"):
        return reject_or_null(out, "MISSING_OUTCOME_SOURCE_REFERENCE")
    out["outcome_source_sha256"] = digest
    outcome = evidence.get("outcome") or {}
    if not isinstance(outcome, dict):
        return reject_or_null(out, "INVALID_OUTCOME")
    is_true: bool | None = None
    if kind == "METRIC_COMPARISON":
        operator = claim.get("operator")
        if operator not in {"LT", "LTE", "GT", "GTE", "EQ"}:
            raise ValueError("operator_not_registered")
        expected = claim.get("threshold")
        actual = outcome.get("metric_value")
        if not safe_numeric(expected) or not safe_numeric(actual):
            return reject_or_null(out, "METRIC_NOT_EVALUABLE")
        is_true = comparable(actual, operator, expected)
    elif kind == "DIRECTIONAL_CLOSE":
        anchor = claim.get("anchor")
        tolerance_pct = claim.get("tolerance_pct")
        direction = claim.get("expected")
        actual = outcome.get("close")
        if (not all(safe_numeric(v) for v in [anchor, tolerance_pct, actual])
                or anchor <= 0 or tolerance_pct <= 0 or tolerance_pct > 50
                or direction not in {"UP", "DOWN", "SIDEWAYS"}):
            raise ValueError("direction_contract_invalid")
        delta = (actual / anchor - 1) * 100
        is_true = ((delta >= tolerance_pct) if direction == "UP" else
                   (delta <= -tolerance_pct) if direction == "DOWN" else
                   (-tolerance_pct < delta < tolerance_pct))
    elif kind == "EVENT_OCCURRENCE":
        expected = claim.get("expected_event")
        observed = outcome.get("event_occurred")
        if not isinstance(expected, bool):
            raise ValueError("expected_event_must_be_explicit_bool")
        if not isinstance(observed, bool):
            return reject_or_null(out, "EVENT_EXISTENCE_NOT_ESTABLISHED")
        if not safe_numeric(claim.get("threshold_pct")) or claim["threshold_pct"] <= 0:
            raise ValueError("event_threshold_not_frozen")
        if claim.get("asset") != "BTC":
            raise ValueError("unsupported_event_asset")
        if outcome.get("event_threshold_pct") != claim["threshold_pct"]:
            return reject_or_null(out, "EVENT_THRESHOLD_MISMATCH")
        is_true = observed is expected
    elif kind in {"START_WINDOW", "END_WINDOW"}:
        first = utc(claim["earliest_utc"])
        last = utc(claim["latest_utc"])
        if not start <= first <= last <= end:
            raise ValueError("date_window_outside_forecast_horizon")
        # A fully observed non-event is a wrong ex-ante start/end prediction, not
        # NOT_EVALUABLE. A non-event may only be declared when the same source
        # has completed the whole original horizon.
        if outcome.get("event_occurred") is False:
            return {**out, "status": "REFUTED", "score": 0,
                    "reason": "PREDICTED_PULLBACK_WINDOW_DID_NOT_OCCUR"}
        if outcome.get("right_censored") is True:
            return reject_or_null(out, "EVENT_NOT_RESOLVED_WITHIN_WINDOW", "RIGHT_CENSORED")
        when = outcome.get("onset_utc" if kind == "START_WINDOW" else "recovery_utc")
        if not when:
            return reject_or_null(out, "EVENT_TIME_NOT_OBSERVED")
        t = utc(when)
        if not start <= t <= end:
            return reject_or_null(out, "EVENT_TIME_OUTSIDE_QUALIFIED_OUTCOME")
        is_true = first <= t <= last
    elif kind == "SEVERITY_CLASS":
        expected = claim.get("expected_severity")
        depth = outcome.get("drawdown_pct")
        if expected not in {"SMALL", "MATERIAL", "MAJOR"}:
            raise ValueError("severity_class_invalid")
        if not safe_numeric(depth) or depth < 0:
            return reject_or_null(out, "DRAWDOWN_NOT_EVALUABLE")
        actual = "MAJOR" if depth >= 10 else "MATERIAL" if depth >= 5 else "SMALL" if depth >= 3 else "NONE"
        is_true = actual == expected
    elif kind == "ALTCOIN_IMPACT":
        expected = claim.get("expected_impact")
        actual = outcome.get("impact_class")
        if expected not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("invalid_predicted_alt_impact")
        if not claim.get("basket_definition_sha256") or not HASH_RE.fullmatch(str(claim["basket_definition_sha256"])):
            return reject_or_null(out, "UNFROZEN_ALTCOIN_BASKET_DEFINITION", "ABSTAIN")
        if actual not in {"LOW", "MEDIUM", "HIGH"}:
            return reject_or_null(out, "UNVERIFIED_ALTCOIN_BASKET", "ABSTAIN")
        is_true = actual == expected
    return {**out, "status": "SUPPORTED" if is_true else "REFUTED",
            "score": 100 if is_true else 0, "reason": "BINARY_PREDICATE_VERIFIED_ON_SUPPLIED_EVIDENCE"}


def evaluate(bundle: dict, observations: dict, *, cutoff_utc: str) -> dict:
    if bundle.get("contract") != "CN_V2_FROZEN_CLAIMS_v1":
        raise ValueError("wrong_claims_contract")
    if observations.get("contract") != "CN_V2_OUTCOME_OBSERVATIONS_v1":
        raise ValueError("wrong_observations_contract")
    source_issue = bundle.get("public_issue_number")
    source_week = bundle.get("forecast_week")
    if not isinstance(source_issue, int) or source_issue < 29 or not isinstance(source_week, str):
        raise ValueError("unsupported_preprospective_issue_identity")
    if bundle.get("scoring_contract") != "CN_EDGE_BINARY_v2_0":
        raise ValueError("unfrozen_method_or_wrong_method_version")
    issued = utc(bundle.get("issued_at_utc"))
    if not isinstance(bundle.get("source_sha256"), str) or not HASH_RE.fullmatch(bundle["source_sha256"]):
        raise ValueError("bundle_source_sha256_missing")
    records = bundle.get("claims")
    if not isinstance(records, list):
        raise ValueError("claims_not_array")
    evidence = observations.get("records")
    if not isinstance(evidence, list):
        raise ValueError("outcomes_not_array")
    known = {}
    for v in evidence:
        if not isinstance(v, dict) or not isinstance(v.get("claim_id"), str):
            raise ValueError("malformed_outcome_record")
        if v["claim_id"] in known:
            raise ValueError("duplicate_outcome_evidence")
        known[v["claim_id"]] = v
    result = []
    seen = set()
    for claim in records:
        if claim.get("claim_id") in seen:
            raise ValueError("duplicate_claim_identity")
        seen.add(claim["claim_id"])
        if claim.get("source_sha256") != bundle["source_sha256"] or utc(claim["issued_at_utc"]) != issued:
            raise ValueError("claim_source_or_issuance_mismatch")
        if claim.get("public_issue_number") != source_issue or claim.get("forecast_week") != source_week:
            raise ValueError("wrong_public_series_identity")
        result.append(grade_one(claim, known.get(claim["claim_id"]), cutoff=utc(cutoff_utc)))
    tally = {state: sum(r["status"] == state for r in result) for state in
             ("SUPPORTED", "REFUTED", "PENDING", "NOT_EVALUABLE", "ABSTAIN", "RIGHT_CENSORED")}
    matured = tally["SUPPORTED"] + tally["REFUTED"]
    declared = len(result) - tally["ABSTAIN"]
    return {
        "contract": "CN_V2_SCORE_SETTLEMENT_v1",
        "scoring_contract": "CN_EDGE_BINARY_v2_0",
        "public_issue_number": source_issue,
        "forecast_week": source_week,
        "source_sha256": bundle["source_sha256"],
        "as_of_utc": cutoff_utc,
        "score_evidence_class": "PROVISIONAL_UNLESS_EXTERNALLY_ATTESTED",
        "no_price_range_aggregation": True,
        "tally": tally,
        "claimed_accuracy_pct": round(100 * tally["SUPPORTED"] / matured, 2) if matured else None,
        "graded_denominator": matured,
        "declared_denominator": declared,
        "coverage_pct": round(100 * matured / declared, 2) if declared else None,
        "outcomes": result,
        "warning": "A binary score does not, alone, establish tradable edge. Independently verify market source, ex-ante release timing, baselines and overlapping-episode independence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = evaluate(json.loads(args.claims.read_text()), json.loads(args.observations.read_text()), cutoff_utc=args.as_of)
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(serialized)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
