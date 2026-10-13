# SPDX-License-Identifier: MIT
"""Plain template summaries of SIMULATED readings. Hardware and rules untested."""

import argparse
import json
from pathlib import Path
from statistics import mean

from analysis.engine import analyse
from analysis.garden_runs import load_scenario
from analysis.soil_calibration import Calibration


def weekly_summaries(result, *, min_days=5):
    """Seven-day windows from the requested start; never invent missing readings."""
    if isinstance(min_days, bool) or not isinstance(min_days, int) or not 1 <= min_days <= 7:
        raise ValueError("weekly minimum must be 1..7 days")
    reports = []
    days = result["days"]
    for offset in range(0, len(days), 7):
        week = days[offset:offset + 7]
        previous = days[max(0, offset - 7):offset]
        text = ["# Weekly garden summary", "", "SIMULATED DATA ONLY. Planned analysis; untested on hardware.",
                f"Week {len(reports) + 1}: {week[0]['date']} to {week[-1]['date']} (UTC).",
                "Moisture is a relative wetness index, not the percentage of water in soil.", "", "What changed"]
        metrics = (("moisture", "Moisture index", "index points", "index points"),
                   ("temp_c", "Temperature", "°C", "°C"),
                   ("humidity_pct", "Humidity", "% RH", "percentage points"))
        for field, label, unit, change_unit in metrics:
            def usable(group):
                return [day[field]["median"] for day in group
                        if day[field]["median"] is not None
                        and day["coverage"]["soil" if field == "moisture" else field] >= result["thresholds"]["min_day_coverage"]
                        and (field != "moisture" or day["usable_for_trends"])]
            values, old = usable(week), usable(previous)
            if len(values) < min_days:
                text.append(f"- {label}: not enough data ({len(values)}/{min_days} usable days needed).")
            else:
                average = mean(values)
                if len(old) < min_days:
                    text.append(f"- {label}: {average:.1f} {unit}, averaging {len(values)} daily medians; "
                                f"not enough data from last week for a comparison ({len(old)}/{min_days} days).")
                else:
                    change = average - mean(old)
                    comparison = (f"{abs(change):.1f} {change_unit} {'higher' if change > 0 else 'lower'} than last week"
                                  if abs(change) >= 0.05 else "about the same as last week")
                    text.append(f"- {label}: {average:.1f} {unit}; {comparison} "
                                f"({len(values)} versus {len(old)} usable days).")
        rates = [day["drying_pp_per_hour"] for day in week if day["drying_pp_per_hour"] is not None]
        old_rates = [day["drying_pp_per_hour"] for day in previous if day["drying_pp_per_hour"] is not None]
        if len(rates) < min_days:
            text.append(f"- Drying trend: not enough data ({len(rates)}/{min_days} days with usable slopes).")
        else:
            text.append(f"- Drying trend: {mean(rates):.2f} relative-index pp/hour from {len(rates)} daily rates."
                        + (f" Change from last week: {mean(rates)-mean(old_rates):+.2f} pp/hour." if len(old_rates) >= min_days
                           else " Not enough data from last week for a drying comparison."))
        weekly_alerts = [item for item in result["alerts"] if week[0]["date"] <= item["date"] <= week[-1]["date"]]
        text.extend(["", "What to check"])
        if weekly_alerts:
            for item in weekly_alerts:
                text.append(f"- {item['date']}: {item['message']} Confidence: {item['confidence']['level']} "
                            f"({item['confidence']['score']:.2f}; evidence score). {item['limitation']}")
        else:
            text.append("- No rule triggered. That isn't proof that the soil or sensor is healthy.")
        if any(day["notes"] for day in week):
            text.append("- Not enough data for every trend check: some daily baselines, coverage or drying intervals were missing.")
        text.extend(["- Keep the same location, depth and contact; repeat the dry/wet reference checks before trusting a shift.",
                     "- Check power, connectors and raw values if readings are flat, noisy or missing.", "",
                     "These templates don't diagnose plants or decide watering. No hardware milestone has passed."])
        reports.append("\n".join(text) + "\n")
    if not reports:
        reports.append("SIMULATED DATA ONLY. Planned/untested. Not enough data: no daily observations in the requested window.\n")
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario_folder", type=Path)
    parser.add_argument("--dry-raw", type=float, required=True)
    parser.add_argument("--wet-raw", type=float, required=True)
    parser.add_argument("--output-dir", type=Path, help="new directory for analysis.json and weekly text; never overwrite")
    args = parser.parse_args()
    try:
        schedule, observations, boundaries = load_scenario(args.scenario_folder)
        result = analyse(observations, schedule, Calibration(args.dry_raw, args.wet_raw), boundaries=boundaries)
        reports = weekly_summaries(result)
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=False)
            (args.output_dir / "analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            for number, report in enumerate(reports, 1):
                (args.output_dir / f"week_{number:02d}.md").write_text(report, encoding="utf-8")
            print(f"Saved SIMULATED, planned/untested analysis to {args.output_dir}.")
        else:
            print("\n".join(reports))
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
