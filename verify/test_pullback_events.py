from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pullback_events import analyze_hourly_btc_pullback

START = datetime(2026,10,12,8,tzinfo=timezone.utc)
def stamp(t): return t.isoformat().replace("+00:00","Z")
def rows(hi,lo):
    return [{"hour_start_utc":stamp(START+timedelta(hours=i)),"high":h,"low":l} for i,(h,l) in enumerate(zip(hi,lo))]
def grade(data):
    return analyze_hourly_btc_pullback(data,window_start_utc=stamp(START),window_end_utc=stamp(START+timedelta(hours=6)))


class PullbackObservationTests(unittest.TestCase):
    def test_no_pullback_after_six_hours(self):
        x=grade(rows([100,101,103,104,104,105],[99,100,101,102,103,104]))
        self.assertEqual(x["coverage"],"COMPLETE")
        self.assertFalse(x["event_occurred"])
        self.assertEqual(x["severity"],"NONE")

    def test_true_5pct_cross_and_half_recovery(self):
        x=grade(rows([100,99,98,96,97,99],[99,97,94,92,93,96]))
        self.assertTrue(x["event_occurred"])
        self.assertEqual(x["onset_utc"],stamp(START+timedelta(hours=2)))
        self.assertEqual(x["trough_utc"],stamp(START+timedelta(hours=3)))
        self.assertEqual(x["recovery_utc"],stamp(START+timedelta(hours=5)))
        self.assertEqual(x["severity"],"MATERIAL")
        self.assertEqual(x["max_drawdown_pct"],8.0)

    def test_unresolved_event_is_censored(self):
        x=grade(rows([100,99,97,96,95,94],[99,97,95,93,90,89]))
        self.assertTrue(x["event_occurred"])
        self.assertTrue(x["right_censored"])
        self.assertIsNone(x["recovery_utc"])

    def test_missing_hour_fails_closed(self):
        data=rows([100,99,98,96,97,99],[99,97,94,92,93,96])
        data.pop(1)
        x=grade(data)
        self.assertEqual(x["coverage"],"INCOMPLETE")
        self.assertIsNone(x["event_occurred"])

    def test_duplicate_hour_fails_closed(self):
        data=rows([100,99,98,96,97,99],[99,97,94,92,93,96])
        data[1]["hour_start_utc"]=data[0]["hour_start_utc"]
        x=grade(data)
        self.assertEqual(x["coverage"],"INCOMPLETE")

    def test_ambiguous_same_bar_high_low_does_not_trigger_event(self):
        data=rows([100,200,101,101,101,101],[99,95,100,100,100,100])
        x=grade(data)
        # Huge high of bar 1 cannot be assumed to precede low of bar 1.
        self.assertEqual(x["onset_utc"],stamp(START+timedelta(hours=2)))

    def test_recovery_on_trough_bar_is_not_credited(self):
        x=grade(rows([100,99,95,100,94,94],[99,96,90,89,88,87]))
        self.assertTrue(x["right_censored"])
        self.assertIsNone(x["recovery_utc"])

    def test_negative_prices_hard_fail(self):
        data=rows([100,99,98,96,97,99],[99,97,94,92,93,96])
        data[2]["low"]=-5
        with self.assertRaisesRegex(ValueError,"bad_market_ohlc"):
            grade(data)


if __name__ == "__main__":
    unittest.main()
