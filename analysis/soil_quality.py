# SPDX-License-Identifier: MIT
"""Planned soil quality checks. Thresholds are untested on real hardware."""

import math
from dataclasses import dataclass
from statistics import median


def finite_number(value):
    """Keep missing values, text and booleans out of the maths."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except OverflowError:
        return None
    return number if math.isfinite(number) else None


@dataclass(frozen=True)
class Limits:
    """Starting thresholds in 12-bit counts, not measured sensor specifications."""

    min_samples: int = 5
    outlier_floor_counts: float = 8.0
    modified_z_limit: float = 3.5
    noisy_mad_counts: float = 20.0
    max_outlier_fraction: float = 0.25
    drift_counts: float = 25.0
    stuck_samples: int = 20
    stuck_span_counts: float = 1.0

    def __post_init__(self):
        for name in ("min_samples", "stuck_samples"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("outlier_floor_counts", "modified_z_limit", "noisy_mad_counts",
                     "drift_counts", "stuck_span_counts"):
            value = finite_number(getattr(self, name))
            if value is None or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        fraction = finite_number(self.max_outlier_fraction)
        if fraction is None or not 0 < fraction < 1:
            raise ValueError("max_outlier_fraction must be between zero and one")


@dataclass(frozen=True)
class SampleSummary:
    raw: float | None
    mad_counts: float | None
    total: int
    used: int
    rejected: int
    flags: tuple[str, ...]


def summarise(samples, limits=Limits()):
    """Filter one settled batch from one place. Never combine different locations."""
    samples = list(samples)
    flags = set()
    valid = []
    for value in samples:
        number = finite_number(value)
        if value is None:
            flags.add("missing_reading")
        elif number is None:
            flags.add("invalid_reading")
        elif not 0 <= number <= 4095:
            flags.add("out_of_range")
        else:
            valid.append(number)

    kept = []
    mad = None
    if valid:
        centre = median(valid)
        mad = median(abs(value - centre) for value in valid)
        # The floor handles repeated ADC codes, where MAD can be zero.
        distance = max(limits.outlier_floor_counts,
                       limits.modified_z_limit * mad / 0.6745)
        kept = [value for value in valid if abs(value - centre) <= distance]
        outliers = len(valid) - len(kept)
        if outliers:
            flags.add("outliers_rejected")
        # Check noise before rejection so filtering cannot hide a bad batch.
        if mad > limits.noisy_mad_counts or outliers / len(valid) > limits.max_outlier_fraction:
            flags.add("noisy")
    if len(kept) < limits.min_samples:
        flags.add("insufficient_samples")
    raw = median(kept) if kept else None
    if raw in (0, 4095):
        flags.add("adc_rail")
    return SampleSummary(raw, mad, len(samples), len(kept), len(samples) - len(kept),
                         tuple(sorted(flags)))


def check_stuck(challenge_history, limits=Limits()):
    """Use a deliberate dry-to-wet challenge, including readings before and after."""
    values = [finite_number(value) for value in challenge_history]
    if any(value is None or not 0 <= value <= 4095 for value in values):
        return ("challenge_unreliable",)
    if len(values) < limits.stuck_samples:
        return ("challenge_incomplete",)
    if max(values) - min(values) <= limits.stuck_span_counts:
        return ("stuck",)
    return ()
