# Watering advisor plan

Status: planned and untested on hardware. Checks and examples are SIMULATED
DATA only. No hardware milestone has passed. This gives me suggestions to
inspect a bed; it doesn't control a pump or diagnose plants. The telemetry
data contract, run metadata versions and T/D/STOP stay unchanged.

## Research and the starting water balance

FAO-56 balances rainfall and irrigation against crop evapotranspiration and
drainage. Available root-zone water depends on field capacity, wilting point
and rooting depth; readily available water is a fraction of that storage.
My one-bucket model omits capillary rise, layered roots, explicit runoff and
the dual crop coefficient. It is not validated for this garden.
[FAO-56 chapter 8](https://www.fao.org/4/x0490e/x0490e0e.htm)

```text
TAW_mm = 1000 * (theta_field_capacity - theta_wilting_point) * root_depth_m
RAW_mm = p * TAW_mm
ET_crop_mm = Kc * ET0_mm
```

These references cover vegetables commonly grown in the UK, not measured
UK garden thresholds. Mid-season Kc assumes a non-stressed, well-managed
crop. Stage, canopy cover and wetting frequency matter. Table p values are
approximately for crop ET of 5 mm/day.
[Kc table 12](https://www.fao.org/4/X0490E/x0490e0b.htm),
[p table 22](https://www.fao.org/4/x0490e/x0490e0e.htm)

| Crop | Mid-season Kc | Reference p |
| --- | --- | --- |
| Lettuce | 1.00 | 0.30 |
| Cabbage / broccoli | 1.05 | 0.45 |
| Carrot | 1.05 | 0.35 |
| Tomato | 1.15 | 0.40 |
| Potato | 1.15 | 0.35 |
| Courgette | 0.95 | 0.50 |

FAO gives `p_adjusted = p_table + 0.04 * (5 - ET_crop)`, bounded to 0.1–0.8.
This implementation instead uses an explicitly selected, fixed p. It doesn't
pick a crop, stage or root depth automatically. Values for my beds are unknown.
[FAO depletion adjustment](https://www.fao.org/4/x0490e/x0490e0e.htm)

## Temperature-only daily evapotranspiration

Hargreaves needs daily minimum/maximum air temperature, date and approximate
latitude. The code calculates extraterrestrial radiation from solar geometry
and converts MJ/m²/day to equivalent mm/day using 0.408. Humidity isn't an
input to this equation. Temperature and humidity alone don't provide measured
sunlight or wind for full Penman-Monteith. FAO recommends regional comparison
with that method where full weather observations exist.
[FAO meteorological methods, equations 20, 21 and 52](https://www.fao.org/4/x0490e/x0490e07.htm)

```text
Ra_MJ = daily extraterrestrial radiation, from date and latitude
ET0_mm = max(0, 0.0023 * (Tmean + 17.8) * sqrt(Tmax - Tmin) * 0.408 * Ra_MJ)
```

The code requires 75% of scheduled daily air-temperature visits. That is my
coverage proposal, not proof it captured the extremes. One rover visit isn't
a day's minimum and maximum. Shielded air readings need checking. Outdoor
solar geometry doesn't describe indoor grow lights, so winter indoor ET
estimates remain experimental.

## Free weather options checked on 13 October 2026

| Service | Useful forecast | Limits and licence |
| --- | --- | --- |
| Open-Meteo | UK-usable coordinate forecasts include daily rain/precipitation and temperatures | Free endpoint is for non-commercial use, including personal home automation: fewer than 10,000 calls/day, 5,000/hour and 600/minute. Data attribution is CC BY 4.0. A sold product needs its commercial service or a reviewed alternative. [Forecast docs](https://open-meteo.com/en/docs), [terms](https://open-meteo.com/en/terms) |
| MET Norway Locationforecast | Global forecasts include precipitation amounts, temperature and humidity; aggregate non-overlapping intervals | CC BY 4.0 attribution; identify the app, cache responses, obey expiry and avoid unnecessary traffic. More than 20 requests/second across the app needs agreement. No delivery guarantee. [Data model](https://docs.api.met.no/doc/locationforecast/datamodel.html), [terms](https://docs.api.met.no/doc/TermsOfService), [licence](https://docs.api.met.no/doc/License), [CC BY permissions](https://creativecommons.org/licenses/by/4.0/) |

The implementation makes no network requests or stores real coordinates/keys.
It uses an invented forecast stub, including a false rain prediction. Future
rain never enters the observed bucket. A missing rain/irrigation amount is
unknown; zero means a recorded zero. Garden forecast skill and future licence
changes aren't verified. Recheck terms before product release.

Commercial controllers combine configured zones, actual/predicted weather
and safeguards. Hunter documents timed schedules adjusted for weather,
ET, rainfall and optional rain/soil sensors. This doesn't reveal its private
algorithm or prove a water-saving figure for my rover.
[Hunter schedules](https://www.hydrawise.com/features/time-based-predictive-watering),
[triggers and inputs](https://dev.hydrawise.hunterindustries.com/content/smart-controller-specifications)

## Bucket implementation

`BedProfile` holds one anonymous bed ID, approximate latitude, Kc, p, input
efficiencies, capacity and initial storage. Capacity/storage default to
unknown. The fixture's 40 mm capacity and 32 mm starting storage are invented.
ADC endpoints don't establish mm of plant-available water. Reference samples,
root/pot dimensions and measured water inputs are needed before choosing
real values. [Soil-specific calibration method](https://library.metergroup.com/Sales%20and%20Support/METER%20Environment/Website%20Articles/Method_b-_soil_specific_calibrations_for_meter_soil_moisture_sensors.pdf)

Each complete simulated day uses this explicit order:

```text
incoming = rain_mm * rain_efficiency + irrigation_mm * irrigation_efficiency
total = previous_storage_mm + incoming
drainage_mm = max(0, total - capacity_mm)
ET_demand_mm = Kc * ET0_mm
ET_removed_mm = min(total - drainage_mm, ET_demand_mm)
storage_mm = total - drainage_mm - ET_removed_mm
depletion_fraction = 1 - storage_mm / capacity_mm
```

Overflow drains immediately in this day step. Real drainage and event timing
remain unvalidated. Missing weather/irrigation breaks a continuous budget;
later complete days can't silently repair it. Restart an explicit analysis
window with checked initial storage. The sensor never resets the mm bucket.

## Learning provisional limits from earlier drying curves

Each call uses one bed and one calibration. Keep sensors, depths and soil
mixes separate. Automatic mixed-bed routing isn't implemented.

Extension guidance describes sensor readings 12–24 hours after heavy watering
or rain as a practical field-capacity estimate. I still need to confirm a
drained plateau, adequate wetting and contact. A lowest observed ADC code
doesn't establish permanent wilting point.
[Soil-sensor irrigation guidance](https://extension.umn.edu/natural-resources/conservation/agricultural-soil-and-water/irrigation/soil-moisture-sensors-for-irrigation-scheduling)

The learner uses only the previous 28 days: at least seven good dry days and
two separate post-wetting cycles. A wet candidate is a day after at least
3 mm recorded wetting, with drying no faster than 1.5 index points/hour.
Its wet end is the median candidate; its dry end is the lower 10th percentile
of observed non-wetting days, requiring an eight-point span. Faulty/drifting
days are excluded. These thresholds are my untested proposals. The dry end
describes the observed experiment range, not a physiological safe limit.

## Decision, confidence and weekly text

The advisor compares bucket depletion with depletion through the provisional
index range. A disagreement above 0.25, score below 0.45, bad readings or
missing limits/weather/storage produce `check_by_finger`.

When both estimates cross p, it suggests `consider_watering`. For moderate
depletion, a next-day forecast of at least 3 mm and probability at least 0.6
changes this to `watch_forecast`. Depletion at or above 0.8 isn't delayed for
forecast rain. Forecasts must be issued before the end-of-day decision,
be at most 36 hours old, have a timezone and refer to tomorrow. Invalid
forecasts are ignored with a reason.

Every result says: "Check by finger at the recorded depth, compare another
spot, and inspect the plant before watering." Evidence scores are capped
at 0.65, or 0.5 with unchecked drift. They aren't measured accuracy. A weekly
line needs five usable days or says "not enough data". No litres, pump
duration or watering commands are generated.

## Soil type, temperature and a planned DS18B20

Soil-specific calibration and installation matter. Research studies
temperature compensation, but I couldn't verify a transferable coefficient
for my exact cheap v1.2 circuit.
[Low-cost calibration study](https://www.mdpi.com/1424-8220/26/11/3291),
[temperature study](https://www.sciencedirect.com/science/article/pii/S0378377416304206)

My proposed test uses each soil mix at several weighed wetness levels and
temperatures, with repeat insertions and held-out samples. Only then consider
`raw_corrected = raw - beta * (soil_temperature - reference_temperature)`.
Keep raw readings and calibration IDs. No correction or soil-temperature
telemetry column is implemented here; future values belong in a visit sidecar.

DS18B20 specifies 3.0–5.5 V power, 1-Wire communication and ±0.5 °C accuracy
from -10 to +85 °C. The bare part isn't waterproof; third-party sealed probes
need their own construction check. I propose three-wire 3.3 V power, ground
and data with the datasheet pull-up arrangement, after checking pinout and a
free controller pin. Don't guess from wire colours.
[Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf),
[manufacturer sealing note](https://ez.analog.com/dsp/otherdsp/a/documents/do19739/can-the-ds18b20-be-submerged-in-water)

Proposed mounting: sealed tip beside the moisture sensing zone at recorded
depth, soil contact, a depth stop and strain relief, away from motors/lamp.
Compare with a reference and check settling. No wiring table changes or
measured response time are implied.

## Images, thermal cues and dataset evidence

Keep visible wilting, controlled water withholding and measured water status
as separate labels. Researchers use expert scores and image shape/angle
metrics; similar appearance can have several causes. Keep uncertain labels
and annotator/review records.
[Wilting study](https://plantmethods.biomedcentral.com/counter/pdf/10.1186/s13007-023-01026-w)

Low-cost thermal canopy measurements have been studied against reference
water status. This is a possible later cue: background pixels, air conditions,
illumination and wet/dry reference baselines need control. A useful rover
threshold and cheap-array outdoor performance are unverified. Start with
RGB, weights and checked labels; thermal remains a later experiment.
[Thermal field study](https://www.mdpi.com/2072-4292/12/4/723)

Use plant/experiment IDs, timestamped measurements, methods and units.
MIAPPE provides this structure. [The dataset plan](dataset_plan.md) borrows
it without claiming full compliance. [MIAPPE](https://www.miappe.org/overview/)

## Run the simulated example

```powershell
python3 -m simulation.garden --output-dir runs/watering_sim --weeks 6
python3 -m analysis.weekly_report runs/watering_sim --dry-raw 3000 --wet-raw 1000 --watering-inputs runs/watering_sim/watering_inputs.json --output-dir artifacts/watering_sim
python3 -m analysis.check
```

Use new output folders. `watering_inputs.json` is a separate SIMULATED
artifact. The fixture still has invented daily recharge, not physical crop
simulation; its curve can disagree with the bucket. Tests also use consistent
fake dry-downs to exercise advice branches. Injected-fault labels aren't used
as evidence. Reboots retain separate-run handling.

Some full-paper pages blocked direct reading; indexed primary abstracts and
available documents supplied general findings, not an exact correction curve.
Bed hydraulics, Kc/p, indoor ET, forecast skill, compensation, finger-check
repeatability and useful advice all remain unvalidated.
