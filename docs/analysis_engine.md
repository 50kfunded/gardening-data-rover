# Weekly analysis plan

Status: tested on SIMULATED DATA only. The rules, thresholds, calibration and
hardware are planned and untested on a real rover. No hardware milestone has
passed. This is arithmetic and template text, with no trained model or plant
diagnosis.

I want to see how the readings changed, which readings look doubtful, and
what I should check next. Missing data stays missing. A relative moisture
index isn't the percentage of water in soil and doesn't decide watering.

## Try it on the computer

Run these from the repository root, without `-I`:

```powershell
python3 -m simulation.garden --output-dir runs/garden_sim --weeks 6 --seed 42
python3 -m analysis.weekly_report runs/garden_sim --dry-raw 3000 --wet-raw 1000 --output-dir artifacts/weekly_sim
python3 -m analysis.check
python3 -m pi.check
python3 -m simulation.check
```

Both output directories must be new. Nothing overwrites an earlier run or
report. On this Windows setup, use the virtual environment's Python 3.12 if
`python3` points to the Store launcher. The commands don't need hardware or
extra analysis packages. Leave off `--output-dir` on the report command to
print the six weekly summaries instead of saving them.

The `3000` and `1000` endpoints above are invented fixture values. They are
required arguments, not calibration defaults to put on a board. Use actual
checked references only after the [soil calibration procedure](soil_calibration.md)
has been tested. The current reader deliberately accepts only simulated runs.

The report directory contains `analysis.json` and `week_01.md`, `week_02.md`,
and so on. Every artifact says SIMULATED and hardware untested. The JSON
keeps daily counts, coverage, raw-quality flags, baselines, EWMA, CUSUM totals,
and alerts so the text can be checked against the numbers.

## What the fake garden does

The default fixture covers six fictional UTC weeks starting on Monday
5 January 2026. It generates immediately, without waiting six weeks.
`--weeks` accepts 1–12 and the seed makes the numeric readings repeatable.
This is one imaginary soil location with one probe and one calibration.

There is one scheduled visit per hour, with nine samples 100 ms apart.
That's a 10 Hz burst at each visit, not continuous weeks of telemetry.
The file grouping is daily; it isn't a claim that a sensor was observed
between visits. Environmental readings change with the fictional hour and
the soil index drops during the made-up daylight period.

Day offsets are zero-based, from the start of the fixture:

| Made-up condition | Default timing |
| --- | --- |
| Rain-like wetting step | Days 3, 10, 17, 28 and 35, from 05:00 UTC |
| Faster drying | Days 14–20: 3.2 rather than 1.2 relative-index pp/hour |
| Wet period | Days 21–23, around 94 relative-index points before drift |
| Slow ADC offset drift | +2 counts per day; not automatically corrected |
| Stuck signal | Days 24–25, exactly 1800 raw counts |
| Noisy signal | Day 26, deliberately wide variation inside each batch |
| Isolated spikes | Day 27, one legal but extreme ADC value per visit |
| Soil dropouts | Day 29, 08:00–15:00; blank soil cells, temperature/humidity kept |
| Missing visits | Day 30, 04:00–09:00 |
| Entire missing day | Day 31 |
| Controller reboot mid-run | Day 32 at 12:00; boot time regresses and a new run part starts |

These are invented patterns, not soil physics, realistic weather, a battery
model or proof that the rules will work in a garden. Shorter fixtures only
include events within their chosen window. Longer ones also split a simulated
32-bit boot-clock rollover if it occurs.

## Files and clocks

The existing 11 telemetry columns, T/D/STOP, empty cells, 256-byte limit,
CSV format version 2 and metadata schema version 2 are unchanged. The
generator writes ordinary labelled run folders with `meta.json`,
`telemetry.csv` and empty `photos/`. It uses the existing reset rule to split
a controller time regression. No boot-time difference is taken across parts.

`meta.json` dates and receive anchors remain computer generation times.
They haven't been redefined as fictional observation dates. A separate
`scenario.json` gives the invented observation window, hourly visit schedule
and first fictional time for each run part. Its `scenario_format_version: 1`
is a simulation-artifact version, not a telemetry or metadata schema change.
`analysis_format_version: 1` similarly versions only the derived report.

The engine maps a row within one part as:

```text
observation_utc = part_first_observation_utc
                  + (row.t_ms - part_first_controller_ms) / 1000 seconds
```

The sidecar's injected-event labels are human-readable test truth. Analysis
never reads them to choose an alert. Tests replace those labels and require
the results to stay identical.

`observations_from_run()` can also use the existing logger receive-time anchor
or S0 start anchor. Those remain estimates with unmeasured clock/latency error.
The CLI uses the explicit simulated sidecar. Real runs are still refused.
Naive dates, unsafe or duplicate run IDs, overlapping visits, out-of-window
rows and an unsplit time/count regression fail instead of being silently
merged. The original `simulation.check` still checks its unchanged 30-second
S0 fixture; it isn't the verifier for these sparse hourly visits.

For each analysis window, I must choose one location and one calibration.
There is no plant ID, location ID or per-sensor reading age in the current
contract. The engine can't safely separate different garden spots or prove
that repeated telemetry contains fresh independent sensor readings. I won't
mix those locations and call the result a trend.

## Batch and daily summaries

For soil, the engine calls the existing `calibrate()` for each short batch.
It uses median/MAD rejection, 12-bit range checks, two-point conversion and
clamping. See [the soil thresholds](soil_calibration.md) and
`analysis/soil_quality.py`. A missing row is represented as a missing sample
inside that batch, rather than replaced by zero.

Noisy batches, values outside the calibration range, weak calibration and
unreliable references are excluded from condition trends. ADC rails and
insufficient samples already give no moisture value. A spike can be rejected
while the remaining batch still contributes, with reduced confidence.

Temperature and humidity use the median of at least five finite samples at
each visit. They remain independent of soil faults. These aren't new sensor
accuracy checks; the shared parser's existing ranges still apply.

For each UTC day and each metric, the report records the mean, median, minimum,
maximum and usable-visit count. Each scheduled visit has one vote, so a long
burst doesn't dominate a day. The summaries describe sampled visits, not a
continuous time-weighted daily average. Coverage is usable visits divided
by expected visits. Missing days are included with `null` summaries.

A soil day enters the condition baseline only with at least 75% coverage
and no suspected stuck sequence. The current hourly fixture needs 18 of
24 usable visits. No gap is filled or interpolated.

## Drying-rate trend

Within a day, use adjacent usable visits from 06:00–18:00 UTC. The pair must
be in the same run part and 0.5–1.5 scheduled intervals apart, so two bursts
close to an hourly slot boundary don't create an exaggerated short-time slope.
Don't bridge a missing visit, a bad batch or a controller boundary.

```text
pair_rate = max(0, earlier_index - later_index) / elapsed_hours
daily_drying_rate = median(pair_rates)
```

A rise greater than two index points is excluded as a wetting jump. It isn't
labelled rain by the engine. At least six usable pairs and a usable soil day
are required; otherwise the rate is `null`. A flat or slightly rising pair
contributes zero. This estimates relative-index change, not actual water loss.

The UTC daylight window is a fixture assumption, not sunrise or a universal
garden rule. It will need checking for the location, season and visit schedule.

## Rolling baseline, EWMA and shift check

The rolling baseline uses earlier usable days within the previous 14 calendar
days. It needs at least seven comparable days, separately for moisture and
drying. It never uses today's value or future data. Bad and missing days
don't become baseline zeros. Earlier condition alerts aren't automatically
deleted; a sustained new level can eventually become the new baseline.

```text
baseline = median(earlier_daily_values)
spread = 1.4826 * median(abs(value - baseline))
```

The minimum alert differences below stop a perfectly repeated simulation's
zero MAD from making tiny changes look important.

EWMA is the displayed moisture trend, with alpha 0.3:

```text
ewma_today = 0.3 * daily_median + 0.7 * ewma_yesterday
```

The first usable day starts at its own median. After a missing or unreliable
soil day, EWMA restarts instead of quietly smoothing across that gap. It
isn't a correction for sensor drift.

The CUSUM-style check uses the current rolling baseline:

```text
residual = daily_median - baseline
up = max(0, previous_up + residual - 3)
down = max(0, previous_down - residual - 3)
```

It reports a shift when the relevant total reaches 20 and at least two
consecutive usable days differ in that direction by more than three points.
The totals then reset. They also reset when the day or baseline is unusable.
The JSON preserves the total that triggered the alert with `reset_after_alert`.
This is a simple accumulated-change rule, not a calibrated statistical test
with a known false-alarm probability. It can't separate drying, probe contact
changes, salinity or sensor drift.

## Starting alert rules

All thresholds below are proposals, tested on invented examples only.

| Alert | Starting rule and limitation |
| --- | --- |
| Dried out faster than usual | Daily rate exceeds the earlier median by `max(0.5 pp/hour, 3 * spread)`. Needs six pairs, 75% daily soil coverage and seven earlier rate days. |
| Unusually wet | Daily median exceeds the earlier median by `max(10 index points, 3 * spread)`. Needs a usable day and seven earlier moisture days. |
| Moisture shift | CUSUM-style total reaches 20, with three-point slack and at least two consecutive changed days. Cause remains unknown. |
| Possibly stuck | 24 consecutive usable visit medians span no more than one raw ADC count. Missing/bad visits clear the sequence. Stable soil or cached readings can match it; confirm with a deliberate dry/wet challenge. |
| Sensor looks noisy | At least three daily visits have the existing `noisy` batch flag. Their soil readings don't enter the condition trend. |
| Data gap | Any missing/unusable scheduled metric, missing sample or incomplete burst. The message separates observed visits, usable metric counts and incomplete batches. A noisy sensor can create a usable-data gap even while rows exist. |
| Controller boundary | Existing split reason indicates a time/count regression. It says the cause may be reboot or rollover, and no drying pair crosses it. |

An equality at a wet/drying threshold doesn't trigger. A tiny `1e-9`
comparison margin avoids floating-point round-off changing that decision.
With too little baseline, coverage or drying data, the daily notes explicitly
say "not enough data" and the corresponding condition alert is withheld.
No alert firing isn't proof that everything is fine.

## Confidence and drift

Every alert includes a score, `low`/`medium`/`high`, `enough_data`, a limitation,
and SIMULATED/planned/untested labels. The score is a rule-evidence indicator,
not a probability that a plant needs water or a measure of sensor accuracy.

For a day, average the existing batch-quality scores and multiply by usable
soil coverage. A suspected stuck day is capped at 0.35 and excluded from
condition trends. Levels are low below 0.45, medium from 0.45 to below 0.75,
and high from 0.75. These boundaries aren't validated.

Wet-alert confidence is capped by both current and earlier-day quality.
Drying alerts are capped at 0.70; shift/noise alerts at 0.65; possible-stuck
alerts at 0.35. Gap and controller-boundary evidence use 0.80 for the known
schedule/split, without claiming the cause is known. A high evidence score
still isn't hardware validation.

Without repeat air/water references, the existing calibrator marks
`drift_unchecked` and reduces quality. A slowly changing soil value alone
doesn't establish drift. The Python API accepts an explicit `ReferenceCheck`
from `check_drift()`; unreliable references withhold condition readings,
and a checked shift reduces quality. Applying one reference to a whole window
assumes it is relevant to that window; dated per-visit reference handling is
not implemented. The CLI deliberately makes no drift correction and has no
automatic reference selection.

## Weekly text

Seven-day windows start from the requested UTC start. Each metric needs at
least five usable daily medians, in both this week and last week, before a
week-to-week comparison is printed. Temperature/humidity can still be
summarised when soil is suspect. The report says how many days were used.
These are averages of daily medians; weekly drying is the mean of usable
daily drying rates. Partial final weeks and the first week are labelled
honestly when a comparison isn't available.

The templates contain "what changed" and "what to check", with confidence
and limitations next to each alert. They suggest checking raw values,
connectors, power, probe contact and repeat references. They don't send a
notification, run a pump, decide watering or infer a plant diagnosis.
Humidity levels are shown as percent relative humidity; their week-to-week
differences are percentage points.

## Tests and what's still open

`python3 -m analysis.check` runs the existing soil tests and the new weekly
tests. The new tests cover clean cycles, rain/fault fixtures, slow drift,
rejected spikes, noise, missing fields/visits/days, ADC rails, reboots,
unchanged formats, prior-only baselines, threshold boundaries, EWMA restart,
up/down shifts, bad settings, unsafe inputs and insufficient weekly data.
Everything is computer-generated and SIMULATED.

Real ADC behaviour, reference drift, soil type/contact/depth, sensor freshness,
visit cadence, clock alignment, thresholds, seasonal baselines and useful
watering limits all remain untested. There is no independent reference
dataset, measured false-alarm rate, validated forecast or product claim.
Run-by-run sensor calibration changes and multiple locations need a separate
review before applying this engine to real observations.

Photo-analysis TODO: later define a checked capture/time/location workflow
and a separate evaluation procedure. No photo-analysis code, image-derived
alert or placeholder result is generated by this engine.
