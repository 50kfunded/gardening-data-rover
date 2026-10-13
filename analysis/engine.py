# SPDX-License-Identifier: MIT
"""Explainable daily rules for SIMULATED visits; thresholds hardware-untested."""

from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import timedelta
from statistics import mean, median

from analysis.garden_runs import utc_time
from analysis.soil_calibration import calibrate
from analysis.soil_quality import Limits, finite_number

STATUS = "planned_hardware_untested"


@dataclass(frozen=True)
class Thresholds:
    baseline_days: int = 14
    min_baseline_days: int = 7
    min_day_coverage: float = 0.75
    min_drying_pairs: int = 6
    drying_delta_pp_h: float = 0.5
    wet_delta_pp: float = 10.0
    ewma_alpha: float = 0.3
    cusum_slack_pp: float = 3.0
    cusum_threshold_pp: float = 20.0
    stuck_visits: int = 24
    stuck_span_counts: float = 1.0
    min_noisy_visits: int = 3

    def __post_init__(self):
        for name in ("baseline_days", "min_baseline_days", "min_drying_pairs", "stuck_visits", "min_noisy_visits"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.min_baseline_days > self.baseline_days or self.stuck_visits < 2:
            raise ValueError("baseline and stuck-window lengths are inconsistent")
        for name in ("min_day_coverage", "drying_delta_pp_h", "wet_delta_pp", "ewma_alpha",
                     "cusum_slack_pp", "cusum_threshold_pp", "stuck_span_counts"):
            value = finite_number(getattr(self, name))
            if value is None or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.min_day_coverage > 1 or self.ewma_alpha > 1:
            raise ValueError("coverage and EWMA alpha must be at most 1")


def confidence(score):
    score = round(max(0.0, min(1.0, score)), 3)
    return {"score": score, "level": "high" if score >= 0.75 else "medium" if score >= 0.45 else "low",
            "meaning": "rule evidence/coverage score, not a probability or measured accuracy"}


def alert(code, day, message, score, enough_data=True, limitation=""):
    return {"code": code, "date": day, "message": message, "confidence": confidence(score),
            "enough_data": enough_data, "limitation": limitation,
            "data_source": "simulation", "status": STATUS}


def stats(values):
    return {"count": len(values), "mean": mean(values) if values else None,
            "median": median(values) if values else None,
            "min": min(values) if values else None, "max": max(values) if values else None}


def _baseline(days, field):
    values = [day[field] for day in days if day[field] is not None]
    if not values:
        return None
    centre = median(values)
    return {"days": len(values), "median": centre,
            "robust_spread": 1.4826 * median(abs(value - centre) for value in values)}


def _visits(observations, schedule, calibration, limits, reference):
    groups = defaultdict(list)
    seen_times = set()
    for observation in observations:
        at = utc_time(observation.at)
        if not schedule.start <= at < schedule.end:
            raise ValueError("observation outside the explicitly requested window")
        if at in seen_times:
            raise ValueError("duplicate/overlapping observation time; don't count it twice")
        seen_times.add(at)
        slot = int((at - schedule.start).total_seconds() // schedule.interval_s)
        groups[slot].append(observation)

    visits = {}
    for slot, items in groups.items():
        items.sort(key=lambda item: item.at)
        if len({item.run_id for item in items}) != 1:
            raise ValueError("overlapping run parts in one visit: don't merge rebooted batches")
        if len(items) > schedule.batch_samples:
            raise ValueError("too many samples for a visit; check the explicit schedule")
        if (items[-1].at - items[0].at).total_seconds() > schedule.batch_samples * 0.1:
            raise ValueError("visit isn't a short 10 Hz settled batch")
        samples = [item.row["soil_raw"] for item in items]
        samples.extend([None] * (schedule.batch_samples - len(samples)))
        reading = calibrate(samples, calibration, limits=limits, reference=reference)
        excluded = {"noisy", "outside_calibration", "weak_calibration", "reference_unreliable"}
        usable = reading.moisture_pct is not None and not excluded.intersection(reading.flags)
        environmental = {}
        for field in ("temp_c", "humidity_pct"):
            values = [finite_number(item.row[field]) for item in items]
            values = [value for value in values if value is not None]
            environmental[field] = median(values) if len(values) >= limits.min_samples else None
        incomplete = (len(items) < schedule.batch_samples
                      or any(item.row[field] is None for item in items for field in ("soil_raw", "temp_c", "humidity_pct"))
                      or any(after.row["t_ms"] - before.row["t_ms"] != 100 for before, after in zip(items, items[1:])))
        visits[slot] = {"at": utc_time(items[0].at), "run_id": items[0].run_id,
                        "soil": reading, "usable": usable, "incomplete": incomplete, **environmental}
    return visits


def analyse(observations, schedule, calibration, *, boundaries=(), thresholds=Thresholds(),
            limits=Limits(), reference=None):
    """One location/calibration only. All outputs stay labelled SIMULATED."""
    if schedule.batch_samples < limits.min_samples:
        raise ValueError("not enough samples per visit for the existing soil calibration")
    visits = _visits(observations, schedule, calibration, limits, reference)
    expected = 86400 // schedule.interval_s
    day_count = (schedule.end - schedule.start).days
    results = []
    alerts = []
    history = deque(maxlen=thresholds.stuck_visits)
    ewma = None
    cusum_high = cusum_low = 0.0
    high_days = low_days = 0

    for day_number in range(day_count):
        day_start = schedule.start + timedelta(days=day_number)
        day_name = day_start.date().isoformat()
        first_slot = day_number * expected
        slots = [visits.get(slot) for slot in range(first_slot, first_slot + expected)]
        present = [visit for visit in slots if visit]
        possible_stuck = False
        for visit in slots:
            if not visit or visit["soil"].raw_median is None or not visit["usable"]:
                history.clear()
                continue
            if history and (visit["at"] - history[-1]["at"]).total_seconds() > 1.5 * schedule.interval_s:
                history.clear()
            history.append(visit)
            if len(history) == thresholds.stuck_visits:
                codes = [old["soil"].raw_median for old in history]
                if max(codes) - min(codes) <= thresholds.stuck_span_counts:
                    possible_stuck = True

        good = [visit for visit in present if visit["usable"]]
        soil_stats = stats([visit["soil"].moisture_pct for visit in good])
        temp_stats = stats([visit["temp_c"] for visit in present if visit["temp_c"] is not None])
        humidity_stats = stats([visit["humidity_pct"] for visit in present if visit["humidity_pct"] is not None])
        coverage = {"visits": len(present) / expected, "soil": len(good) / expected,
                    "temp_c": temp_stats["count"] / expected, "humidity_pct": humidity_stats["count"] / expected}
        soil_confidence = (mean(visit["soil"].confidence for visit in good) * coverage["soil"] if good else 0.0)
        if possible_stuck:
            soil_confidence = min(soil_confidence, 0.35)
        reliable = coverage["soil"] >= thresholds.min_day_coverage and not possible_stuck

        rates = []
        for before, after in zip(slots, slots[1:]):
            if (not before or not after or not before["usable"] or not after["usable"]
                    or before["run_id"] != after["run_id"]
                    or not 6 <= before["at"].hour < 18 or after["at"].hour > 18):
                continue
            hours = (after["at"] - before["at"]).total_seconds() / 3600
            if not 0.5 * schedule.interval_s / 3600 <= hours <= 1.5 * schedule.interval_s / 3600:
                continue
            drop = before["soil"].moisture_pct - after["soil"].moisture_pct
            if drop < -2:  # A wetting jump, not drying. No claim about its cause.
                continue
            rates.append(max(0.0, drop / hours))
        drying = median(rates) if reliable and len(rates) >= thresholds.min_drying_pairs else None
        noisy_count = sum("noisy" in visit["soil"].flags for visit in present)
        incomplete_count = sum(visit["incomplete"] for visit in present)
        rejected_samples = sum(visit["soil"].samples_rejected for visit in present)
        daily_flags = sorted({flag for visit in present for flag in visit["soil"].flags})
        if possible_stuck:
            daily_flags.append("possible_stuck")
        result = {"date": day_name, "expected_visits": expected, "observed_visits": len(present),
                  "coverage": coverage, "moisture": soil_stats, "temp_c": temp_stats,
                  "humidity_pct": humidity_stats, "moisture_basis": "relative_index",
                  "confidence": confidence(soil_confidence), "usable_for_trends": reliable,
                  "drying_pp_per_hour": drying, "drying_pairs": len(rates),
                  "noisy_visits": noisy_count, "rejected_soil_samples": rejected_samples,
                  "incomplete_visits": incomplete_count,
                  "flags": daily_flags, "notes": [], "baseline": {}, "ewma_moisture_pct": None,
                  "cusum": {"up": 0.0, "down": 0.0, "reset_after_alert": False}, "data_source": "simulation", "status": STATUS}

        if incomplete_count or any(value < 1 for value in coverage.values()):
            enough = all(coverage[field] >= thresholds.min_day_coverage for field in ("soil", "temp_c", "humidity_pct"))
            alerts.append(alert("data_gap", day_name,
                                f"Data gap: {len(present)}/{expected} visits; usable soil {len(good)}/{expected}, "
                                f"temperature {temp_stats['count']}/{expected}, humidity {humidity_stats['count']}/{expected}; "
                                f"{incomplete_count} incomplete batches.",
                                0.8, enough, "Not enough data for a complete daily comparison." if not enough
                                else "Partial coverage; missing values weren't filled in."))
        if possible_stuck:
            alerts.append(alert("sensor_stuck", day_name,
                                f"Possibly stuck: {thresholds.stuck_visits} consecutive visit medians changed by "
                                f"at most {thresholds.stuck_span_counts:g} ADC count(s). Check with a controlled dry/wet challenge.",
                                0.35, False, "Not enough data to confirm a fault; stable soil or cached readings can look the same."))
        if noisy_count >= thresholds.min_noisy_visits:
            alerts.append(alert("sensor_noisy", day_name,
                                f"Sensor looks noisy: {noisy_count} visits failed the existing batch-noise checks.",
                                0.65, True, "The noise rule is unvalidated; don't infer real drying from rejected batches."))
        for boundary in boundaries:
            if day_start <= utc_time(boundary.at) < day_start + timedelta(days=1):
                alerts.append(alert("controller_boundary", day_name,
                                    "Controller time/count regression: a new run part was kept separate.",
                                    0.8, True, "Not enough data to identify reboot versus rollover; no slope crosses this boundary."))

        prior = results[max(0, day_number - thresholds.baseline_days):]
        prior = [old for old in prior if old["usable_for_trends"]]
        baseline_days = [{"moisture": old["moisture"]["median"], "drying": old["drying_pp_per_hour"]} for old in prior]
        moisture_baseline = _baseline(baseline_days, "moisture")
        drying_baseline = _baseline(baseline_days, "drying")
        result["baseline"] = {"moisture": moisture_baseline, "drying": drying_baseline}
        moisture_ready = reliable and moisture_baseline and moisture_baseline["days"] >= thresholds.min_baseline_days
        drying_ready = drying is not None and drying_baseline and drying_baseline["days"] >= thresholds.min_baseline_days

        if moisture_ready:
            current = soil_stats["median"]
            wet_limit = moisture_baseline["median"] + max(thresholds.wet_delta_pp, 3 * moisture_baseline["robust_spread"])
            if current > wet_limit + 1e-9:
                alerts.append(alert("unusually_wet", day_name,
                                    f"Unusually wet relative to earlier visits: {current:.1f} index points; "
                                    f"prior median {moisture_baseline['median']:.1f}, trigger above {wet_limit:.1f}.",
                                    min(soil_confidence, mean(old["confidence"]["score"] for old in prior)),
                                    True, "Rain, probe contact and sensor drift can all change this relative index."))
            difference = current - moisture_baseline["median"]
            cusum_high = max(0.0, cusum_high + difference - thresholds.cusum_slack_pp)
            cusum_low = max(0.0, cusum_low - difference - thresholds.cusum_slack_pp)
            high_days = high_days + 1 if difference > thresholds.cusum_slack_pp else 0
            low_days = low_days + 1 if difference < -thresholds.cusum_slack_pp else 0
            result["cusum"] = {"up": cusum_high, "down": cusum_low, "reset_after_alert": False}
            if ((cusum_high >= thresholds.cusum_threshold_pp and high_days >= 2)
                    or (cusum_low >= thresholds.cusum_threshold_pp and low_days >= 2)):
                direction = "up" if cusum_high >= thresholds.cusum_threshold_pp and high_days >= 2 else "down"
                alerts.append(alert("moisture_shift", day_name,
                                    f"Sustained moisture-index shift {direction}: the CUSUM-style total reached "
                                    f"{thresholds.cusum_threshold_pp:g} after at least two consecutive changed days.",
                                    min(soil_confidence, 0.65), True,
                                    "Not enough data to separate a real soil change from sensor drift without repeat references."))
                result["cusum"]["reset_after_alert"] = True
                cusum_high = cusum_low = 0.0
                high_days = low_days = 0
        else:
            cusum_high = cusum_low = 0.0
            high_days = low_days = 0
            if not reliable:
                result["notes"].append("Not enough reliable soil data for daily trend or shift checks.")
                ewma = None  # Don't carry a smooth trend silently across bad/missing days.
            else:
                result["notes"].append(f"Not enough baseline data: need {thresholds.min_baseline_days} earlier usable days for wet/shift checks.")
        if drying_ready:
            rate_limit = drying_baseline["median"] + max(thresholds.drying_delta_pp_h, 3 * drying_baseline["robust_spread"])
            if drying > rate_limit + 1e-9:
                alerts.append(alert("dried_out_faster", day_name,
                                    f"Dried out faster than usual in this relative-index test: {drying:.2f} pp/hour; "
                                    f"prior median {drying_baseline['median']:.2f}, trigger above {rate_limit:.2f}.",
                                    min(soil_confidence, 0.7), True,
                                    "Drying is an observed index slope, not a measured water-loss rate or watering instruction."))
        else:
            result["notes"].append("Not enough drying data or earlier comparable days for a faster-drying check.")
        if reliable:
            current = soil_stats["median"]
            ewma = current if ewma is None else thresholds.ewma_alpha * current + (1 - thresholds.ewma_alpha) * ewma
            result["ewma_moisture_pct"] = ewma
        results.append(result)

    return {"analysis_format_version": 1, "data_source": "simulation", "status": STATUS,
            "notice": "SIMULATED DATA ONLY: planned analysis, not hardware or garden validation.",
            "start_utc": schedule.start.isoformat(), "end_utc": schedule.end.isoformat(),
            "location_scope": "one location and one calibration, selected by the operator",
            "moisture_basis": "relative_index", "thresholds": asdict(thresholds),
            "calibration": asdict(calibration), "soil_limits": asdict(limits),
            "reference_status": "unchecked" if reference is None else list(reference.flags),
            "days": results, "alerts": alerts}
