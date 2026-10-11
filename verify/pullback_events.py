#!/usr/bin/env python3
"""Source-independent BTC hourly OHLC pullback event extraction for CN v2 tests.

The caller must prove that each bar is from the frozen eligible source and
period. This routine never makes a market warning; it only derives a factual
post-window event and declines to score if coverage is not complete.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone


def parse_utc(v: str) -> datetime:
    if not isinstance(v, str):
        raise ValueError("missing_utc")
    result = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if result.utcoffset() != timedelta(0):
        raise ValueError("non_utc_timestamp")
    return result.astimezone(timezone.utc)


def analyze_hourly_btc_pullback(
    rows: list[dict],
    *,
    window_start_utc: str,
    window_end_utc: str,
    threshold_pct: float = 5.0,
    recovery_fraction: float = 0.5,
) -> dict:
    start, end = parse_utc(window_start_utc), parse_utc(window_end_utc)
    if start.minute or start.second or end.minute or end.second or start.microsecond or end.microsecond:
        raise ValueError("hour_alignment_required")
    duration = (end - start).total_seconds()
    if duration <= 0 or duration % 3600:
        raise ValueError("window_must_span_whole_hours")
    if not isinstance(threshold_pct, (int, float)) or isinstance(threshold_pct, bool) or not math.isfinite(threshold_pct) or threshold_pct <= 0:
        raise ValueError("threshold_invalid")
    if not isinstance(recovery_fraction, (float, int)) or not 0 < recovery_fraction <= 1:
        raise ValueError("recovery_fraction_invalid")
    stamps = [parse_utc(r["hour_start_utc"]) for r in rows]
    ordered = sorted(zip(stamps, rows), key=lambda x: x[0])
    expected = int(duration // 3600)
    if len(ordered) != expected or len(set(stamps)) != expected:
        return {"coverage": "INCOMPLETE", "expected_hours": expected, "observed_hours": len(ordered),
                "event_occurred": None, "onset_utc": None, "recovery_utc": None}
    for i, (stamp, bar) in enumerate(ordered):
        if stamp != start + timedelta(hours=i):
            return {"coverage": "INCOMPLETE", "expected_hours": expected, "observed_hours": len(ordered),
                    "event_occurred": None, "onset_utc": None, "recovery_utc": None}
        high, low = bar.get("high"), bar.get("low")
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in (high,low)) or not 0 < low <= high:
            raise ValueError("bad_market_ohlc")
    running_peak = None
    running_peak_time = None
    trigger = None
    first_peak = None
    trough = None
    trough_time = None
    max_drawdown = 0.0
    for stamp, bar in ordered:
        high = float(bar["high"])
        low = float(bar["low"])
        if running_peak is not None:
            drawdown = 100 * (running_peak - low) / running_peak
            max_drawdown = max(max_drawdown, drawdown)
            if trigger is None and drawdown >= threshold_pct:
                trigger = stamp
                first_peak = running_peak
                trough = low
                trough_time = stamp
            elif trigger is not None and low < trough:
                trough = low
                trough_time = stamp
        # IMPORTANT: today's peak cannot be assumed to have preceded today's low.
        # Only prior full-bar high is eligible to establish an hourly threshold cross.
        if running_peak is None or high > running_peak:
            running_peak = high
            running_peak_time = stamp
    recovered = None
    if trigger is not None:
        level = trough + recovery_fraction * (first_peak - trough)
        for stamp, bar in ordered:
            if stamp > trough_time and float(bar["high"]) >= level:
                recovered = stamp
                break
    onset = trigger.isoformat().replace("+00:00", "Z") if trigger else None
    last = trough_time.isoformat().replace("+00:00", "Z") if trough_time else None
    recovery = recovered.isoformat().replace("+00:00", "Z") if recovered else None
    return {
        "contract": "CN_V2_PULLBACK_EVENT_OBSERVATION_v1",
        "coverage": "COMPLETE",
        "expected_hours": expected,
        "observed_hours": expected,
        "threshold_pct": threshold_pct,
        "recovery_fraction": recovery_fraction,
        "event_occurred": bool(trigger),
        "onset_utc": onset,
        "trough_utc": last,
        "recovery_utc": recovery,
        "right_censored": bool(trigger and not recovered),
        "max_drawdown_pct": round(max_drawdown, 6),
        "severity": "MAJOR" if max_drawdown >= 10 else "MATERIAL" if max_drawdown >= 5
                    else "SMALL" if max_drawdown >= 3 else "NONE",
        "note": "Peak-before-low is enforced across different hourly bars. Recovery strictly follows the final trough bar; exact intrabar order remains unknown.",
    }
