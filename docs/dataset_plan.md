# the data needed before more robots help

**planning only.** no real dataset or model exists. the committed example
is SIMULATED DATA; collection totals below are illustrative targets, not results.

i want to collect data that can answer a defined question. the number of
robots is a way to cover places and visits, not a measure of model quality.
these are proposed collection targets, not established minimum sample sizes.
the actual dataset and model do not exist yet.

## what a unit means

a rover unit is one complete rover. i will also count gardens, distinct
plants or marked groups, visits, photos and reliable labels separately.
different views of one plant at one visit share the same condition. visits
on adjacent days can also be closely related. a million telemetry rows do
not create a million independent examples of plant health.

a unit can visit several gardens if the schedule is feasible. a fixed camera
and sensor kit can contribute equivalent records if its collection method
is documented. a soil-only sensor node adds soil readings, not camera images.
using phones as extra cameras needs their own IDs and capture settings.

## the first useful model task

start with one narrow appearance question, such as whether visible wilting
is present in a tomato view. use human-reviewed labels: visible wilting,
no visible wilting, or uncertain. uncertain records remain useful for review
but are not silently assigned a known label. the appearance label does not
establish the cause, and absence of that symptom does not establish health.

weekly charts, photo timelines and checked dry/damp/wet ranges can be made
without a learned model. pH, nutrients and biological activity need suitable
measurements to support claims about them. "dead soil" is not a moisture class.

an exploratory target for a first small model is 500-2,000 carefully labelled
images for one narrow task, preferably involving 20-50 distinct plants and
more than one garden. this is a project planning range, not a promise of
accuracy. one garden can support an educational experiment; claims about
new gardens require separate test gardens. adapt a suitable existing model
or use its image features before considering training a large model from
scratch. public data may help after checking its task, licence and conditions.

for a stronger pilot, a planning target is 5,000-20,000 reviewed examples for
the chosen task across several gardens, plants and conditions. capture may
greatly exceed this. count examples in each class and their distinct plants,
gardens and episodes; a total dominated by routine views can miss the condition
the model is supposed to recognise. there is no image count that establishes
general plant diagnosis.

## how many observations a schedule produces

let G be gardens, P be subjects per garden, V be visits per subject per day,
D be days, and K be photographs per visit. for a uniform completed schedule:

```text
plant visits = G * P * V * D
photographs  = G * P * V * D * K
```

the examples below use one unit per garden, one daily visit, two photographs
per visit and no missing visits. they show potential capture, not independent
training examples. real totals will be lower when visits fail or photos are
rejected, and only some records may have usable labels.

| example | distinct gardens | subjects per garden | days | plant visits | photos |
| --- | --- | --- | --- | --- | --- |
| one unit | 1 | 10 | 60 | 600 | 1,200 |
| five units | 5 | 15 | 90 | 6,750 | 13,500 |
| 20 units | 20 | 20 | 180 | 72,000 | 144,000 |

if a pilot captures 13,500 photos and 80% pass the image checks, 10,800 remain.
if only half of those have suitable reviewed labels, that leaves 5,400 labelled
photos. these percentages are examples, not measured rates. several photos
can still describe the same plant and episode.

at the planned 10 Hz, ten minutes of telemetry gives 6,000 rows. repeating
that run for 60 days gives 360,000 rows from one rover. for ten daily plant
visits over those days, there are still only 600 plant visits. repeated sensor
values in a log do not add new reference conditions.

## the records each plant visit needs

the existing 11-column telemetry file stays as agreed. later visit and label
records will link to it; these notes do not implement or change the schema.

| record | why it matters |
| --- | --- |
| device ID, hardware/firmware version and calibration ID | trace changes between collection systems |
| anonymous garden ID, spot ID and plant/group ID | keep repeated observations and dataset splits attached to their source |
| plant type, variety and growth stage where known | interpret appearance and document what the dataset covers |
| UTC visit time and valid ESP32 sampling interval | connect photo and sensor observations |
| photo filenames, resolution, camera position and settings | reproduce and compare views |
| raw soil value, probe depth, placement validity and reference method | keep measurements separate from an assumed moisture label |
| air readings, sun/shade note and relevant sensor exposure | describe the collection conditions |
| watering, rain, compost/feed and care notes | record events that may accompany changes; unknown amounts stay unknown |
| human appearance label, source, review status and uncertainty | identify what the training target actually means |
| confirmed test result, sample ID, depth, time and method when available | connect stronger evidence to a soil or plant claim |
| model version, prediction and uncertainty in a separate record | compare predictions with evidence without treating them as truth |

keep the original readings and record labels separately. labels generated
by the current model need a prediction marker, not an automatic promotion
to human-confirmed truth. simulation records remain excluded from real
garden training and evaluation datasets unless a separate synthetic-data
experiment explicitly documents their use.

## measurement units

robot units and measurement units are different things. these are the
measurement conventions for the current schema and possible later tests.

| quantity | unit or convention |
| --- | --- |
| visit and photo time | UTC with timezone; Unix seconds where used in filenames |
| ESP32 elapsed time | milliseconds since boot, linked to a UTC anchor |
| wheel command and gyro Z | radians per second, rad/s |
| raw encoders | cumulative pulse counts; this single-channel hardware does not measure direction independently |
| accelerometer readings | metres per second squared, m/s^2, including gravity |
| soil raw | 12-bit ADC counts, 0-4095; not moisture percent |
| air temperature | degrees Celsius |
| air humidity | percent relative humidity; not soil water content |
| probe depth and measured camera position | millimetres or metres, explicitly named in the record |
| later measured water content | specify gravimetric kg/kg or volumetric m^3/m^3; if expressed as percent, preserve which definition and reference method |
| later pH | unitless logarithmic quantity, with the test method recorded |
| later nutrients | preserve the laboratory's reported unit, such as mg/kg dry soil, and extraction method; do not merge incompatible methods automatically |

see [the existing data contract](data_contract.md) for the exact CSV fields.
new sensors and derived values get a documented schema/version when they
are implemented. ADC readings are not converted into chemistry measurements.

## calibrating and labelling soil conditions

check the actual probe and soil using several reference conditions and
repeated placements. record depth, contact and reference method. a burst of
100 readings from the same placement is useful for noise measurement, but
it is still one placement rather than 100 independent wet/dry conditions.
agree boundaries and acceptable error from the reference experiment before
using moisture labels. replacement sensors need comparison and calibration.

record puddles as a separate surface observation. a wet probe reading alone
does not establish standing water. a soil health question needs the relevant
physical, chemical or biological evidence; a moisture category is not enough.

## how to know whether more data improves the model

split the dataset according to the claim. for new gardens, keep whole gardens
outside training and tuning. for future visits to a known garden, hold out
later time periods and keep adjacent observations together. keep all views,
crops and augmentations of one visit in its group. use a recorded split before
tuning, including normalisation and other data-dependent preparation.

measure missed events, false alerts, precision, recall and review workload.
report the actual evaluation counts, uncertainty and coverage by class,
garden, plant and condition. choose acceptable rates for the specific task
before the final test. a model that flags nothing must not pass just because
most routine visits have no visible symptom.

train on increasing group-selected amounts of data and plot validation
performance against the amount used. this learning curve helps show whether
more similar data helps. if the errors concentrate on shaded views or a new
plant type, collect those examples. if labels or framing are wrong, fix them
before buying more rovers. a model architecture or input may also limit the
result; more data is not guaranteed to solve every failure.

[scikit-learn's grouped and time-based evaluation guidance](https://scikit-learn.org/stable/modules/cross_validation.html)
explains keeping dependent groups apart. its
[learning-curve guidance](https://scikit-learn.org/stable/modules/learning_curve.html)
explains measuring the benefit of additional training samples.

in one published plant-disease study, 54,306 controlled leaf images produced
99.35% accuracy on its held-out dataset but 31.4% on images from different
conditions. that is evidence about that study, not a benchmark or dataset-size
requirement for this rover. it illustrates why garden diversity and realistic
evaluation matter. see
[Mohanty, Hughes and Salathe, 2016](https://arxiv.org/abs/1604.03169).

## where the work happens

the ESP32 handles real-time motion and sensor reads. the Pi collects local
files and can later upload them over WiFi. heavier analysis and model training
happen on the PC or laptop; its available hardware determines what is practical.
a small deployable model could be considered later after performance tests.

start by reviewing records locally. during a larger pilot, checked uploads
should verify file completeness and keep the local copy until backup is
confirmed. maintain separate raw data, reviewed labels, dataset versions,
models and evaluation results. collect only from participating gardens with
clear permission for the intended uses. anonymous IDs belong in the records;
private garden photos and measurements stay outside the source repository.
