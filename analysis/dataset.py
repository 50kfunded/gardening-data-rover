# SPDX-License-Identifier: MIT
"""Private dataset validation and photo export. Tests use SIMULATED pixels only."""

import argparse
import hashlib
import io
import json
import math
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath

ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
SPLITS = {"train", "validation", "test", "unassigned"}
META_FIELDS = {"dataset_format_version", "dataset_id", "data_source", "status", "notice", "split_policy"}
FIELDS = {"image_id", "visit_id", "experiment_id", "plant_id", "bed_id", "camera_id", "image_path",
          "data_source", "view", "distance_mm", "captured_at_utc", "sensor_at_utc", "soil_raw",
          "soil_moisture_index", "moisture_basis", "soil_temp_c", "air_temp_c", "humidity_pct",
          "soil_gwc_pct", "soil_sample_id", "pot_mass_g", "water_added_g", "calibration_id", "depth_mm", "contact", "weather",
          "labels", "annotator_id", "privacy_reviewed", "split"}
WEATHER_FIELDS = {"source", "observed_at_utc", "rain_mm", "forecast_issued_at_utc", "forecast_rain_mm"}
LABEL_FIELDS = {"visible_wilting", "water_status", "cause", "confidence", "reviewed"}


def _json(text):
    def nonfinite(_):
        raise ValueError("non-finite JSON number")
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(text, parse_constant=nonfinite, object_pairs_hook=unique)


def utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp needs UTC text")
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must have an explicit UTC offset")
    return result.astimezone(timezone.utc)


def _number(value, low, high=None, *, integer=False):
    try:
        return (value is None or (not isinstance(value, bool) and isinstance(value, (int, float))
                and (not integer or isinstance(value, int)) and math.isfinite(value)
                and value >= low and (high is None or value <= high)))
    except OverflowError:
        return False


def safe_photo(root, relative):
    """Reject traversal, absolute paths, links/junctions and unsupported formats."""
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("photo path must be a relative POSIX path")
    parts = PurePosixPath(relative).parts
    if (not parts or PurePosixPath(relative).is_absolute() or PureWindowsPath(relative).drive
            or any(part in {".", ".."} for part in relative.split("/"))
            or parts[0] not in {"raw", "processed"}):
        raise ValueError("photo path must stay under raw/ or processed/")
    candidate = root
    for part in parts:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", part):
            raise ValueError("photo path must use anonymous safe names")
        candidate = candidate / part
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError("photo paths cannot use links or junctions")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root) or resolved.suffix.lower() not in FORMATS:
        raise ValueError("photo path or format isn't supported")
    if not resolved.is_file():
        raise ValueError("referenced photo is missing")
    return resolved


def _images():
    try:
        from PIL import Image, ImageCms, ImageOps
    except ImportError as error:
        raise ValueError("photo tools need analysis/dataset_requirements.txt installed") from error
    return Image, ImageCms, ImageOps


def inspect_photo(path):
    Image, _, _ = _images()
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as photo:
            if photo.format != FORMATS[path.suffix.lower()] or getattr(photo, "n_frames", 1) != 1:
                raise ValueError("photo format doesn't match or has multiple frames")
            if photo.mode not in {"RGB", "RGBA", "L", "CMYK"}:
                raise ValueError("unsupported photo colour mode")
            photo.load()
            exif = photo.getexif()
            return {"has_metadata": bool(exif) or bool(photo.info),
                    "has_gps": 34853 in exif,
                    "pixel_hash": hashlib.sha256(photo.convert("RGB").tobytes()
                                                 + str(photo.size).encode()).hexdigest()}


def _validate_record(row, source):
    errors = []
    if not isinstance(row, dict) or set(row) != FIELDS:
        return ["record must have exactly the documented fields; no location/contact fields"], None
    for field in ("image_id", "visit_id", "experiment_id", "plant_id", "bed_id", "camera_id", "annotator_id"):
        if not isinstance(row[field], str) or not ID.fullmatch(row[field]):
            errors.append(f"{field} must be an anonymous ID")
    if row["calibration_id"] is not None and (not isinstance(row["calibration_id"], str)
                                               or not ID.fullmatch(row["calibration_id"])):
        errors.append("calibration_id must be an anonymous ID or null")
    if row["soil_sample_id"] is not None and (not isinstance(row["soil_sample_id"], str)
                                              or not ID.fullmatch(row["soil_sample_id"])):
        errors.append("soil_sample_id must be an anonymous ID or null")
    if row["data_source"] != source:
        errors.append("record source must match dataset; don't mix simulated and observed data")
    if row["view"] not in {"wide", "mid", "close"}:
        errors.append("view must be wide, mid or close")
    if row["split"] not in SPLITS:
        errors.append("unknown split")
    if row["moisture_basis"] != "relative_index":
        errors.append("current moisture basis must stay relative_index")
    if row["contact"] not in {"good", "uncertain", "unknown"}:
        errors.append("contact needs an explicit assessment")
    if type(row["privacy_reviewed"]) is not bool:
        errors.append("privacy_reviewed must be boolean")
    ranges = {"distance_mm": (1, 20000), "soil_raw": (0, 4095), "soil_moisture_index": (0, 100),
              "soil_temp_c": (-55, 125), "air_temp_c": (-55, 125), "humidity_pct": (0, 100),
              "soil_gwc_pct": (0, None),
              "pot_mass_g": (0, None), "water_added_g": (0, None), "depth_mm": (0, 2000)}
    for field, (low, high) in ranges.items():
        if not _number(row[field], low, high, integer=field == "soil_raw"):
            errors.append(f"{field} is outside its numeric/unit range")
    if row["distance_mm"] is None:
        errors.append("distance_mm must be measured")
    if row["soil_moisture_index"] is not None and (row["soil_raw"] is None or row["calibration_id"] is None):
        errors.append("derived moisture needs raw evidence and calibration ID")
    if row["soil_gwc_pct"] is not None and row["soil_sample_id"] is None:
        errors.append("measured GWC needs its soil sample ID")
    captured = None
    try:
        captured = utc(row["captured_at_utc"])
        sensor = utc(row["sensor_at_utc"]) if row["sensor_at_utc"] is not None else None
        if sensor is not None and abs((sensor - captured).total_seconds()) > 300:
            errors.append("sensor/photo join exceeds the proposed five-minute window")
        if any(row[key] is not None for key in ("soil_raw", "soil_temp_c", "air_temp_c", "humidity_pct")) and sensor is None:
            errors.append("sensor evidence needs its own timestamp")
    except (ValueError, TypeError, OverflowError):
        errors.append("capture/sensor timestamp must be valid UTC")
    weather = row["weather"]
    if not isinstance(weather, dict) or set(weather) != WEATHER_FIELDS:
        errors.append("weather must use the documented fields; no coordinates")
    else:
        if weather["source"] not in {"unknown", "simulation", "manual", "open_meteo", "met_norway"}:
            errors.append("unknown weather source")
        for field in ("rain_mm", "forecast_rain_mm"):
            if not _number(weather[field], 0, 1000):
                errors.append("weather amount must be mm or null")
        for field in ("observed_at_utc", "forecast_issued_at_utc"):
            try:
                if weather[field] is not None:
                    at = utc(weather[field])
                    if captured is not None and at > captured:
                        errors.append("weather evidence was recorded/issued after the capture")
            except (ValueError, TypeError, OverflowError):
                errors.append("weather timestamp must be valid UTC")
        if weather["rain_mm"] is not None and weather["observed_at_utc"] is None:
            errors.append("rain evidence needs its timestamp")
        if weather["forecast_rain_mm"] is not None and weather["forecast_issued_at_utc"] is None:
            errors.append("forecast evidence needs its issue time")
    labels = row["labels"]
    if not isinstance(labels, dict) or set(labels) != LABEL_FIELDS:
        errors.append("labels must use the documented separate appearance/status fields")
    else:
        if labels["visible_wilting"] not in {"none", "mild", "clear", "severe", "uncertain"}:
            errors.append("unknown visible wilting label")
        if labels["water_status"] not in {"well_watered_control", "dry_down", "rewatered", "unknown"}:
            errors.append("unknown water status label")
        if labels["cause"] not in {"unknown", "controlled_withholding"}:
            errors.append("cause cannot be inferred as a diagnosis")
        if labels["confidence"] not in {"low", "medium", "high"} or type(labels["reviewed"]) is not bool:
            errors.append("label confidence and review flag are required")
    return errors, captured


def validate_dataset(folder):
    """Read-only; messages use record numbers, never embedded private metadata."""
    root = Path(folder).resolve()
    Image, _, _ = _images()
    errors, notes, records = [], [], []
    try:
        if (root / "INCOMPLETE").exists():
            raise ValueError("incomplete export")
        for name in ("dataset.json", "manifest.jsonl"):
            path = root / name
            if path.is_symlink() or path.is_junction() or path.stat().st_size > 20_000_000:
                raise ValueError("manifest is linked or too large")
        meta = _json((root / "dataset.json").read_text(encoding="utf-8"))
        if (not isinstance(meta, dict) or set(meta) != META_FIELDS
                or type(meta["dataset_format_version"]) is not int or meta["dataset_format_version"] != 1
                or not isinstance(meta["dataset_id"], str) or not ID.fullmatch(meta["dataset_id"])
                or meta["data_source"] not in {"simulation", "observation"}
                or meta["status"] != "planned_untested" or meta["split_policy"] != "plant_and_date"
                or not isinstance(meta["notice"], str)
                or (meta["data_source"] == "simulation" and not meta["notice"].startswith("SIMULATED DATA"))):
            raise ValueError("dataset declaration must match the documented planned/untested schema")
        lines = (root / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
        records = [_json(line) for line in lines if line.strip()]
        if not records or len(records) > 100000:
            raise ValueError("need 1..100000 records")
    except (OSError, ValueError, TypeError, KeyError):
        return {"valid": False, "records": 0, "errors": ["dataset declaration/manifest is missing, invalid or incomplete"], "warnings": []}

    identifiers, paths, plant_splits, date_splits, visit_splits, content_splits = set(), set(), {}, {}, {}, {}
    split_dates = {name: [] for name in ("train", "validation", "test")}
    for i, row in enumerate(records, 1):
        try:
            bad, captured = _validate_record(row, meta["data_source"])
        except (TypeError, ValueError, OverflowError):
            bad, captured = ["record fields have invalid types"], None
        if bad:
            errors.extend(f"record {i}: {message}" for message in bad)
            continue
        if row["image_id"] in identifiers or row["image_path"] in paths:
            errors.append(f"record {i}: duplicate image ID or photo reference")
        identifiers.add(row["image_id"])
        paths.add(row["image_path"])
        split = row["split"]
        if split != "unassigned":
            keys = ((plant_splits, row["plant_id"], "plant"),
                    (date_splits, (row["experiment_id"], captured.date()), "experiment/date"),
                    (visit_splits, row["visit_id"], "visit"))
            for mapping, key, label in keys:
                if key in mapping and mapping[key] != split:
                    errors.append(f"record {i}: {label} leaks across splits")
                mapping[key] = split
            split_dates[split].append(captured.date())
        try:
            path = safe_photo(root, row["image_path"])
            info = inspect_photo(path)
            if row["image_path"].startswith("processed/") and info["has_metadata"]:
                errors.append(f"record {i}: processed photo still contains embedded metadata")
            elif info["has_metadata"]:
                notes.append(f"record {i}: raw photo has embedded metadata; keep private and sanitize before export")
            if split != "unassigned":
                digest = info["pixel_hash"]
                if digest in content_splits and content_splits[digest] != split:
                    errors.append(f"record {i}: identical decoded pixels leak across splits")
                content_splits[digest] = split
        except (OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            errors.append(f"record {i}: photo is missing, unsafe, unsupported or unreadable")
    for earlier, later in (("train", "validation"), ("train", "test"), ("validation", "test")):
        if split_dates[earlier] and split_dates[later] and max(split_dates[earlier]) >= min(split_dates[later]):
            errors.append(f"{earlier}/{later}: date blocks must be ordered and non-overlapping")
    for prefix in ("raw", "processed"):
        base = root / prefix
        if base.exists() and (base.is_symlink() or base.is_junction()):
            errors.append("photo directories cannot be links or junctions")
            continue
        for path in base.rglob("*") if base.exists() else ():
            if path.is_file() and path.relative_to(root).as_posix() not in paths:
                errors.append("unlisted file in photo directory; review it before export")
    if any(isinstance(row, dict) and row.get("split") == "unassigned" for row in records):
        notes.append("unassigned records are collection-only; exclude from evaluation")
    return {"valid": not errors, "records": len(records), "data_source": meta["data_source"],
            "errors": errors, "warnings": notes}


def sanitize_dataset(folder):
    """New PNG copies under sanitized/. Originals and their timestamps are untouched."""
    root = Path(folder).resolve()
    result = validate_dataset(root)
    if not result["valid"]:
        raise ValueError("dataset must validate before photo export")
    meta = _json((root / "dataset.json").read_text(encoding="utf-8"))
    records = [_json(line) for line in (root / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(not row["privacy_reviewed"] for row in records):
        raise ValueError("all photos need a human privacy review before export")
    target = root / "sanitized"
    target.mkdir(exist_ok=False)
    marker = target / "INCOMPLETE"
    marker.write_text("Incomplete private export. Do not use or publish.\n", encoding="utf-8")
    (target / "processed").mkdir()
    Image, ImageCms, ImageOps = _images()
    for row in records:
        path = safe_photo(root, row["image_path"])
        with Image.open(path) as original:
            rendered = ImageOps.exif_transpose(original)
            profile = original.info.get("icc_profile")
            if profile:
                try:
                    rendered = ImageCms.profileToProfile(rendered, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                                                         ImageCms.createProfile("sRGB"),
                                                         outputMode="RGBA" if rendered.mode == "RGBA" else "RGB")
                except (ImageCms.PyCMSError, OSError, TypeError) as error:
                    raise ValueError("embedded colour profile could not be converted") from error
            if rendered.mode == "RGBA":
                background = Image.new("RGBA", rendered.size, "white")
                background.alpha_composite(rendered)
                rendered = background.convert("RGB")  # Don't expose colours hidden under transparency.
            else:
                rendered = rendered.convert("RGB")  # Untagged inputs assumed sRGB; document this limit.
            clean = Image.new("RGB", rendered.size)
            clean.paste(rendered)
            row["image_path"] = f"processed/{row['image_id']}.png"
            with (target / row["image_path"]).open("xb") as output:
                clean.save(output, format="PNG")  # Fresh pixels: no EXIF/XMP/IPTC/text/thumbnail copied.
            if inspect_photo(target / row["image_path"])["has_metadata"]:
                raise ValueError("photo metadata remained after export")
    (target / "dataset.json").write_text(json.dumps(meta, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (target / "manifest.jsonl").write_text("".join(json.dumps(row, allow_nan=False) + "\n" for row in records), encoding="utf-8")
    marker.unlink()  # Only the marker created by this invocation, never source data.
    checked = validate_dataset(target)
    if not checked["valid"]:
        marker.write_text("Export validation failed. Do not use or publish.\n", encoding="utf-8")
        raise ValueError("sanitized copies failed validation")
    return target


def private_root(folder):
    root = Path(folder).resolve()
    repo = Path(__file__).resolve().parents[1]
    if root.is_relative_to(repo) and not root.is_relative_to(repo / "data" / "private" / "datasets"):
        raise ValueError("inside this repo, use the gitignored data/private/datasets/ directory")
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--sanitize", action="store_true", help="create a new private sanitized/ dataset; never overwrite")
    args = parser.parse_args()
    try:
        root = private_root(args.folder)
        result = validate_dataset(root)
        print("PLANNED/UNTESTED dataset tooling; tests use SIMULATED images only.")
        print(f"Records: {result['records']}; errors: {len(result['errors'])}; warnings: {len(result['warnings'])}")
        for message in result["errors"] + result["warnings"]:
            print(message)
        if not result["valid"]:
            raise ValueError("dataset validation failed")
        if args.sanitize:
            sanitize_dataset(root)
            print("Created and verified private sanitized/ copies. Originals untouched; no upload or publication.")
    except (OSError, ValueError, TypeError, KeyError, SyntaxError):
        # Avoid echoing OS errors with private paths or embedded photo fields.
        parser.exit(1, "FAIL: dataset could not be validated/exported. Check the manifest, photo format and a new output folder.\n")


if __name__ == "__main__":
    main()
