# SPDX-License-Identifier: MIT
"""SIMULATED private records and generated pixels; never real photos or plants."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageCms, PngImagePlugin

from analysis.dataset import private_root, safe_photo, sanitize_dataset, validate_dataset


def simulated_record(index=1, plant="plant_sim", day="2026-10-13", split="unassigned"):
    return {"image_id": f"image_sim_{index}", "visit_id": f"visit_sim_{index}",
            "experiment_id": "experiment_sim", "plant_id": plant, "bed_id": "bed_sim",
            "camera_id": "camera_sim", "image_path": f"raw/image_sim_{index}.jpg",
            "data_source": "simulation", "view": "mid", "distance_mm": 400,
            "captured_at_utc": day + "T12:00:00+00:00", "sensor_at_utc": day + "T11:59:30+00:00",
            "soil_raw": 1800, "soil_moisture_index": 60, "moisture_basis": "relative_index",
            "soil_temp_c": 18.5, "air_temp_c": 20, "humidity_pct": 60,
            "soil_gwc_pct": None, "soil_sample_id": None,
            "pot_mass_g": 1000, "water_added_g": None, "calibration_id": "calibration_sim",
            "depth_mm": 70, "contact": "good", "weather": {"source": "simulation",
            "observed_at_utc": day + "T11:00:00+00:00", "rain_mm": 0,
            "forecast_issued_at_utc": None, "forecast_rain_mm": None},
            "labels": {"visible_wilting": "uncertain", "water_status": "unknown",
                       "cause": "unknown", "confidence": "low", "reviewed": False},
            "annotator_id": "annotator_sim", "privacy_reviewed": True, "split": split}


class SimulatedDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rover-dataset-sim-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "private_sim"
        (self.root / "raw").mkdir(parents=True)
        self.meta = {"dataset_format_version": 1, "dataset_id": "dataset_sim",
                     "data_source": "simulation", "status": "planned_untested",
                     "notice": "SIMULATED DATA ONLY. Generated pixels, no real garden.",
                     "split_policy": "plant_and_date"}
        self.rows = [simulated_record()]
        self.write()

    def write(self, photos=True):
        (self.root / "dataset.json").write_text(json.dumps(self.meta), encoding="utf-8")
        (self.root / "manifest.jsonl").write_text("".join(json.dumps(row) + "\n" for row in self.rows), encoding="utf-8")
        if photos:
            for index, row in enumerate(self.rows, 1):
                path = self.root / row["image_path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (8, 6), (index * 37 % 255, 96, 160)).save(path)

    def errors(self):
        self.write(photos=False)
        return " ".join(validate_dataset(self.root)["errors"])

    def test_valid_simulated_manifest_and_unassigned_notice(self):
        result = validate_dataset(self.root)
        self.assertTrue(result["valid"], result)
        self.assertEqual("simulation", result["data_source"])
        self.assertTrue(any("collection-only" in message for message in result["warnings"]))

    def test_null_evidence_stays_missing_without_creating_a_health_label(self):
        for field in ("soil_raw", "soil_moisture_index", "soil_temp_c", "air_temp_c", "humidity_pct",
                      "sensor_at_utc", "calibration_id", "pot_mass_g"):
            self.rows[0][field] = None
        self.write(photos=False)
        self.assertTrue(validate_dataset(self.root)["valid"])
        self.assertEqual("uncertain", self.rows[0]["labels"]["visible_wilting"])

    def test_mixed_source_unknown_fields_and_wrong_unit_ranges_fail(self):
        original = copy.deepcopy(self.rows[0])
        for key, value in (("soil_raw", 4096), ("soil_raw", 18.5), ("humidity_pct", 101),
                           ("soil_temp_c", float("nan")), ("distance_mm", None),
                           ("soil_moisture_index", True), ("data_source", "observation")):
            self.rows[0] = dict(original, **{key: value})
            self.assertTrue(self.errors(), (key, value))
        self.rows[0] = dict(original, latitude=0)
        self.assertIn("documented fields", self.errors())

    def test_stale_sensor_and_non_utc_timestamp_fail(self):
        self.rows[0]["sensor_at_utc"] = "2026-10-13T10:00:00+00:00"
        self.assertIn("five-minute", self.errors())
        self.rows[0]["captured_at_utc"] = "2026-10-13T12:00:00"
        self.assertIn("UTC", self.errors())
        self.rows[0]["captured_at_utc"] = "2026-10-13T12:00:00+01:00"
        self.assertIn("UTC", self.errors())

    def test_future_weather_cannot_be_ground_truth_at_capture(self):
        self.rows[0]["weather"]["forecast_issued_at_utc"] = "2026-10-14T12:00:00+00:00"
        self.rows[0]["weather"]["forecast_rain_mm"] = 5
        self.assertIn("after the capture", self.errors())

    def test_derived_moisture_needs_calibration_and_raw_reference(self):
        self.rows[0]["calibration_id"] = None
        self.assertIn("calibration ID", self.errors())

    def test_valid_joint_plant_and_later_date_splits(self):
        self.rows = [simulated_record(1, "plant_a_sim", "2026-10-13", "train"),
                     simulated_record(2, "plant_b_sim", "2026-11-13", "validation"),
                     simulated_record(3, "plant_c_sim", "2026-12-13", "test")]
        self.write()
        self.assertTrue(validate_dataset(self.root)["valid"])

    def test_same_plant_or_date_cannot_be_randomly_split_by_image(self):
        self.rows = [simulated_record(1, "plant_a_sim", "2026-10-13", "train"),
                     simulated_record(2, "plant_a_sim", "2026-11-13", "test")]
        self.write()
        self.assertIn("plant leaks", self.errors())
        self.rows[1]["plant_id"] = "plant_b_sim"
        self.rows[1]["captured_at_utc"] = "2026-10-13T12:00:00+00:00"
        self.rows[1]["sensor_at_utc"] = "2026-10-13T11:59:30+00:00"
        self.rows[1]["weather"]["observed_at_utc"] = "2026-10-13T11:00:00+00:00"
        self.assertIn("experiment/date", self.errors())

    def test_reversed_date_blocks_and_same_visit_leakage_fail(self):
        self.rows = [simulated_record(1, "plant_a_sim", "2026-12-13", "train"),
                     simulated_record(2, "plant_b_sim", "2026-11-13", "test")]
        self.rows[1]["visit_id"] = self.rows[0]["visit_id"]
        self.write()
        errors = self.errors()
        self.assertIn("date blocks", errors)
        self.assertIn("visit leaks", errors)

    def test_identical_pixels_in_different_files_cannot_cross_splits(self):
        self.rows = [simulated_record(1, "plant_a_sim", "2026-10-13", "train"),
                     simulated_record(2, "plant_b_sim", "2026-11-13", "test")]
        self.write()
        (self.root / self.rows[1]["image_path"]).write_bytes((self.root / self.rows[0]["image_path"]).read_bytes())
        self.assertIn("identical decoded pixels", self.errors())

    def test_duplicate_reference_missing_image_and_unlisted_file_fail(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        self.assertIn("duplicate image", self.errors())
        self.rows = self.rows[:1]
        self.rows[0]["image_path"] = "raw/missing.jpg"
        self.assertIn("missing", self.errors())
        self.assertIn("unlisted", self.errors())

    def test_absolute_traversal_backslash_and_unsupported_format_fail(self):
        for path in ("../escape.jpg", "raw/../escape.jpg", "C:/escape.jpg", "/escape.jpg",
                     "raw\\image.jpg", "raw/image.heic", "raw/unsafe%name.jpg"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_photo(self.root, path)
        with self.assertRaises(ValueError):
            private_root(Path(__file__).resolve().parents[2] / "public_photos")

    def test_corrupt_mislabeled_and_animated_photos_fail(self):
        path = self.root / self.rows[0]["image_path"]
        path.write_bytes(b"SIMULATED invalid image")
        self.assertIn("unreadable", self.errors())
        Image.new("RGB", (8, 6)).save(path, format="PNG")
        self.assertIn("unsupported", self.errors())
        self.rows[0]["image_path"] = "raw/image_sim_1.webp"
        path.unlink()
        path = self.root / self.rows[0]["image_path"]
        Image.new("RGB", (8, 6), "red").save(path, save_all=True,
                                               append_images=[Image.new("RGB", (8, 6), "blue")], format="WEBP")
        self.assertIn("unsupported", self.errors())

    def test_label_uncertainty_is_valid_but_diagnoses_are_not_assumed(self):
        self.assertTrue(validate_dataset(self.root)["valid"])
        self.rows[0]["labels"]["cause"] = "disease"
        self.assertIn("diagnosis", self.errors())

    def test_jpeg_gps_exif_and_orientation_are_stripped_from_new_png(self):
        path = self.root / self.rows[0]["image_path"]
        exif = Image.Exif()
        exif[274] = 6
        exif[315] = "SIMULATED metadata only"
        exif[34853] = {1: "N", 2: (0.0, 0.0, 0.0), 3: "E", 4: (0.0, 0.0, 0.0)}
        Image.new("RGB", (8, 6), (30, 96, 160)).save(path, exif=exif)
        original = path.read_bytes()
        target = sanitize_dataset(self.root)
        self.assertEqual(original, path.read_bytes())
        with Image.open(target / "processed/image_sim_1.png") as output:
            self.assertEqual((6, 8), output.size)
            self.assertFalse(output.getexif())
            self.assertFalse(output.info)
        exported = json.loads((target / "manifest.jsonl").read_text())
        self.assertEqual(self.rows[0]["captured_at_utc"], exported["captured_at_utc"])
        self.assertEqual(self.rows[0]["soil_raw"], exported["soil_raw"])
        self.assertTrue(validate_dataset(target)["valid"])

    def test_png_text_xmp_and_icc_are_not_carried_into_export(self):
        old = self.root / self.rows[0]["image_path"]
        old.unlink()
        self.rows[0]["image_path"] = "raw/image_sim_1.png"
        self.write(photos=False)
        text = PngImagePlugin.PngInfo()
        text.add_text("XML:com.adobe.xmp", "SIMULATED location metadata")
        text.add_text("Comment", "SIMULATED caption")
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        Image.new("RGB", (8, 6), (30, 96, 160)).save(self.root / self.rows[0]["image_path"], pnginfo=text, icc_profile=profile)
        target = sanitize_dataset(self.root)
        with Image.open(target / "processed/image_sim_1.png") as output:
            self.assertFalse(output.info)
        self.assertTrue(validate_dataset(target)["valid"])

    def test_export_requires_review_and_never_overwrites(self):
        self.rows[0]["privacy_reviewed"] = False
        self.write(photos=False)
        with self.assertRaisesRegex(ValueError, "privacy review"):
            sanitize_dataset(self.root)
        self.assertFalse((self.root / "sanitized").exists())
        self.rows[0]["privacy_reviewed"] = True
        self.write(photos=False)
        sanitize_dataset(self.root)
        with self.assertRaises(FileExistsError):
            sanitize_dataset(self.root)

    def test_processed_metadata_and_incomplete_exports_are_rejected(self):
        target = sanitize_dataset(self.root)
        path = target / "processed/image_sim_1.png"
        text = PngImagePlugin.PngInfo()
        text.add_text("Comment", "SIMULATED metadata")
        Image.new("RGB", (8, 6)).save(path, pnginfo=text)
        self.assertIn("embedded metadata", " ".join(validate_dataset(target)["errors"]))
        (target / "INCOMPLETE").write_text("SIMULATED partial export")
        self.assertFalse(validate_dataset(target)["valid"])

    def test_invalid_json_duplicate_keys_and_empty_dataset_fail(self):
        path = self.root / "manifest.jsonl"
        for text in ("", "not JSON", '{"image_id":"a","image_id":"b"}'):
            path.write_text(text)
            self.assertFalse(validate_dataset(self.root)["valid"])

    def test_cli_validates_and_exports_only_synthetic_private_data(self):
        result = subprocess.run([sys.executable, "-m", "analysis.dataset", str(self.root), "--sanitize"],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Originals untouched", result.stdout)
        self.assertTrue(validate_dataset(self.root / "sanitized")["valid"])

    def test_wrong_record_types_fail_without_a_traceback(self):
        original = copy.deepcopy(self.rows[0])
        for field in ("view", "split", "labels", "weather", "image_id"):
            self.rows[0] = dict(original, **{field: []})
            self.assertTrue(self.errors())

    def test_links_are_rejected_before_photo_reading(self):
        with patch.object(Path, "is_symlink", return_value=True), self.assertRaisesRegex(ValueError, "links"):
            safe_photo(self.root, self.rows[0]["image_path"])

    def test_bad_profile_keeps_failed_export_marked_incomplete(self):
        path = self.root / self.rows[0]["image_path"]
        Image.new("RGB", (8, 6)).save(path, icc_profile=b"SIMULATED invalid ICC profile")
        with self.assertRaises(ValueError):
            sanitize_dataset(self.root)
        self.assertTrue((self.root / "sanitized/INCOMPLETE").exists())
        self.assertFalse(validate_dataset(self.root / "sanitized")["valid"])

    def test_bad_cli_manifest_fails_without_echoing_private_fields(self):
        (self.root / "manifest.jsonl").write_text("SIMULATED invalid private metadata")
        result = subprocess.run([sys.executable, "-m", "analysis.dataset", str(self.root)], capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("invalid private metadata", result.stdout + result.stderr)

    def test_transparent_pixels_are_not_exposed_when_exporting_rgb(self):
        (self.root / self.rows[0]["image_path"]).unlink()
        self.rows[0]["image_path"] = "raw/image_sim_1.png"
        self.write(photos=False)
        Image.new("RGBA", (8, 6), (255, 0, 0, 0)).save(self.root / self.rows[0]["image_path"])
        target = sanitize_dataset(self.root)
        with Image.open(target / "processed/image_sim_1.png") as output:
            self.assertEqual((255, 255, 255), output.getpixel((0, 0)))

    def test_organic_soil_gwc_is_not_clamped_to_100_percent(self):
        self.rows[0]["soil_gwc_pct"] = 150
        self.rows[0]["soil_sample_id"] = "sample_sim"
        self.write(photos=False)
        self.assertTrue(validate_dataset(self.root)["valid"])
        self.rows[0]["soil_sample_id"] = None
        self.assertIn("sample ID", self.errors())
