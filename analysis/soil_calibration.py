# SPDX-License-Identifier: MIT
"""Planned soil calibration, tested only with SIMULATED DATA. No hardware calls."""

from dataclasses import dataclass

from analysis.soil_quality import Limits, check_stuck, finite_number, summarise


@dataclass(frozen=True)
class Calibration:
    """Measured dry and wet reference codes are required; there are no defaults."""

    dry_raw: float
    wet_raw: float

    def __post_init__(self):
        for value in (self.dry_raw, self.wet_raw):
            number = finite_number(value)
            if number is None or not 0 <= number <= 4095:
                raise ValueError("calibration endpoints must be finite 12-bit counts")
        if self.dry_raw == self.wet_raw:
            raise ValueError("dry and wet endpoints must differ")


@dataclass(frozen=True)
class ReferenceCheck:
    dry_shift_counts: float | None
    wet_shift_counts: float | None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class SoilReading:
    # This percentage is a relative index, not gravimetric or volumetric water content.
    moisture_pct: float | None
    raw_median: float | None
    mad_counts: float | None
    samples_used: int
    samples_rejected: int
    confidence: float
    flags: tuple[str, ...]
    basis: str = "relative_index"
    status: str = "planned_hardware_untested"


def check_drift(calibration, *, dry_samples=None, wet_samples=None, limits=Limits()):
    """Compare repeated air/water references, not two changing soil locations."""
    shifts = []
    flags = set()
    for samples, baseline in ((dry_samples, calibration.dry_raw),
                              (wet_samples, calibration.wet_raw)):
        if samples is None:
            shifts.append(None)
            flags.add("reference_incomplete")
            continue
        summary = summarise(samples, limits)
        bad = set(summary.flags) - {"outliers_rejected"}
        if bad:
            shifts.append(None)
            flags.add("reference_unreliable")
            continue
        shift = summary.raw - baseline
        shifts.append(shift)
        if abs(shift) > limits.drift_counts:
            flags.add("drift")
    return ReferenceCheck(*shifts, tuple(sorted(flags)))


def calibrate(samples, calibration, *, limits=Limits(), reference=None,
              challenge_history=None):
    """Map one settled batch to 0..100 and return quality warnings alongside it."""
    summary = summarise(samples, limits)
    flags = set(summary.flags)
    if reference is None:
        flags.add("drift_unchecked")
    else:
        flags.update(reference.flags)
    if challenge_history is not None:
        flags.update(check_stuck(challenge_history, limits))

    moisture = None
    confidence = 0.0
    faults = {"invalid_reading", "out_of_range", "adc_rail", "insufficient_samples", "stuck"}
    if not flags.intersection(faults):
        # This works whether the sensor code goes up or down as it gets wetter.
        span = calibration.wet_raw - calibration.dry_raw
        index = 100 * (summary.raw - calibration.dry_raw) / span
        moisture = max(0.0, min(100.0, index))
        if moisture != index:
            flags.add("outside_calibration")
        if abs(span) < 10 * limits.noisy_mad_counts:
            flags.add("weak_calibration")

        # A batch-quality score, not a probability that the moisture is correct.
        confidence = (summary.used / summary.total) / (
            1 + (summary.mad_counts / limits.noisy_mad_counts) ** 2)
        penalties = {"noisy": 0.25, "outside_calibration": 0.5, "drift": 0.5,
                     "drift_unchecked": 0.8, "reference_incomplete": 0.8,
                     "reference_unreliable": 0.0, "weak_calibration": 0.5,
                     "challenge_unreliable": 0.0, "challenge_incomplete": 0.8}
        for flag, factor in penalties.items():
            if flag in flags:
                confidence *= factor
    return SoilReading(moisture, summary.raw, summary.mad_counts, summary.used,
                       summary.rejected, confidence, tuple(sorted(flags)))


def gravimetric_water_pct(wet_mass_g, dry_mass_g):
    """Water mass divided by dry soil mass. Subtract the container mass first."""
    wet = finite_number(wet_mass_g)
    dry = finite_number(dry_mass_g)
    if wet is None or dry is None or dry <= 0 or wet < dry:
        raise ValueError("need finite masses with wet >= dry > 0")
    # Organic soils can hold more water than their dry mass, so do not clamp this.
    return 100 * (wet - dry) / dry
