# The data needed before more robots help

**Planning only.** No real dataset or model exists. The committed example
is SIMULATED DATA; collection totals below are illustrative targets, not results.

I want to collect data that can answer a defined question. The number of
robots is a way to cover places and visits, not a measure of model quality.
These are proposed collection targets, not established minimum sample sizes.
The actual dataset and model do not exist yet.

## What a unit means

A rover unit is one complete rover. I will also count gardens, distinct
plants or marked groups, visits, photos and reliable labels separately.
Different views of one plant at one visit share the same condition. Visits
on adjacent days can also be closely related. A million telemetry rows do
not create a million independent examples of plant health.

A unit can visit several gardens if the schedule is feasible. A fixed camera
and sensor kit can contribute equivalent records if its collection method
is documented. A soil-only sensor node adds soil readings, not camera images.
Using phones as extra cameras needs their own IDs and capture settings.

## The first useful model task

Start with one narrow appearance question, such as whether visible wilting
is present in a tomato view. Use human-reviewed labels: visible wilting,
no visible wilting, or uncertain. Uncertain records remain useful for review
but are not silently assigned a known label. The appearance label does not
establish the cause, and absence of that symptom does not establish health.

Weekly charts, photo timelines and checked dry/damp/wet ranges can be made
without a learned model. pH, nutrients and biological activity need suitable
measurements to support claims about them. "Dead soil" is not a moisture class.

An exploratory target for a first small model is 500-2,000 carefully labelled
images for one narrow task, preferably involving 20-50 distinct plants and
more than one garden. This is a project planning range, not a promise of
accuracy. One garden can support an educational experiment; claims about
new gardens require separate test gardens. Adapt a suitable existing model
or use its image features before considering training a large model from
scratch. Public data may help after checking its task, licence and conditions.

For a stronger pilot, a planning target is 5,000-20,000 reviewed examples for
the chosen task across several gardens, plants and conditions. Capture may
greatly exceed this. Count examples in each class and their distinct plants,
gardens and episodes; a total dominated by routine views can miss the condition
the model is supposed to recognise. There is no image count that establishes
general plant diagnosis.

## How many observations a schedule produces

Let G be gardens, P be subjects per garden, V be visits per subject per day,
D be days, and K be photographs per visit. For a uniform completed schedule:

```text
plant visits = G * P * V * D
photographs  = G * P * V * D * K
```

The examples below use one unit per garden, one daily visit, two photographs
per visit and no missing visits. They show potential capture, not independent
training examples. Real totals will be lower when visits fail or photos are
rejected, and only some records may have usable labels.

| Example | Distinct gardens | Subjects per garden | Days | Plant visits | Photos |
| --- | --- | --- | --- | --- | --- |
| One unit | 1 | 10 | 60 | 600 | 1,200 |
| Five units | 5 | 15 | 90 | 6,750 | 13,500 |
| 20 units | 20 | 20 | 180 | 72,000 | 144,000 |

If a pilot captures 13,500 photos and 80% pass the image checks, 10,800 remain.
If only half of those have suitable reviewed labels, that leaves 5,400 labelled
photos. These percentages are examples, not measured rates. Several photos
can still describe the same plant and episode.

At the planned 10 Hz, ten minutes of telemetry gives 6,000 rows. Repeating
that run for 60 days gives 360,000 rows from one rover. For ten daily plant
visits over those days, there are still only 600 plant visits. Repeated sensor
values in a log do not add new reference conditions.

## The records each plant visit needs

The existing 11-column telemetry file stays as agreed. The private visit and
label manifest below links separate evidence to it. Dataset format version 1
is a new artifact, not a telemetry or T/D/STOP change. Its tooling is tested
only with SIMULATED records and generated pixels.

| Record | Why it matters |
| --- | --- |
| Device ID, hardware/firmware version and calibration ID | Trace changes between collection systems |
| Anonymous garden ID, spot ID and plant/group ID | Keep repeated observations and dataset splits attached to their source |
| Plant type, variety and growth stage where known | Interpret appearance and document what the dataset covers |
| UTC visit time and valid controller sampling interval | Connect photo and sensor observations |
| Photo filenames, resolution, camera position and settings | Reproduce and compare views |
| Raw soil value, probe depth, placement validity and reference method | Keep measurements separate from an assumed moisture label |
| Air readings, sun/shade note and relevant sensor exposure | Describe the collection conditions |
| Watering, rain, compost/feed and care notes | Record events that may accompany changes; unknown amounts stay unknown |
| Human appearance label, source, review status and uncertainty | Identify what the training target actually means |
| Confirmed test result, sample ID, depth, time and method when available | Connect stronger evidence to a soil or plant claim |
| Model version, prediction and uncertainty in a separate record | Compare predictions with evidence without treating them as truth |

Keep the original readings and record labels separately. Labels generated
by the current model need a prediction marker, not an automatic promotion
to human-confirmed truth. Simulation records remain excluded from real
garden training and evaluation datasets unless a separate synthetic-data
experiment explicitly documents their use.

## Measurement units

Robot units and measurement units are different things. These are the
measurement conventions for the current schema and possible later tests.

| Quantity | Unit or convention |
| --- | --- |
| Visit and photo time | UTC with timezone; Unix seconds where used in filenames |
| controller elapsed time | Milliseconds since boot, linked to a UTC anchor |
| Wheel command and gyro Z | Radians per second, rad/s |
| Raw encoders | Cumulative pulse counts; this single-channel hardware does not measure direction independently |
| Accelerometer readings | Metres per second squared, m/s^2, including gravity |
| Soil raw | 12-bit ADC counts, 0-4095; not moisture percent |
| Air temperature | Degrees Celsius |
| Air humidity | Percent relative humidity; not soil water content |
| Probe depth and measured camera position | Millimetres or metres, explicitly named in the record |
| Later measured water content | Specify gravimetric kg/kg or volumetric m^3/m^3; if expressed as percent, preserve which definition and reference method |
| Later pH | Unitless logarithmic quantity, with the test method recorded |
| Later nutrients | Preserve the laboratory's reported unit, such as mg/kg dry soil, and extraction method; do not merge incompatible methods automatically |

See [the existing data contract](data_contract.md) for the exact CSV fields.
New sensors and derived values get a documented schema/version when they
are implemented. ADC readings are not converted into chemistry measurements.

## Calibrating and labelling soil conditions

Check the actual probe and soil using several reference conditions and
repeated placements. Record depth, contact and reference method. A burst of
100 readings from the same placement is useful for noise measurement, but
it is still one placement rather than 100 independent wet/dry conditions.
Agree boundaries and acceptable error from the reference experiment before
using moisture labels. Replacement sensors need comparison and calibration.

Record puddles as a separate surface observation. A wet probe reading alone
does not establish standing water. A soil health question needs the relevant
physical, chemical or biological evidence; a moisture category is not enough.

## How to know whether more data improves the model

Split the dataset according to the claim. For new gardens, keep whole gardens
outside training and tuning. For future visits to a known garden, hold out
later time periods and keep adjacent observations together. Keep all views,
crops and augmentations of one visit in its group. Use a recorded split before
tuning, including normalisation and other data-dependent preparation.

Measure missed events, false alerts, precision, recall and review workload.
Report the actual evaluation counts, uncertainty and coverage by class,
garden, plant and condition. Choose acceptable rates for the specific task
before the final test. A model that flags nothing must not pass just because
most routine visits have no visible symptom.

Train on increasing group-selected amounts of data and plot validation
performance against the amount used. This learning curve helps show whether
more similar data helps. If the errors concentrate on shaded views or a new
plant type, collect those examples. If labels or framing are wrong, fix them
before buying more rovers. A model architecture or input may also limit the
result; more data is not guaranteed to solve every failure.

[Scikit-learn's grouped and time-based evaluation guidance](https://scikit-learn.org/stable/modules/cross_validation.html)
explains keeping dependent groups apart. Its
[learning-curve guidance](https://scikit-learn.org/stable/modules/learning_curve.html)
explains measuring the benefit of additional training samples.

In one published plant-disease study, 54,306 controlled leaf images produced
99.35% accuracy on its held-out dataset but 31.4% on images from different
conditions. That is evidence about that study, not a benchmark or dataset-size
requirement for this rover. It illustrates why garden diversity and realistic
evaluation matter. See
[Mohanty, Hughes and Salathe, 2016](https://arxiv.org/abs/1604.03169).

## Private dataset schema and folder plan

Status: planned/untested. No real collection or hardware milestone has passed.
Everything generated by the tests is SIMULATED. Measured observations, when
collection starts, must be marked `observation`, not relabelled as simulation.
Do not mix those sources in one training/evaluation dataset.

This smaller schema borrows MIAPPE's distinction between biological material,
experiment, observed variable, method and unit. It isn't full MIAPPE compliance.
[MIAPPE overview](https://www.miappe.org/overview/),
[MIAPPE 1.1 specification paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7317793/)

```text
data/private/datasets/pilot_private/       # all ignored, including JSON and CSV
  dataset.json                           # declaration below
  manifest.jsonl                         # one photo observation per line
  experiments.csv                        # cultivar, soil mix, treatment, lamp schedule
  cameras.csv                            # camera ID, model, settings, ruler checks
  soil_samples.csv                       # tare/wet/dry masses and sample method
  measurements.csv                       # timestamped weights, inputs, sensor batches
  raw/                                   # anonymous image names; private originals
  processed/                             # optional private copies only
  sanitized/                             # new output created by the script
    dataset.json
    manifest.jsonl
    processed/                           # fresh metadata-free PNG copies
```

The whole `data/private/` tree and photo formats are gitignored. I still check
`git status` before commits; an ignore rule can be overridden manually. Never
force-add photographs, records, contact details or exact locations. Camera IDs
are pseudonyms, not phone serial numbers; annotator IDs are pseudonyms, not
names/emails. The exporter doesn't upload anything or copy the reference CSVs.
Keep those private references and backups locally; don't publish an export
without a separate review.

`dataset.json` uses exactly these fields. This example is SIMULATED, not a
real dataset declaration:

```json
{
  "dataset_format_version": 1,
  "dataset_id": "dataset_sim",
  "data_source": "simulation",
  "status": "planned_untested",
  "notice": "SIMULATED DATA ONLY. Invented records and generated pixels.",
  "split_policy": "plant_and_date"
}
```

All manifest keys are required, with `null` for unknown measurements. The
script rejects unknown keys, duplicate IDs, non-finite values and unsafe paths.
It doesn't prove that a human measurement or label is correct.

| Fields | Meaning / units |
| --- | --- |
| `image_id`, `visit_id`, `experiment_id`, `plant_id`, `bed_id` | Anonymous IDs. Keep one plant's identity through every view, date and dry-down episode. |
| `camera_id`, `image_path`, `view`, `distance_mm` | Camera reference, relative `raw/` or `processed/` path, wide/mid/close and measured lens-to-subject distance in mm. |
| `data_source` | `simulation` or `observation`, matching the declaration. |
| `captured_at_utc`, `sensor_at_utc` | Explicit UTC ISO timestamps. Sensor evidence uses its own time, within a proposed five-minute join window. |
| `soil_raw`, `soil_moisture_index`, `moisture_basis`, `calibration_id` | Integer 0–4095, relative 0–100 index, literal `relative_index`, and calibration ID. An index needs raw evidence and its calibration. |
| `soil_gwc_pct`, `soil_sample_id` | Optional measured gravimetric water % (water mass / dry soil mass) and reference sample ID. Organic material can exceed 100%; don't clamp it. |
| `soil_temp_c`, `air_temp_c`, `humidity_pct` | Separate soil/air temperatures in °C and air % RH; null if unmeasured. Soil temperature is a sidecar value, not a new telemetry column. |
| `pot_mass_g`, `water_added_g`, `depth_mm`, `contact` | Whole-pot mass, recorded water addition in g, insertion depth in mm, and good/uncertain/unknown contact. Unknown water isn't zero. |
| `weather` | Source, observed time/rain mm, forecast issue time/rain mm. Keep forecasts separate from observations; no coordinates. |
| `labels`, `annotator_id` | Separate appearance, treatment/status, cause, confidence, review flag and pseudonymous reviewer ID. |
| `privacy_reviewed`, `split` | Human scene-review flag; train/validation/test/unassigned. Unassigned is collection-only. |

Weather uses exactly `source`, `observed_at_utc`, `rain_mm`,
`forecast_issued_at_utc`, `forecast_rain_mm`. Sources are unknown/simulation/
manual/open_meteo/met_norway. Known amounts need timestamps. Forecasts issued
after capture can't be evidence available at that capture. Source freshness
and garden-level weather accuracy still need review.

Labels use exactly `visible_wilting`, `water_status`, `cause`, `confidence`,
`reviewed`. The proposed visual rubric is none/mild/clear/severe/uncertain.
Water status is well_watered_control/dry_down/rewatered/unknown. Cause is
unknown or controlled_withholding; withholding is an experimental treatment,
not proof it caused every symptom. Confidence is low/medium/high. A second
reviewer should score a blinded subset and disagreements stay recorded.

For a binary wilting experiment, use reviewed none/clear examples and hold
mild/severe/uncertain records for the agreed task protocol; don't quietly
turn uncertainty into a healthy label. The validator checks format and split
integrity, not which labels belong in a future training task.
[Expert wilting-score study](https://plantmethods.biomedcentral.com/counter/pdf/10.1186/s13007-023-01026-w)

A complete SIMULATED manifest-line template (the named image must exist
locally before validation):

```json
{
  "image_id": "image_sim_1", "visit_id": "visit_sim_1",
  "experiment_id": "experiment_sim", "plant_id": "plant_sim", "bed_id": "bed_sim",
  "camera_id": "camera_sim", "image_path": "raw/image_sim_1.jpg",
  "data_source": "simulation", "view": "mid", "distance_mm": 400,
  "captured_at_utc": "2026-10-13T12:00:00+00:00",
  "sensor_at_utc": "2026-10-13T11:59:30+00:00",
  "soil_raw": 1800, "soil_moisture_index": 60, "moisture_basis": "relative_index",
  "soil_gwc_pct": null, "soil_sample_id": null,
  "soil_temp_c": null, "air_temp_c": 20, "humidity_pct": 60,
  "pot_mass_g": 1000, "water_added_g": null, "calibration_id": "calibration_sim",
  "depth_mm": 70, "contact": "good",
  "weather": {"source": "simulation", "observed_at_utc": "2026-10-13T11:00:00+00:00",
              "rain_mm": 0, "forecast_issued_at_utc": null, "forecast_rain_mm": null},
  "labels": {"visible_wilting": "uncertain", "water_status": "unknown",
             "cause": "unknown", "confidence": "low", "reviewed": false},
  "annotator_id": "annotator_sim", "privacy_reviewed": false, "split": "unassigned"
}
```

Each photo points to its own contemporaneous batch/weight. Don't attach the
latest convenient value to all photos. Keep raw controller times and run ID
in `measurements.csv` so reboots and the UTC join can be audited. For an image
taken between sensor visits, use null when no suitable measurement exists.
The validator checks timing/units but doesn't recompute calibration or audit
the reference CSVs; I must inspect those separately.

## Split by plant and date, never by individual photo

Choose plant cohorts and chronological date blocks before tuning. This
validator's strict `plant_and_date` policy requires:

- A plant ID appears in only one assigned split, across all experiments.
- A visit and an experiment/UTC-date group appear in only one assigned split.
- Train dates precede validation dates, which precede test dates, without overlap.
- Identical decoded pixels can't cross splits even if filenames/metadata differ.

This joint holdout needs both new plants and later dates. For example, train
cohort A in an earlier block, validation cohort B later and test cohort C last.
Photos from the other cohort/date combinations remain unassigned or excluded,
not randomly reassigned. Every crop/view/timelapse frame and later augmentation
inherits its source group. Don't fit calibration, scaling or thresholds on
the held-out data. Adjacent frames aren't independent plant replicates.
[Grouped/time-based evaluation](https://scikit-learn.org/stable/modules/cross_validation.html)

A separate same-plant future-date study answers a different question and
needs a separately reviewed split policy; this script deliberately doesn't
accept it as evidence of generalising to new plants. New-garden claims also
need whole held-out gardens. Automated duplicate checks don't detect every
crop or near-duplicate, so review those manually.

## A: indoor pot dry-down and timelapse protocol

This is my proposed home experiment, not a validated stress protocol.

1. Start with one cultivar and six comparable established pots: three
   watered controls and three gradual dry-down pots. Six is a practical
   starting proposal, not a statistical minimum. Record soil mix, dry soil
   amount, pot/container tare, plant IDs, depth and sensor/calibration IDs.
2. Use a fixed indoor grow-light schedule and camera position over UK winter.
   Record lamp distance/timing and room conditions. Keep heat from the lamp
   away from temperature sensors. Swap/randomise positions with a record to
   investigate shelf effects. Keep a normal dark period suitable for the crop.
3. Wet and drain each pot without standing water, recording water added and
   any collected drainage. Log the drained starting mass and sensor plateau.
   It is a pot/container-capacity candidate, not a measured permanent wilting point.
4. Weigh at the same times daily on a checked scale, recording its resolution
   (proposed 0.1–1 g). Keep the saucer, label and sensor/cable support consistent.
   Weigh water additions separately. Whole-pot loss includes water evaporation,
   transpiration and other mass changes; a plant's growth prevents treating
   every gram over weeks as soil-water loss. Include a matching unplanted pot
   if practical to estimate evaporation, without claiming perfect separation.
5. Photograph at proposed 30–60 minute intervals with fixed exposure/white
   balance where available, plus manual wide/mid/close views at the weighing
   visits. Include a scale and small colour reference. Record capture settings.
6. Reduce water gradually for the dry-down group. Choose an early stop rule
   before starting: mild observed wilting or a conservative measured mass-loss
   limit established in the pilot, then rewater and record recovery. Don't
   chase permanent wilting or plant death to obtain a label. Controls stay watered.
7. Store appearance labels independently from treatment and measurements.
   Repeat with new plants before selecting thresholds. Keep full episodes in
   their split and report the number of distinct plants, not just photos.

These choices borrow time-series/observed-variable structure from
[MIAPPE](https://www.miappe.org/overview/) and separate expert appearance
scores from treatment as in the [wilting study](https://plantmethods.biomedcentral.com/counter/pdf/10.1186/s13007-023-01026-w).
Lighting/reference consistency follows [PlantCV guidance](https://github.com/danforthcenter/plantcv/blob/main/docs/analysis_approach.md).

Low-cost thermal canopy temperature is a possible later comparison against
weights and independently reviewed wilting. Control leaf/background pixels,
air temperature, illumination and reference conditions. A warm canopy alone
isn't a wilting/cause label, and no useful threshold for this rover is verified.
[Thermal water-status study](https://www.mdpi.com/2072-4292/12/4/723)

## B: weigh soil samples for calibration

Use [the soil calibration procedure](soil_calibration.md): one sensor/soil
mix, six independently prepared wetness levels, consistent packing/depth,
three insertion repeats per level and extra held-out samples. These numbers
are proposals. Give every sample an ID and immediately record tare, wet mass,
sensor batch, soil temperature, known additions and preparation time.

Dry a representative weighed portion to constant mass using a documented
method, subtracting tare from wet and dry masses:

```text
GWC_pct = 100 * (wet_soil_mass_g - dry_soil_mass_g) / dry_soil_mass_g
```

For mineral soil the reference commonly uses about 105 °C; organic material
needs a reviewed lower-temperature method. Use dedicated/lab soil-drying
equipment, not food equipment. If unavailable, leave measured GWC null;
air-dry comparisons aren't oven-dry ground truth. VWC additionally needs
measured bulk density or bulk sample volume.
[Reference method](https://www.extension.arizona.edu/publication/guide-maintaining-and-calibrating-field-installed-soil-and-plant-moisture-sensors),
[METER soil-specific method](https://library.metergroup.com/Sales%20and%20Support/METER%20Environment/Website%20Articles/Method_b-_soil_specific_calibrations_for_meter_soil_moisture_sensors.pdf)

Repeat weighed levels across a few temperatures and sensor replacements;
fit any correction on training references and inspect held-out errors. There
is no verified generic v1.2 temperature/soil correction in this repo.
[Temperature-compensation research](https://www.sciencedirect.com/science/article/pii/S0378377416304206)

## C: phone wide, mid and close captures

Use anonymous camera IDs for each phone and lens. Proposed distances are
60–100 cm wide (whole plant/bed), 35–60 cm mid (one plant/branch), and 20–30 cm
close (leaf detail). Measure lens-to-subject distance and first check a ruler
for sharpness; the phone may not focus at the close target. Use its normal
colour camera and record any different lens/macro mode. Avoid digital zoom.

At a visit, keep the plant/visit IDs common to all views. Take a consistent
side and top orientation where useful, record a scale/colour card in the same
light, and avoid touching the leaf into a different posture. Shade/lighting
and wind conditions go in the experiment log. Capture sensor batches/weights
within the proposed five-minute join window; unknown evidence stays null.
Turn off location tagging where possible and still sanitize the exported
copies. Review scenes for faces, doors, labels and identifiable surroundings.
[PlantCV image-layout guidance](https://github.com/danforthcenter/plantcv/blob/main/docs/analysis_approach.md)

## Tooling, metadata removal and limitations

```powershell
python3 -m pip install -r analysis/dataset_requirements.txt
python3 -m analysis.dataset data/private/datasets/pilot_private
python3 -m analysis.dataset data/private/datasets/pilot_private --sanitize
python3 -m analysis.check
```

Watering/daily maths remain standard-library Python. Photo tooling and its
SIMULATED tests use Pillow. Supported input photos are single-frame JPEG,
PNG and WebP in supported colour modes. HEIC, RAW, video and animation aren't
supported; convert a reviewed private copy first. No real photo is processed
by the tests.

Validation checks the manifest, units, UTC joins, source labels, file paths,
readability, duplicates and split leakage. Raw embedded metadata is a warning;
processed embedded metadata is an error. Export requires `privacy_reviewed`
true on every record and creates a new `sanitized/` directory. It won't
overwrite an existing export or change originals.

The exporter applies EXIF orientation, converts valid embedded ICC profiles
to sRGB, renders fresh RGB pixels and saves PNG without copying EXIF, GPS,
XMP, IPTC, comments or thumbnails. Untagged input is assumed sRGB; colour
measurement under that assumption is unvalidated. Transparent pixels are
composited on white rather than exposing hidden colours. Invalid profiles
fail the export. The timestamp and sensor evidence remain in the private
manifest. PNG saves decoded pixels without another JPEG encoding, but
original JPEG compression can't be undone. A failed partial export is marked
`INCOMPLETE` and must not be used.
[Pillow orientation](https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.exif_transpose),
[colour conversion](https://pillow.readthedocs.io/en/stable/reference/ImageCms.html),
[image save API](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save)

This removes embedded photo metadata, not visible personal information or
all possible hidden pixel content. I must review the scene and manifest before
sharing. The tool doesn't upload, train, annotate or confirm a plant condition.
Reference CSV correctness, image near-duplicates, consent, clock accuracy,
calibration and experimental validity still need a human check.

## Proposed timeline from now to P3

These dates are planning slots from 13 October 2026, not passed milestones
or promised completion dates. Phone/pot collection can start separately from
rover assembly. Hardware dependencies can move every later slot.

| Slot | Planned work | Evidence to review before moving on |
| --- | --- | --- |
| October–November 2026 | P1 board/power/UART bring-up remains pending. Set up private records, scale checks, camera/ruler trials and soil references. | Repeatable timestamped records and raw ADC checks; no automatic watering. |
| December 2026–February 2027 | Indoor grow-light pots, watered controls, mild dry-down/recovery episodes and timelapse. Finish P1 checks when hardware allows. | Independent plants/episodes, lamp conditions, weighed references and honest uncertain labels. |
| March–April 2027 | P2 repeated stopped visits/camera comparisons, held-out plant cohorts and outdoor lighting trials when conditions allow. | Review indoor/outdoor differences; don't present indoor accuracy as garden validation. |
| May–July 2027, or later | P3 supervised stationary probe cycles, then supervised route/placement trials after preceding safety tests pass. Add later-date/new-plant garden data. | Placement/contact failures stay labelled; freeze splits and inspect raw evidence before reporting results. |

RHS describes artificial lighting for the UK's short winter days and gradual
hardening-off for indoor-raised plants. Hardening-off doesn't make tender
plants frost-hardy; outdoor transfer depends on the crop and actual conditions.
[RHS indoor lighting](https://www.rhs.org.uk/plants/types/houseplants/artificial-lighting),
[hardening off](https://www.rhs.org.uk/prevention-protection/hardening-off-tender-plants)

Open checks: scale accuracy, actual camera focus/settings, sensor contact,
soil-temperature probe construction, drift/temperature compensation, safe
crop-specific dry-down limits, label agreement and realistic held-out
performance. Some full research pages blocked direct access; no unseen
dataset, private annotation manual or compensation coefficient is claimed.

## Where the work happens

The controller handles real-time motion and sensor reads. The Radxa collects local
files and can later upload them over WiFi. Heavier analysis and model training
happen on the PC or laptop; its available hardware determines what is practical.
A small deployable model could be considered later after performance tests.

Start by reviewing records locally. During a larger pilot, checked uploads
should verify file completeness and keep the local copy until backup is
confirmed. Maintain separate raw data, reviewed labels, dataset versions,
models and evaluation results. Collect only from participating gardens with
clear permission for the intended uses. Anonymous IDs belong in the records;
private garden photos and measurements stay outside the source repository.
