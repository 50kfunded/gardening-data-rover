# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: inject faults into the committed invented soil readings."""

import math
import random
import unittest
from pathlib import Path

from analysis.read_run import read_run
from analysis.soil_calibration import Calibration, calibrate, check_drift, gravimetric_water_pct
from analysis.soil_quality import Limits


class SimulatedSoilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = Path(__file__).resolve().parents[2] / "data" / "sample" / "example_sim"
        metadata, rows = read_run(folder)
        if metadata["data_source"] != "simulation":
            raise ValueError("soil tests must only use SIMULATED DATA")
        cls.raw = [row["soil_raw"] for row in rows]
        # These endpoints are invented. They are not values to flash onto a board.
        cls.calibration = Calibration(dry_raw=3000, wet_raw=1000)

    def test_all_committed_simulated_windows_keep_the_relative_index_label(self):
        for start in range(0, len(self.raw), 9):
            batch = self.raw[start:start + 9]
            if len(batch) < 5:
                continue
            reading = calibrate(batch, self.calibration)
            self.assertEqual("relative_index", reading.basis)
            self.assertEqual("planned_hardware_untested", reading.status)
            self.assertIsNotNone(reading.moisture_pct)
            self.assertTrue(0 <= reading.moisture_pct <= 100)
            self.assertIn("drift_unchecked", reading.flags)

    def test_two_point_mapping_handles_both_sensor_directions(self):
        for calibration in (self.calibration, Calibration(1000, 3000)):
            for raw, expected in ((calibration.dry_raw, 0),
                                  ((calibration.dry_raw + calibration.wet_raw) / 2, 50),
                                  (calibration.wet_raw, 100)):
                self.assertEqual(expected, calibrate([raw] * 9, calibration).moisture_pct)

    def test_values_beyond_calibration_are_clamped_and_flagged(self):
        for raw, expected in ((3500, 0), (500, 100)):
            reading = calibrate([raw] * 9, self.calibration)
            self.assertEqual(expected, reading.moisture_pct)
            self.assertIn("outside_calibration", reading.flags)
            self.assertLess(reading.confidence, 0.8)

    def test_simulated_noise_and_spikes_do_not_move_the_result_far(self):
        batch = self.raw[:31]
        baseline = calibrate(batch, self.calibration)
        rng = random.Random(42)
        noisy = [value + rng.gauss(0, 3) for value in batch]
        noisy[0], noisy[7], noisy[20] = 100, 3900, 3800
        reading = calibrate(noisy, self.calibration)
        self.assertIn("outliers_rejected", reading.flags)
        self.assertGreaterEqual(reading.samples_rejected, 3)
        self.assertAlmostEqual(baseline.moisture_pct, reading.moisture_pct, delta=1.0)
        self.assertLess(reading.confidence, baseline.confidence)

    def test_zero_mad_still_rejects_an_isolated_spike(self):
        reading = calibrate([self.raw[0]] * 8 + [3900], self.calibration)
        self.assertEqual(8, reading.samples_used)
        self.assertEqual(1, reading.samples_rejected)
        self.assertIn("outliers_rejected", reading.flags)

    def test_noisy_batch_is_flagged_before_filtering(self):
        batch = [self.raw[0] + step for step in (-160, -120, -80, -40, 0, 40, 80, 120, 160)]
        reading = calibrate(batch, self.calibration)
        self.assertIn("noisy", reading.flags)
        self.assertLess(reading.confidence, 0.1)

    def test_many_spikes_cannot_be_filtered_into_a_high_confidence_reading(self):
        reading = calibrate([self.raw[0]] * 6 + [3900] * 3, self.calibration)
        self.assertIn("noisy", reading.flags)
        self.assertIn("outliers_rejected", reading.flags)
        self.assertLess(reading.confidence, 0.2)

    def test_controlled_references_detect_simulated_drift_in_both_directions(self):
        for shift in (-100, 100):
            reference = check_drift(self.calibration, dry_samples=[3000 + shift] * 9,
                                    wet_samples=[1000 + shift] * 9)
            self.assertEqual(shift, reference.dry_shift_counts)
            self.assertEqual(shift, reference.wet_shift_counts)
            self.assertIn("drift", reference.flags)
            reading = calibrate(self.raw[:9], self.calibration, reference=reference)
            self.assertIn("drift", reading.flags)
            self.assertLess(reading.confidence, 0.5)

    def test_changing_simulated_soil_is_not_called_drift(self):
        reference = check_drift(self.calibration, dry_samples=[3000] * 9,
                                wet_samples=[1000] * 9)
        dry = calibrate(self.raw[:9], self.calibration, reference=reference)
        wet = calibrate([value - 300 for value in self.raw[:9]], self.calibration,
                        reference=reference)
        self.assertGreater(wet.moisture_pct, dry.moisture_pct)
        self.assertNotIn("drift", wet.flags)

    def test_faulty_or_missing_reference_cannot_claim_drift_is_checked(self):
        incomplete = check_drift(self.calibration, dry_samples=[3000] * 9)
        self.assertIn("reference_incomplete", incomplete.flags)
        faulty = check_drift(self.calibration, dry_samples=[0] * 9, wet_samples=[1000] * 9)
        self.assertIn("reference_unreliable", faulty.flags)
        self.assertIsNone(faulty.dry_shift_counts)
        self.assertEqual(0, calibrate(self.raw[:9], self.calibration,
                                     reference=faulty).confidence)

    def test_unchanging_soil_is_not_automatically_called_stuck(self):
        reading = calibrate([self.raw[0]] * 30, self.calibration)
        self.assertNotIn("stuck", reading.flags)
        self.assertIsNotNone(reading.moisture_pct)

    def test_stuck_fault_needs_a_deliberate_change_challenge(self):
        reading = calibrate(self.raw[:9], self.calibration,
                            challenge_history=[self.raw[0]] * 30)
        self.assertIn("stuck", reading.flags)
        self.assertIsNone(reading.moisture_pct)
        self.assertEqual(0, reading.confidence)
        responsive = calibrate(self.raw[:9], self.calibration,
                               challenge_history=[3000] * 15 + [1000] * 15)
        self.assertNotIn("stuck", responsive.flags)

    def test_incomplete_or_invalid_challenge_is_reported(self):
        for history, flag in (([1800] * 3, "challenge_incomplete"),
                              ([None] * 30, "challenge_unreliable")):
            reading = calibrate(self.raw[:9], self.calibration, challenge_history=history)
            self.assertIn(flag, reading.flags)
            self.assertNotIn("stuck", reading.flags)

    def test_out_of_range_codes_are_not_disguised_by_clamping(self):
        for value in (-1, 4096):
            reading = calibrate(self.raw[:8] + [value], self.calibration)
            self.assertIn("out_of_range", reading.flags)
            self.assertEqual(1, reading.samples_rejected)
            self.assertIsNone(reading.moisture_pct)
            self.assertEqual(0, reading.confidence)

    def test_missing_data_stays_missing_but_a_partial_batch_can_be_used(self):
        for batch in ([], [None] * 9, self.raw[:4]):
            reading = calibrate(batch, self.calibration)
            self.assertIsNone(reading.moisture_pct)
            self.assertEqual(0, reading.confidence)
        reading = calibrate(self.raw[:8] + [None], self.calibration)
        self.assertIn("missing_reading", reading.flags)
        self.assertEqual(1, reading.samples_rejected)
        self.assertIsNotNone(reading.moisture_pct)

    def test_non_numeric_non_finite_and_boolean_inputs_are_faults(self):
        for value in ("1800", True, math.nan, math.inf, -math.inf, 10 ** 1000):
            reading = calibrate(self.raw[:8] + [value], self.calibration)
            self.assertIn("invalid_reading", reading.flags)
            self.assertIsNone(reading.moisture_pct)
            self.assertEqual(0, reading.confidence)

    def test_adc_rails_are_suspect_even_when_they_are_legal_codes(self):
        for value in (0, 4095):
            reading = calibrate([value] * 9, self.calibration)
            self.assertIn("adc_rail", reading.flags)
            self.assertIsNone(reading.moisture_pct)

    def test_invalid_calibration_and_thresholds_fail_early(self):
        for endpoints in ((1800, 1800), (math.nan, 1000), (3000, 4096), (True, 1000)):
            with self.assertRaises(ValueError):
                Calibration(*endpoints)
        for settings in ({"min_samples": 0}, {"min_samples": 1.5}, {"stuck_samples": True},
                         {"noisy_mad_counts": 0}, {"drift_counts": math.inf},
                         {"max_outlier_fraction": 1}, {"stuck_span_counts": -1}):
            with self.assertRaises(ValueError):
                Limits(**settings)

    def test_a_tiny_calibration_span_is_flagged_as_weak(self):
        reading = calibrate([1810] * 9, Calibration(1800, 1820))
        self.assertEqual(50, reading.moisture_pct)
        self.assertIn("weak_calibration", reading.flags)
        self.assertLess(reading.confidence, 0.8)

    def test_gravimetric_maths_uses_dry_mass_without_a_false_100_percent_cap(self):
        # SIMULATED masses: 125 g moist soil, 100 g dry soil, container already removed.
        self.assertEqual(25, gravimetric_water_pct(125, 100))
        self.assertEqual(150, gravimetric_water_pct(250, 100))
        for wet, dry in ((90, 100), (100, 0), (math.nan, 100), (True, 100)):
            with self.assertRaises(ValueError):
                gravimetric_water_pct(wet, dry)


if __name__ == "__main__":
    unittest.main()
