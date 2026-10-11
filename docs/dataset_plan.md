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

The existing 11-column telemetry file stays as agreed. Later visit and label
records will link to it; these notes do not implement or change the schema.

| Record | Why it matters |
| --- | --- |
| Device ID, hardware/firmware version and calibration ID | Trace changes between collection systems |
| Anonymous garden ID, spot ID and plant/group ID | Keep repeated observations and dataset splits attached to their source |
| Plant type, variety and growth stage where known | Interpret appearance and document what the dataset covers |
| UTC visit time and valid Nucleo sampling interval | Connect photo and sensor observations |
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
| Nucleo elapsed time | Milliseconds since boot, linked to a UTC anchor |
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

## Where the work happens

The Nucleo handles real-time motion and sensor reads. The Radxa collects local
files and can later upload them over WiFi. Heavier analysis and model training
happen on the PC or laptop; its available hardware determines what is practical.
A small deployable model could be considered later after performance tests.

Start by reviewing records locally. During a larger pilot, checked uploads
should verify file completeness and keep the local copy until backup is
confirmed. Maintain separate raw data, reviewed labels, dataset versions,
models and evaluation results. Collect only from participating gardens with
clear permission for the intended uses. Anonymous IDs belong in the records;
private garden photos and measurements stay outside the source repository.
