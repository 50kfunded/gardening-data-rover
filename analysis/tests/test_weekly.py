# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: weekly rules, file boundaries and invented faults."""

import copy
import csv
import json
import math
import tempfile
import unittest
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analysis.engine import Thresholds, analyse
from analysis.garden_runs import Observation, Schedule, load_scenario, observations_from_run
from analysis.read_run import read_run
from analysis.soil_calibration import Calibration, check_drift
from analysis.weekly_report import weekly_summaries
from shared.data_format import COLUMNS, SCHEMA_VERSION, SIMULATION_NOTICE, parse_telemetry
from simulation.garden import BATCH_SAMPLES, GardenConfig, garden_batches, write_garden

START = datetime(2026, 1, 5, tzinfo=timezone.utc)  # Fictional, not a real garden visit.
CALIBRATION = Calibration(3000, 1000)  # Invented fixture references, never hardware defaults.


def invented_observations(days, base=70, rate=1.2):
    observations = []
    for day in range(days):
        level = base(day) if callable(base) else base
        speed = rate(day) if callable(rate) else rate
        for hour in range(24):
            moisture = level - speed * min(12, max(0, hour - 6))
            raw = round(3000 - 20 * moisture)
            for sample in range(9):
                t_ms = hour * 3_600_000 + (sample + 1) * 100
                at = START + timedelta(days=day, milliseconds=t_ms)
                row = parse_telemetry(f"T,{t_ms},0,0,0,0,0,0,0,{raw},{18+day/10:.2f},{60+day/10:.2f}\n")
                observations.append(Observation(at, row, f"day{day}_sim"))
    return observations, Schedule(START, START + timedelta(days=days))


class SimulatedGardenFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="rover-weekly-sim-")
        cls.root = write_garden(Path(cls.temporary.name) / "garden_sim")
        cls.schedule, cls.observations, cls.boundaries = load_scenario(cls.root)
        cls.result = analyse(cls.observations, cls.schedule, CALIBRATION, boundaries=cls.boundaries)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_long_fixture_keeps_columns_versions_and_source_notices(self):
        manifest = json.loads((self.root / "scenario.json").read_text())
        self.assertEqual(42, len(self.result["days"]))
        for entry in manifest["runs"]:
            folder = self.root / entry["run_id"]
            metadata, rows = read_run(folder)
            self.assertEqual(2, metadata["schema_version"])
            self.assertEqual(SCHEMA_VERSION, metadata["schema_version"])
            self.assertEqual(2, metadata["csv_format_version"])
            self.assertEqual("simulation", metadata["data_source"])
            self.assertEqual("untested", metadata["hardware_status"])
            self.assertEqual("controller_boot_ms", metadata["timebase"])
            with (folder / "telemetry.csv").open(newline="") as source:
                self.assertEqual(SIMULATION_NOTICE, source.readline().strip())
                self.assertEqual(list(COLUMNS), next(csv.reader(source)))
            self.assertFalse(list((folder / "photos").iterdir()))
            self.assertTrue(all(before["t_ms"] < after["t_ms"] for before, after in zip(rows, rows[1:])))
            self.assertTrue(all(row["soil_raw"] is None or 0 <= row["soil_raw"] <= 4095 for row in rows))
            # meta.json retains generation time; the fictional clock is a separate artifact.
            self.assertNotEqual(metadata["date"], entry["first_observation_utc"])

    def test_every_requested_injection_exists_without_new_telemetry_fields(self):
        manifest = json.loads((self.root / "scenario.json").read_text())
        labels = {label for event in manifest["injected_events"] for label in event["labels"]}
        self.assertTrue({"rain_event", "slow_sensor_drift", "stuck_sensor", "noisy_sensor",
                         "spike", "soil_dropout", "telemetry_gap", "controller_reboot"} <= labels)
        self.assertTrue(any(item.row["soil_raw"] is None for item in self.observations))
        self.assertEqual(1, len(self.boundaries))

    def test_end_to_end_fixture_triggers_all_rules_and_reports(self):
        codes = Counter(item["code"] for item in self.result["alerts"])
        self.assertTrue({"dried_out_faster", "unusually_wet", "moisture_shift", "sensor_stuck",
                         "sensor_noisy", "data_gap", "controller_boundary"} <= codes.keys())
        reports = weekly_summaries(self.result)
        self.assertEqual(6, len(reports))
        for report in reports:
            self.assertIn("SIMULATED DATA ONLY", report)
            self.assertIn("untested on hardware", report)
            self.assertIn("What changed", report)
            self.assertIn("What to check", report)
            self.assertIn("No hardware milestone has passed", report)
        json.dumps(self.result, allow_nan=False)

    def test_ground_truth_injections_are_not_used_by_analysis(self):
        with tempfile.TemporaryDirectory(prefix="rover-truth-sim-") as temporary:
            root = write_garden(Path(temporary) / "scenario")
            manifest = json.loads((root / "scenario.json").read_text())
            manifest["injected_events"] = [{"made_up_label": "everything is fine"}]
            (root / "scenario.json").write_text(json.dumps(manifest))
            schedule, observations, boundaries = load_scenario(root)
            self.assertEqual(self.result, analyse(observations, schedule, CALIBRATION, boundaries=boundaries))

    def test_stuck_is_only_suspected_and_cannot_enter_environment_baselines(self):
        for index in (24, 25):
            day = self.result["days"][index]
            self.assertFalse(day["usable_for_trends"])
            self.assertIsNone(day["drying_pp_per_hour"])
            warning = next(item for item in self.result["alerts"] if item["date"] == day["date"] and item["code"] == "sensor_stuck")
            self.assertEqual("low", warning["confidence"]["level"])
            self.assertFalse(warning["enough_data"])
            self.assertIn("stable soil", warning["limitation"])
            self.assertIn("controlled dry/wet challenge", warning["message"])

    def test_noisy_day_withholds_soil_but_keeps_environmental_readings(self):
        day = self.result["days"][26]
        self.assertEqual(24, day["noisy_visits"])
        self.assertIsNone(day["moisture"]["median"])
        self.assertIsNone(day["drying_pp_per_hour"])
        self.assertEqual(24, day["temp_c"]["count"])
        self.assertEqual(24, day["humidity_pct"]["count"])
        self.assertFalse(day["usable_for_trends"])
        bad = [item["code"] for item in self.result["alerts"] if item["date"] == day["date"]]
        self.assertNotIn("dried_out_faster", bad)
        self.assertNotIn("unusually_wet", bad)

    def test_isolated_spikes_are_rejected_without_biasing_daily_median(self):
        day = self.result["days"][27]
        self.assertEqual(24, day["rejected_soil_samples"])
        self.assertIn("outliers_rejected", day["flags"])
        self.assertEqual(0, day["noisy_visits"])
        self.assertAlmostEqual(60.7, day["moisture"]["median"], delta=0.2)

    def test_dropouts_and_whole_missing_day_stay_missing(self):
        dropout = self.result["days"][29]
        self.assertAlmostEqual(16/24, dropout["coverage"]["soil"])
        self.assertFalse(dropout["usable_for_trends"])
        self.assertEqual(8, dropout["incomplete_visits"])
        missing = self.result["days"][31]
        self.assertEqual(0, missing["observed_visits"])
        self.assertIsNone(missing["moisture"]["mean"])
        self.assertIsNone(missing["temp_c"]["mean"])
        self.assertIsNone(missing["humidity_pct"]["mean"])
        self.assertIsNone(missing["ewma_moisture_pct"])
        warning = next(item for item in self.result["alerts"] if item["date"] == missing["date"])
        self.assertFalse(warning["enough_data"])
        self.assertIn("Not enough data", warning["limitation"])

    def test_reboot_split_preserves_utc_and_excludes_boundary_drying_pair(self):
        day = self.result["days"][32]
        self.assertEqual(24, day["observed_visits"])
        self.assertEqual(11, day["drying_pairs"])
        self.assertAlmostEqual(1.2, day["drying_pp_per_hour"], delta=0.1)
        self.assertEqual(START + timedelta(days=32, hours=12, milliseconds=100), self.boundaries[0].at)

    def test_writer_never_overwrites_and_seed_reproduces_numeric_data(self):
        with self.assertRaises(FileExistsError):
            write_garden(self.root)
        config = GardenConfig(weeks=1)
        self.assertEqual(list(garden_batches(config)), list(garden_batches(config)))
        self.assertNotEqual(list(garden_batches(config)), list(garden_batches(replace(config, seed=43))))

    def test_manifest_path_escape_duplicate_and_false_source_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="rover-bad-scenario-") as temporary:
            root = write_garden(Path(temporary) / "scenario", GardenConfig(weeks=1))
            path = root / "scenario.json"
            original = json.loads(path.read_text())
            for change in ("escape", "duplicate", "hardware", "anchor", "label"):
                broken = copy.deepcopy(original)
                if change == "escape":
                    broken["runs"][0]["run_id"] = "../escape_sim"
                elif change == "duplicate":
                    broken["runs"].append(broken["runs"][0])
                elif change == "hardware":
                    broken["data_source"] = "hardware"
                elif change == "anchor":
                    broken["runs"][0]["controller_first_ms"] = 123
                else:
                    broken["notice"] = "ordinary data"
                path.write_text(json.dumps(broken))
                with self.subTest(change=change), self.assertRaises(ValueError):
                    load_scenario(root)

    def test_unsplit_reset_and_unlabelled_csv_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="rover-bad-run-") as temporary:
            root = write_garden(Path(temporary) / "scenario", GardenConfig(weeks=1))
            entry = json.loads((root / "scenario.json").read_text())["runs"][0]
            folder = root / entry["run_id"]
            path = folder / "telemetry.csv"
            original = path.read_text()
            lines = original.splitlines()
            cells = lines[-1].split(",")
            cells[0] = "0"
            lines[-1] = ",".join(cells)
            path.write_text("\n".join(lines) + "\n")
            with self.assertRaisesRegex(ValueError, "unsplit"):
                load_scenario(root)
            path.write_text("\n".join(original.splitlines()[1:]) + "\n")
            with self.assertRaisesRegex(ValueError, "notice"):
                load_scenario(root)

    def test_existing_committed_run_uses_existing_anchor_without_new_metadata(self):
        folder = Path(__file__).resolve().parents[2] / "data/sample/example_sim"
        metadata, rows = read_run(folder)
        observations, boundary = observations_from_run(folder)
        self.assertEqual(300, len(observations))
        self.assertIsNone(boundary)
        expected = datetime.fromtimestamp(metadata["started_unix_s"], timezone.utc) + timedelta(milliseconds=rows[0]["t_ms"])
        self.assertEqual(expected, observations[0].at)

    def test_simulated_boot_clock_rollover_is_split_without_losing_dates(self):
        with tempfile.TemporaryDirectory(prefix="rover-rollover-sim-") as temporary:
            root = write_garden(Path(temporary) / "scenario", GardenConfig(weeks=8, faults=False))
            schedule, observations, boundaries = load_scenario(root)
            self.assertEqual(56*24*9, len(observations))
            self.assertEqual(1, len(boundaries))
            self.assertTrue(all(schedule.start <= item.at < schedule.end for item in observations))
            self.assertEqual(START+timedelta(days=55, hours=23, milliseconds=900), observations[-1].at)


class SimulatedWeeklyMathTests(unittest.TestCase):
    def test_clean_cycles_dont_trigger_condition_or_fault_alerts(self):
        observations, schedule = invented_observations(28)
        result = analyse(observations, schedule, CALIBRATION)
        self.assertFalse(result["alerts"])
        for day in result["days"]:
            self.assertAlmostEqual(1.2, day["drying_pp_per_hour"], places=8)
            self.assertEqual(1, day["coverage"]["soil"])
            self.assertEqual("relative_index", day["moisture_basis"])

    def test_baselines_use_only_earlier_days_and_warm_up_honestly(self):
        observations, schedule = invented_observations(21, base=lambda day: 90 if day >= 14 else 70)
        result = analyse(observations, schedule, CALIBRATION)
        shorter = analyse(observations[:14*24*9], replace(schedule, end=START+timedelta(days=14)), CALIBRATION)
        self.assertEqual(shorter["days"], result["days"][:14])
        self.assertIsNone(result["days"][0]["baseline"]["moisture"])
        self.assertTrue(all("Not enough baseline" in " ".join(day["notes"]) for day in result["days"][:7]))
        self.assertTrue(any(item["code"] == "unusually_wet" for item in result["alerts"]))

    def test_ewma_formula_and_cusum_shift_in_both_directions(self):
        for shift, direction in ((20, "up"), (-20, "down")):
            observations, schedule = invented_observations(21, base=lambda day: 70 + (shift if day >= 14 else 0))
            result = analyse(observations, schedule, CALIBRATION)
            before, after = result["days"][13:15]
            self.assertAlmostEqual(0.3*after["moisture"]["median"] + 0.7*before["ewma_moisture_pct"], after["ewma_moisture_pct"])
            shifts = [item for item in result["alerts"] if item["code"] == "moisture_shift"]
            self.assertTrue(shifts)
            self.assertIn(f"shift {direction}", shifts[0]["message"])
            self.assertGreaterEqual(shifts[0]["date"], result["days"][15]["date"])

    def test_drying_rate_shift_is_a_slope_not_a_low_level_threshold(self):
        observations, schedule = invented_observations(21, rate=lambda day: 3.2 if day >= 14 else 1.2)
        result = analyse(observations, schedule, CALIBRATION)
        self.assertEqual(7, sum(item["code"] == "dried_out_faster" for item in result["alerts"]))
        self.assertAlmostEqual(3.2, result["days"][14]["drying_pp_per_hour"])

    def test_slow_drift_is_not_mislabelled_as_a_proven_sensor_fault(self):
        observations, schedule = invented_observations(42, base=lambda day: 70-day)
        result = analyse(observations, schedule, CALIBRATION)
        self.assertTrue(all("drift_unchecked" in day["flags"] for day in result["days"]))
        shifts = [item for item in result["alerts"] if item["code"] == "moisture_shift"]
        self.assertTrue(shifts)
        self.assertTrue(all("sensor drift" in item["limitation"] for item in shifts))
        self.assertFalse(any(item["code"] == "sensor_drift" for item in result["alerts"]))

    def test_explicit_repeat_references_use_existing_drift_check(self):
        observations, schedule = invented_observations(7)
        normal = analyse(observations, schedule, CALIBRATION)
        reference = check_drift(CALIBRATION, dry_samples=[3100]*9, wet_samples=[1100]*9)
        shifted = analyse(observations, schedule, CALIBRATION, reference=reference)
        self.assertIn("drift", shifted["days"][0]["flags"])
        self.assertLess(shifted["days"][0]["confidence"]["score"], normal["days"][0]["confidence"]["score"])

    def test_partial_batch_creates_gap_and_reduces_confidence(self):
        observations, schedule = invented_observations(7)
        normal = analyse(observations, schedule, CALIBRATION)
        partial = analyse(observations[1:], schedule, CALIBRATION)
        self.assertEqual(1, partial["days"][0]["incomplete_visits"])
        self.assertTrue(any(item["code"] == "data_gap" for item in partial["alerts"]))
        self.assertLess(partial["days"][0]["confidence"]["score"], normal["days"][0]["confidence"]["score"])

    def test_adc_rails_are_not_reported_as_real_zero_or_full_moisture(self):
        observations, schedule = invented_observations(7)
        for raw in (0, 4095):
            broken = [replace(item, row={**item.row, "soil_raw": raw}) for item in observations]
            result = analyse(broken, schedule, CALIBRATION)
            self.assertTrue(all(day["moisture"]["mean"] is None for day in result["days"]))
            self.assertTrue(all("adc_rail" in day["flags"] for day in result["days"]))

    def test_missing_environmental_fields_dont_become_zero_or_hide_incomplete_batches(self):
        observations, schedule = invented_observations(7)
        missing = [replace(item, row={**item.row, "temp_c": None, "humidity_pct": None}) for item in observations]
        result = analyse(missing, schedule, CALIBRATION)
        for day in result["days"]:
            self.assertIsNone(day["temp_c"]["mean"])
            self.assertIsNone(day["humidity_pct"]["mean"])
            self.assertIsNotNone(day["moisture"]["mean"])
            self.assertEqual(24, day["incomplete_visits"])

    def test_bad_reference_withholds_condition_alerts(self):
        observations, schedule = invented_observations(21, base=lambda day: 90 if day >= 14 else 70)
        reference = check_drift(CALIBRATION, dry_samples=[0]*9, wet_samples=[1000]*9)
        result = analyse(observations, schedule, CALIBRATION, reference=reference)
        self.assertTrue(all(not day["usable_for_trends"] for day in result["days"]))
        self.assertFalse(any(item["code"] in {"unusually_wet", "dried_out_faster", "moisture_shift"} for item in result["alerts"]))

    def test_drying_trigger_boundary_and_shift_evidence_are_auditable(self):
        observations, schedule = invented_observations(21, rate=lambda day: 1.7 if day >= 14 else 1.2)
        result = analyse(observations, schedule, CALIBRATION)
        self.assertFalse(any(item["code"] == "dried_out_faster" for item in result["alerts"]))
        observations, schedule = invented_observations(21, base=lambda day: 90 if day >= 14 else 70)
        result = analyse(observations, schedule, CALIBRATION)
        alarms = [day for day in result["days"] if day["cusum"]["reset_after_alert"]]
        self.assertTrue(alarms)
        self.assertTrue(all(max(day["cusum"]["up"], day["cusum"]["down"]) >= 20 for day in alarms))

    def test_smoothing_restarts_after_missing_day_and_weekly_flat_text_is_plain(self):
        observations, schedule = invented_observations(21)
        observations = [item for item in observations if item.at.date() != (START+timedelta(days=10)).date()]
        result = analyse(observations, schedule, CALIBRATION)
        self.assertIsNone(result["days"][10]["ewma_moisture_pct"])
        self.assertEqual(result["days"][11]["moisture"]["median"], result["days"][11]["ewma_moisture_pct"])
        observations, schedule = invented_observations(14)
        report = weekly_summaries(analyse(observations, schedule, CALIBRATION))[1]
        self.assertIn("about the same as last week", report)

    def test_no_data_and_partial_week_reports_admit_insufficient_data(self):
        schedule = Schedule(START, START + timedelta(days=10))
        result = analyse([], schedule, CALIBRATION)
        self.assertEqual(10, len(result["days"]))
        self.assertTrue(all(day["moisture"]["median"] is None for day in result["days"]))
        self.assertTrue(all(not item["enough_data"] for item in result["alerts"]))
        reports = weekly_summaries(result)
        self.assertEqual(2, len(reports))
        self.assertTrue(all("not enough data" in report.lower() for report in reports))
        observations, schedule = invented_observations(10)
        report = weekly_summaries(analyse(observations, schedule, CALIBRATION))[-1]
        self.assertIn("3/5 usable days needed", report)

    def test_all_alerts_have_confidence_limitations_and_source_labels(self):
        observations, schedule = invented_observations(21, base=lambda day: 95 if day >= 14 else 70)
        result = analyse(observations, schedule, CALIBRATION)
        for item in result["alerts"]:
            self.assertTrue(item["limitation"])
            self.assertIsInstance(item["enough_data"], bool)
            self.assertTrue(0 <= item["confidence"]["score"] <= 1)
            self.assertIn(item["confidence"]["level"], ("low", "medium", "high"))
            self.assertEqual("simulation", item["data_source"])
            self.assertEqual("planned_hardware_untested", item["status"])

    def test_weekly_templates_compare_temperature_humidity_and_moisture(self):
        observations, schedule = invented_observations(14, base=lambda day: 70+day/2)
        reports = weekly_summaries(analyse(observations, schedule, CALIBRATION))
        self.assertIn("not enough data from last week", reports[0])
        self.assertIn("higher than last week", reports[1])
        self.assertIn("Temperature", reports[1])
        self.assertIn("Humidity", reports[1])
        self.assertIn("Humidity: 60.3 % RH", reports[0])
        self.assertIn("0.7 percentage points higher than last week", reports[1])
        self.assertIn("Drying trend", reports[1])

    def test_duplicates_overlaps_wrong_window_and_long_batches_are_rejected(self):
        observations, schedule = invented_observations(7)
        bad_inputs = [observations + [observations[0]],
                      [replace(observations[0], at=START-timedelta(seconds=1))] + observations[1:],
                      [replace(observations[0], run_id="other_sim")] + observations[1:],
                      [replace(observations[0], at=START+timedelta(seconds=30))] + observations[1:]]
        for bad in bad_inputs:
            with self.assertRaises(ValueError):
                analyse(bad, schedule, CALIBRATION)

    def test_short_interval_between_slot_boundaries_is_not_a_drying_pair(self):
        observations, schedule = invented_observations(7)
        changed = []
        for item in observations:
            # Move the 06:00 visit to 06:59 without changing its within-burst spacing.
            at = item.at + timedelta(minutes=59) if item.at.hour == 6 else item.at
            changed.append(replace(item, at=at))
        result = analyse(changed, schedule, CALIBRATION)
        self.assertTrue(all(day["drying_pairs"] == 11 for day in result["days"]))

    def test_bad_settings_fail_instead_of_making_confident_output(self):
        for settings in ({"weeks": 0}, {"weeks": True}, {"drift_counts_per_day": math.inf}, {"seed": True}):
            with self.assertRaises(ValueError):
                GardenConfig(**settings)
        for settings in ({"ewma_alpha": 0}, {"min_day_coverage": 2}, {"baseline_days": True},
                         {"min_baseline_days": 20}, {"cusum_threshold_pp": math.nan}):
            with self.assertRaises(ValueError):
                Thresholds(**settings)
        for start, end, interval in ((START.replace(tzinfo=None), START+timedelta(days=7), 3600),
                                     (START, START, 3600), (START, START+timedelta(days=7), 77)):
            with self.assertRaises(ValueError):
                Schedule(start, end, interval)


if __name__ == "__main__":
    unittest.main()
