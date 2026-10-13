# SPDX-License-Identifier: MIT
"""Planned watering advice from SIMULATED days. No actuator or network calls."""

import json
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median

from analysis.soil_quality import finite_number

STATUS = "planned_hardware_untested"
BAD_SOIL = {"possible_stuck", "stuck", "noisy", "drift", "reference_unreliable",
            "outside_calibration", "weak_calibration", "adc_rail"}


def number(value, name, low=0, high=None):
    result = finite_number(value)
    if result is None or result < low or (high is not None and result > high):
        raise ValueError(f"invalid {name}")
    return result


def evidence(score):
    score = round(max(0.0, min(0.65, score)), 3)
    return {"score": score, "level": "medium" if score >= 0.45 else "low",
            "meaning": "provisional evidence score, not measured accuracy or a probability"}


@dataclass(frozen=True)
class BedProfile:
    bed_id: str
    latitude_deg: float
    capacity_mm: float | None = None
    initial_storage_mm: float | None = None
    crop_kc: float = 1.0
    allowed_depletion: float = 0.35
    rain_efficiency: float = 0.8
    irrigation_efficiency: float = 1.0

    def __post_init__(self):
        if not isinstance(self.bed_id, str) or not self.bed_id or not self.bed_id.isidentifier():
            raise ValueError("bed ID must be an anonymous identifier")
        number(self.latitude_deg, "latitude", -66, 66)
        number(self.crop_kc, "crop coefficient", 0.1, 2)
        number(self.allowed_depletion, "allowed depletion", 0.1, 0.8)
        number(self.rain_efficiency, "rain efficiency", 0, 1)
        number(self.irrigation_efficiency, "irrigation efficiency", 0, 1)
        if self.capacity_mm is not None:
            if number(self.capacity_mm, "bucket capacity", 0, 1000) == 0:
                raise ValueError("capacity must be positive")
        if self.initial_storage_mm is not None:
            if self.capacity_mm is None:
                raise ValueError("initial storage needs a capacity")
            number(self.initial_storage_mm, "initial storage", 0, self.capacity_mm)


def extraterrestrial_radiation(day, latitude_deg):
    """FAO-56 daily Ra, MJ/m²/day; deliberately limited to non-polar latitudes."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    if not isinstance(day, date):
        raise ValueError("radiation needs a date")
    phi = math.radians(number(latitude_deg, "latitude", -66, 66))
    j = day.timetuple().tm_yday
    dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
    delta = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
    sunset = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(delta))))
    return max(0.0, 24 * 60 / math.pi * 0.0820 * dr *
               (sunset * math.sin(phi) * math.sin(delta)
                + math.cos(phi) * math.cos(delta) * math.sin(sunset)))


def hargreaves_et0(day, latitude_deg, t_min_c, t_max_c):
    """Temperature-only estimate in mm/day. Ra is converted from MJ using 0.408."""
    low = number(t_min_c, "minimum air temperature", -50, 60)
    high = number(t_max_c, "maximum air temperature", -50, 60)
    if high < low:
        raise ValueError("maximum temperature precedes minimum")
    radiation_mm = 0.408 * extraterrestrial_radiation(day, latitude_deg)
    return max(0.0, 0.0023 * ((low + high) / 2 + 17.8) * math.sqrt(high - low) * radiation_mm)


def bucket_step(storage_mm, capacity_mm, rain_mm, irrigation_mm, et0_mm, *,
                crop_kc=1.0, rain_efficiency=0.8, irrigation_efficiency=1.0):
    """Inputs enter, excess drains, then ET leaves. Every flux is explicit."""
    capacity = number(capacity_mm, "capacity", 0, 1000)
    if capacity == 0:
        raise ValueError("capacity must be positive")
    storage = number(storage_mm, "storage", 0, capacity)
    rain = number(rain_mm, "rain") * number(rain_efficiency, "rain efficiency", 0, 1)
    irrigation = number(irrigation_mm, "irrigation") * number(irrigation_efficiency, "irrigation efficiency", 0, 1)
    demand = number(et0_mm, "ET0") * number(crop_kc, "crop coefficient", 0.1, 2)
    total = storage + rain + irrigation
    drainage = max(0.0, total - capacity)
    evapotranspiration = min(total - drainage, demand)
    final = max(0.0, total - drainage - evapotranspiration)
    return {"storage_mm": final, "effective_rain_mm": rain, "effective_irrigation_mm": irrigation,
            "drainage_mm": drainage, "et_demand_mm": demand, "et_removed_mm": evapotranspiration,
            "depletion_fraction": 1 - final / capacity}


def usable(day):
    value = finite_number(day["moisture"]["median"])
    return (day["usable_for_trends"] and day["coverage"]["soil"] >= 0.75
            and value is not None and 0 <= value <= 100 and not BAD_SOIL.intersection(day["flags"]))


def learn_limits(history, wetting_dates, *, min_days=7, min_wet_cycles=2):
    """Earlier good days from ONE bed. Proxies, never field capacity or wilting point."""
    recent = history[-28:]
    good = [day for day in recent if usable(day)]
    # A post-wetting day is a candidate after drainage, not a saturation reading.
    # Keep separate cycles and reject candidates with rapid continuing drying.
    wet = [day["moisture"]["median"] for day in good
           if (date.fromisoformat(day["date"]) - timedelta(days=1)).isoformat() in wetting_dates
           and day["drying_pp_per_hour"] is not None and day["drying_pp_per_hour"] <= 1.5]
    dry = sorted(day["moisture"]["median"] for day in good if day["date"] not in wetting_dates)
    reason = "Not enough earlier reliable drying days and separate post-wetting cycles."
    if len(good) < min_days or len(wet) < min_wet_cycles or len(dry) < min_days:
        return {"ready": False, "good_days": len(good), "wet_cycles": len(wet), "reason": reason}
    wet_end = median(wet)
    dry_end = dry[int(0.1 * (len(dry) - 1))]
    if wet_end - dry_end < 8:
        return {"ready": False, "good_days": len(good), "wet_cycles": len(wet),
                "reason": "Observed index span is too small; check the probe and collect more dry-downs."}
    return {"ready": True, "wet_index": wet_end, "dry_index": dry_end,
            "good_days": len(good), "wet_cycles": len(wet),
            "basis": "provisional observed index range; not FC, VWC or permanent wilting point"}


def forecast_rain(entry, current_day):
    """Forecast only for the next day, issued before the decision and <=36 h old."""
    if entry is None:
        return None
    try:
        decision = datetime.combine(date.fromisoformat(current_day) + timedelta(days=1),
                                    datetime.min.time(), timezone.utc)
        issued = datetime.fromisoformat(entry["issued_at_utc"])
        if issued.utcoffset() is None or not 0 <= (decision - issued).total_seconds() <= 36 * 3600:
            return None
        if entry["for_date"] != decision.date().isoformat():
            return None
        return {"rain_mm": number(entry["rain_mm"], "forecast rain"),
                "probability": number(entry["probability"], "rain probability", 0, 1)}
    except (KeyError, ValueError, TypeError, OverflowError):
        return None


def advise_bed(days, profile, water_days):
    """Evidence and budget stay separate; forecasts never become observed rain."""
    history, wetting_dates, output = [], set(), []
    storage = profile.initial_storage_mm
    previous_date = None
    for day in days:
        current_date = date.fromisoformat(day["date"])
        if previous_date is not None and current_date != previous_date + timedelta(days=1):
            raise ValueError("watering days must be consecutive and ordered")
        previous_date = current_date
        limits = learn_limits(history, wetting_dates)  # No look-ahead or current-day fit.
        context = water_days.get(day["date"], {})
        budget, et0 = None, None
        reasons = []
        quality = usable(day)
        if not quality:
            reasons.append("Soil evidence is missing, noisy, drifting or possibly stuck.")
        try:
            if day["coverage"]["temp_c"] < 0.75:
                raise ValueError("not enough air temperature coverage")
            et0 = hargreaves_et0(day["date"], profile.latitude_deg,
                                day["temp_c"]["min"], day["temp_c"]["max"])
            rain = number(context.get("rain_mm"), "observed rain")
            irrigation = number(context.get("irrigation_mm"), "recorded irrigation")
            if rain + irrigation >= 3:
                wetting_dates.add(day["date"])
            if storage is None or profile.capacity_mm is None:
                reasons.append("Bucket capacity or initial water storage is unknown.")
            else:
                budget = bucket_step(storage, profile.capacity_mm, rain, irrigation, et0,
                                     crop_kc=profile.crop_kc, rain_efficiency=profile.rain_efficiency,
                                     irrigation_efficiency=profile.irrigation_efficiency)
                storage = budget["storage_mm"]
        except (ValueError, TypeError):
            storage = None  # Unknown rain/ET destroys a complete budget, not silently zero.
            reasons.append("Not enough measured weather or irrigation data for a continuous bucket estimate.")
        forecast = forecast_rain(context.get("forecast"), day["date"])
        if context.get("forecast") is not None and forecast is None:
            reasons.append("Forecast is stale, future-issued, malformed or for a different day; ignored.")
        if not limits["ready"]:
            reasons.append(limits["reason"])
        score = min(day["confidence"]["score"], 0.65)
        if "drift_unchecked" in day["flags"]:
            score = min(score, 0.5)
        action = "check_by_finger"
        sensor_depletion = None
        ready = quality and limits["ready"] and budget is not None
        if ready:
            sensor_depletion = max(0.0, min(1.0, (limits["wet_index"] - day["moisture"]["median"])
                                          / (limits["wet_index"] - limits["dry_index"])))
            model_depletion = budget["depletion_fraction"]
            if abs(sensor_depletion - model_depletion) > 0.25:
                score = min(score, 0.3)
                ready = False
                reasons.append("Probe and bucket disagree; check contact, amounts, capacity and calibration.")
            elif score < 0.45:
                ready = False
                reasons.append("Evidence score is too low for a watering suggestion.")
            elif min(sensor_depletion, model_depletion) >= profile.allowed_depletion:
                if (max(sensor_depletion, model_depletion) < 0.8 and forecast
                        and forecast["rain_mm"] >= 3 and forecast["probability"] >= 0.6):
                    action = "watch_forecast"
                    reasons.append("Rain is forecast tomorrow; check the bed now and recheck whether rain actually arrives.")
                else:
                    action = "consider_watering"
                    reasons.append("Both provisional estimates crossed the proposed depletion limit.")
            else:
                action = "hold_and_check"
                reasons.append("Both estimates do not yet indicate the proposed watering threshold.")
        if not ready:
            score = min(score, 0.3)
        output.append({"date": day["date"], "bed_id": profile.bed_id, "action": action,
                       "confidence": evidence(score), "enough_data": bool(ready),
                       "et0_mm": et0, "bucket": budget, "sensor_depletion_fraction": sensor_depletion,
                       "limits": limits, "forecast": forecast, "reasons": reasons,
                       "fallback": "Check by finger at the recorded depth, compare another spot, and inspect the plant before watering.",
                       "data_source": "simulation", "status": STATUS})
        history.append(day)
    return {"watering_format_version": 1, "bed_id": profile.bed_id, "profile": asdict(profile),
            "data_source": "simulation", "status": STATUS, "days": output,
            "notice": "SIMULATED DATA ONLY: watering suggestions, no automatic watering or validated soil physics."}


def load_inputs(path, schedule):
    """Separate simulation sidecar. No changes to telemetry or run metadata."""
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(obj, dict) or type(obj.get("watering_input_version")) is not int
            or obj.get("watering_input_version") != 1 or obj.get("data_source") != "simulation"
            or obj.get("hardware_status") != "untested" or not isinstance(obj.get("notice"), str)
            or not obj["notice"].startswith("SIMULATED DATA:")):
        raise ValueError("watering inputs must be labelled SIMULATED and untested")
    profile = BedProfile(**obj["profile"])
    water_days = obj["days"]
    if not isinstance(water_days, dict):
        raise ValueError("water days must be a date mapping")
    for key in water_days:
        at = date.fromisoformat(key)
        if not schedule.start.date() <= at < schedule.end.date():
            raise ValueError("weather day is outside the scenario")
        if not isinstance(water_days[key], dict):
            raise ValueError("weather day must be an object")
    return profile, water_days


def weekly_watering_line(advice, start, end):
    days = [day for day in advice["days"] if start <= day["date"] <= end]
    ready = [day for day in days if day["enough_data"]]
    if len(ready) < 5:
        return (f"- Watering advisor ({advice['bed_id']}): not enough data "
                f"({len(ready)}/5 usable days needed). Check by finger; no automatic watering. Confidence: low.")
    counts = {action: sum(day["action"] == action for day in ready)
              for action in ("consider_watering", "watch_forecast", "hold_and_check")}
    return (f"- Watering advisor ({advice['bed_id']}): consider watering on {counts['consider_watering']} day(s), "
            f"watch forecast rain on {counts['watch_forecast']}, hold and check on {counts['hold_and_check']}; "
            f"{len(days)-len(ready)} day(s) need a finger check because evidence is incomplete. "
            "Confidence: medium at best; provisional bucket and index limits, no automatic watering.")
