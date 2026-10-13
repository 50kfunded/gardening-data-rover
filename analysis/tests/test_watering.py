# SPDX-License-Identifier: MIT
"""SIMULATED watering budgets, invented bed limits and forecasts only."""

import copy
import json
import math
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from analysis.engine import analyse
from analysis.garden_runs import load_scenario
from analysis.soil_calibration import Calibration
from analysis.watering import (BedProfile, advise_bed, bucket_step, extraterrestrial_radiation,
                               forecast_rain, hargreaves_et0, learn_limits, load_inputs,
                               weekly_watering_line)
from analysis.weekly_report import weekly_summaries
from simulation.garden import GardenConfig, write_garden


def fake_day(offset, moisture=60, **changes):
    day = {"date": (date(2026, 6, 1) + timedelta(days=offset)).isoformat(),
           "moisture": {"median": moisture}, "temp_c": {"min": 12, "max": 24},
           "coverage": {"soil": 1.0, "temp_c": 1.0}, "usable_for_trends": True,
           "drying_pp_per_hour": 0.8, "flags": [], "confidence": {"score": 0.6}}
    day.update(changes)
    return day


def fake_history():
    # Two distinct wetting cycles, then several clean SIMULATED dry-down days.
    levels = (65, 80, 72, 60, 50, 40, 65, 80, 70, 60, 50, 40, 30, 25)
    return [fake_day(i, value) for i, value in enumerate(levels)]


class SimulatedWaterMathTests(unittest.TestCase):
    def test_bucket_conserves_water_and_drains_excess(self):
        result = bucket_step(18, 20, 10, 4, 3, crop_kc=1.2,
                             rain_efficiency=0.8, irrigation_efficiency=0.75)
        self.assertAlmostEqual(9, result["drainage_mm"])
        self.assertAlmostEqual(16.4, result["storage_mm"])
        self.assertAlmostEqual(18 + 8 + 3, result["storage_mm"] + result["drainage_mm"] + result["et_removed_mm"])

    def test_bucket_cannot_remove_more_water_than_it_contains(self):
        result = bucket_step(1, 20, 0, 0, 10)
        self.assertEqual(0, result["storage_mm"])
        self.assertEqual(1, result["et_removed_mm"])
        self.assertEqual(10, result["et_demand_mm"])

    def test_temperature_equation_units_and_season(self):
        ra = extraterrestrial_radiation("2026-06-21", 52)
        self.assertAlmostEqual(41.74, ra, delta=0.15)
        expected = 0.0023 * (18 + 17.8) * math.sqrt(12) * ra * 0.408
        self.assertAlmostEqual(expected, hargreaves_et0("2026-06-21", 52, 12, 24))
        self.assertGreater(ra, extraterrestrial_radiation("2026-12-21", 52))
        self.assertEqual(0, hargreaves_et0("2026-06-21", 52, 12, 12))

    def test_invalid_inputs_reject_nan_boolean_negative_and_missing(self):
        for value in (float("nan"), float("inf"), True, -1, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bucket_step(10, 20, value, 0, 2)
        for args in (("2026-06-01", 90, 12, 24), ("2026-06-01", 52, 24, 12)):
            with self.assertRaises(ValueError):
                hargreaves_et0(*args)
        with self.assertRaises(ValueError):
            BedProfile("bed_sim", 52, initial_storage_mm=10)

    def test_learned_limits_are_observed_proxies_from_separate_cycles(self):
        history = fake_history()
        wetting = {history[0]["date"], history[6]["date"]}
        result = learn_limits(history, wetting)
        self.assertTrue(result["ready"])
        self.assertEqual(80, result["wet_index"])
        self.assertEqual(30, result["dry_index"])
        self.assertIn("not FC", result["basis"])
        self.assertFalse(learn_limits(history, {history[0]["date"]})["ready"])
        self.assertFalse(learn_limits([fake_day(i, 60) for i in range(14)], wetting)["ready"])

    def test_bad_days_and_rapid_drainage_cannot_teach_limits(self):
        history = fake_history()
        wetting = {history[0]["date"], history[6]["date"]}
        for flags in (["possible_stuck"], ["drift"], ["noisy"]):
            bad = copy.deepcopy(history)
            bad[1]["flags"] = flags
            self.assertFalse(learn_limits(bad, wetting)["ready"])
        history[1]["drying_pp_per_hour"] = 5
        self.assertFalse(learn_limits(history, wetting)["ready"])


class SimulatedWaterDecisionTests(unittest.TestCase):
    def setUp(self):
        self.days = fake_history() + [fake_day(14, 50)]
        self.water = {day["date"]: {"rain_mm": 0, "irrigation_mm": 0} for day in self.days}
        for i in (0, 6):
            self.water[self.days[i]["date"]]["irrigation_mm"] = 3
        # An invented capacity large enough to give a moderate end depletion.
        self.profile = BedProfile("bed_sim", 52, capacity_mm=140, initial_storage_mm=140)

    def test_warmup_and_no_future_leakage(self):
        full = advise_bed(self.days, self.profile, self.water)
        prefix = advise_bed(self.days[:10], self.profile, self.water)
        self.assertEqual(prefix["days"], full["days"][:10])
        self.assertTrue(all(day["action"] == "check_by_finger" for day in full["days"][:7]))
        json.dumps(full, allow_nan=False)

    def test_consider_watering_requires_sensor_and_budget_agreement(self):
        result = advise_bed(self.days, self.profile, self.water)["days"][-1]
        self.assertEqual("consider_watering", result["action"])
        self.assertTrue(result["enough_data"])
        self.assertLessEqual(result["confidence"]["score"], 0.65)
        self.assertIn("Check by finger", result["fallback"])
        wet = self.days[:-1] + [fake_day(14, 80)]
        disagreement = advise_bed(wet, self.profile, self.water)["days"][-1]
        self.assertEqual("check_by_finger", disagreement["action"])
        self.assertIn("disagree", " ".join(disagreement["reasons"]))

    def test_forecast_changes_suggestion_but_never_enters_bucket(self):
        dry = advise_bed(self.days, self.profile, self.water)["days"][-1]
        day = self.days[-1]["date"]
        self.water[day]["forecast"] = {"issued_at_utc": day + "T18:00:00+00:00",
                                       "for_date": "2026-06-16", "rain_mm": 5, "probability": 0.8}
        rainy = advise_bed(self.days, self.profile, self.water)["days"][-1]
        self.assertEqual("watch_forecast", rainy["action"])
        self.assertEqual(dry["bucket"], rainy["bucket"])
        self.water[day]["forecast"]["issued_at_utc"] = "2026-06-20T00:00:00+00:00"
        ignored = advise_bed(self.days, self.profile, self.water)["days"][-1]
        self.assertEqual("consider_watering", ignored["action"])

    def test_hold_and_check_when_consistent_estimates_are_still_wet(self):
        self.days[-1]["moisture"]["median"] = 70
        profile = BedProfile("bed_sim", 52, capacity_mm=280, initial_storage_mm=280)
        result = advise_bed(self.days, profile, self.water)["days"][-1]
        self.assertEqual("hold_and_check", result["action"])
        self.assertTrue(result["enough_data"])

    def test_forecast_does_not_delay_severely_depleted_bed(self):
        # First use a consistent severe sensor value, then independently depleted capacity.
        self.days[-1]["moisture"]["median"] = 30
        self.water[self.days[-1]["date"]]["forecast"] = {
            "issued_at_utc": "2026-06-15T18:00:00+00:00", "for_date": "2026-06-16",
            "rain_mm": 20, "probability": 0.9}
        profile = BedProfile("bed_sim", 52, capacity_mm=60, initial_storage_mm=60)
        result = advise_bed(self.days, profile, self.water)["days"][-1]
        self.assertEqual("consider_watering", result["action"])

    def test_missing_rain_breaks_budget_and_is_not_assumed_zero(self):
        self.water[self.days[5]["date"]]["rain_mm"] = None
        result = advise_bed(self.days, self.profile, self.water)
        self.assertTrue(all(day["bucket"] is None for day in result["days"][5:]))
        self.assertEqual("check_by_finger", result["days"][-1]["action"])

    def test_faults_low_coverage_unknown_capacity_and_low_confidence_fall_back(self):
        for flags in (["possible_stuck"], ["noisy"], ["drift"]):
            days = copy.deepcopy(self.days)
            days[-1]["flags"] = flags
            self.assertEqual("check_by_finger", advise_bed(days, self.profile, self.water)["days"][-1]["action"])
        days = copy.deepcopy(self.days)
        days[-1]["coverage"]["soil"] = 0.5
        self.assertEqual("check_by_finger", advise_bed(days, self.profile, self.water)["days"][-1]["action"])
        days[-1]["coverage"]["soil"] = 1
        days[-1]["confidence"]["score"] = 0.2
        self.assertEqual("check_by_finger", advise_bed(days, self.profile, self.water)["days"][-1]["action"])
        self.assertEqual("check_by_finger", advise_bed(self.days, BedProfile("bed_sim", 52), self.water)["days"][-1]["action"])

    def test_beds_keep_independent_histories_and_dates_must_be_ordered(self):
        other = advise_bed([fake_day(i, 60) for i in range(15)], BedProfile("other_sim", 52, 140, 140), self.water)
        self.assertFalse(any(day["limits"]["ready"] for day in other["days"]))
        self.assertEqual("other_sim", other["bed_id"])
        with self.assertRaises(ValueError):
            advise_bed(self.days[::-1], self.profile, self.water)

    def test_weekly_line_counts_suggestions_and_missing_evidence(self):
        advice = advise_bed(self.days, self.profile, self.water)
        line = weekly_watering_line(advice, self.days[0]["date"], self.days[6]["date"])
        self.assertIn("not enough data", line)
        advice["days"] = [dict(advice["days"][-1], date=fake_day(i)["date"]) for i in range(7)]
        self.assertIn("consider watering on 7", weekly_watering_line(advice, "2026-06-01", "2026-06-07"))

    def test_forecast_rejects_stale_wrong_day_missing_timezone_and_bad_probability(self):
        good = {"issued_at_utc": "2026-06-15T18:00:00+00:00", "for_date": "2026-06-16",
                "rain_mm": 5, "probability": 0.8}
        self.assertIsNotNone(forecast_rain(good, "2026-06-15"))
        for key, value in (("issued_at_utc", "2026-06-01T00:00:00+00:00"),
                           ("issued_at_utc", "2026-06-15T18:00:00"),
                           ("for_date", "2026-06-17"), ("probability", 80)):
            self.assertIsNone(forecast_rain(dict(good, **{key: value}), "2026-06-15"))

    def test_six_week_files_integrate_without_new_contract_or_truth_label_inputs(self):
        with tempfile.TemporaryDirectory(prefix="rover-water-sim-") as tmp:
            root = write_garden(Path(tmp) / "garden_sim", GardenConfig())
            schedule, observations, boundaries = load_scenario(root)
            inputs = load_inputs(root / "watering_inputs.json", schedule)
            result = analyse(observations, schedule, Calibration(3000, 1000), boundaries=boundaries, watering_inputs=inputs)
            self.assertEqual(42, len(result["watering"]["days"]))
            self.assertEqual(6, len(weekly_summaries(result)))
            self.assertTrue(all("Watering advisor" in report for report in weekly_summaries(result)))
            obj = json.loads((root / "scenario.json").read_text())
            self.assertTrue(any("irrigation_event" in event["labels"] for event in obj["injected_events"]))
            obj["injected_events"] = []
            (root / "scenario.json").write_text(json.dumps(obj))
            _, observations2, boundaries2 = load_scenario(root)
            self.assertEqual(result, analyse(observations2, schedule, Calibration(3000, 1000),
                                           boundaries=boundaries2, watering_inputs=inputs))
            bad = json.loads((root / "watering_inputs.json").read_text())
            bad["data_source"] = "observation"
            (root / "watering_inputs.json").write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                load_inputs(root / "watering_inputs.json", schedule)
