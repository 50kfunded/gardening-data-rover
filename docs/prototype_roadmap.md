# How the prototypes could progress

**Planning only.** Only the computer simulation exists. No hardware milestone
has passed; the proposed dates and fleet sizes below are not achieved results.

I want to build one useful rover first, then improve the parts that limit the
garden trial. Each prototype is a stage of the project. It does not mean I
need to buy a completely new robot every time.

This is a proposed roadmap, written on 10 October 2026. It assumes roughly
5-8 hours a week for learning and building, with delivery time still to be checked.
The month ranges are elapsed time from starting preparation, not deadlines.
Parts availability, weather and failed tests can move them. A stage starts when its
prerequisites pass. Collecting another season of data takes calendar time.

S0, the computer simulation, has passed. S1, choosing three repeatable garden
spots, is pending. No real rover, garden dataset or AI model has passed yet.
The original hardware milestones still happen one at a time.

## The progression

| Stage | Approximate window | Main change | Collection scale to investigate |
| --- | --- | --- | --- |
| Preparation | Now to week 4 | Agree the observations, prepare the software and order parts when the buying checks are complete | One computer; no fabricated readings counted as real training data |
| Prototype 1 | Months 2-3 | Build the instrumented rover: closed-loop driving, sensors, CSV and stopped photos | One rover, one garden, initially three observation spots |
| Prototype 2 | Months 3-5 | Make repeated garden visits useful: consistent photos, calibrated soil observations, visit notes and a dashboard | The same rover, one garden, roughly 8-12 subjects if access and time allow |
| Prototype 3 | Months 5-8 | Test automatic probe placement and more reliable movement along a supervised garden route | One or two rovers visiting two or three consenting gardens |
| Prototype 4 | Months 8-12 | Standardise a small fleet and evaluate one narrow model on gardens it has not learned from | Roughly 3-5 rovers serving 5-10 gardens through an agreed visit schedule |
| Prototype 5 | Months 12-24 | Improve reliability and the model using a wider pilot and missing conditions found in testing | Roughly 10-20 rovers or equivalent camera/sensor setups; 10-20 or more gardens |

These fleet sizes are collection proposals, not scientific minimums for AI.
One rover can visit several gardens. A fixed camera/sensor setup can also
contribute if it follows the same protocol, but a soil-only sensor node does
not produce photographs. [The dataset plan](dataset_plan.md) separates robot
count, gardens, plants, visits, photographs and reliable labels.

## Prototype 1: get trustworthy records

The Pi Zero 2 W and ESP32 control the two motors, read the encoders and
sensors, and save timestamped CSV and C920 photos. The camera milestone starts
with still photos. The soil probe is placed by hand. The first driving tests
are on a flat floor, followed by a separate loaded test on the short grass.

The maths here is wheel motion, encoder sampling and PID. The aim is to hold
a requested wheel speed and understand the measurements used to do it.
AI is not needed for controlling this first rover or saving the readings.

**Pass:** all original hardware milestones and their tests pass, the checked
wiring and code are on GitHub, the two-minute demo exists, and I can explain
PID and what a Kalman filter might add. A floor driving pass does not establish
garden navigation. These requirements are still in [the build plan](plan.md).

An initial garden collection target is three spots, one visit per day for
30 days, and one or two views at each visit: 90 plant visits and 90-180 photos
before failures or filtering. This is an extra garden trial, not a change to
the definition of done. Use the actual plants present at the time.

## Prototype 2: make comparisons across days

The main change is repeatability and context. Secure the camera and boards,
check that the chassis works on the chosen route, mark camera positions,
check the Pi clock, and use a consistent probe depth. Calibrate the actual
probe in the actual soil. Retain raw readings and record which measurements
were valid. Housing and power changes depend on the first build's results.

The Pi will show a photo timeline, calibrated moisture trends and weekly
summaries with missing visits visible. Watering, rain, compost, plant identity
and visible symptoms are recorded. One or more fixed probes could be added
as references for what happens between rover visits; that is optional extra
hardware with its own calibration.

Ordinary Python rules and graphs come first. A first AI experiment can begin
on the PC once useful labels exist: for example, visible wilting in tomato
photos. This remains a learning experiment if it has only seen this garden.
"No visible wilting" does not mean "confirmed healthy". The Pi keeps capturing
and logging; training and heavier analysis happen on the PC or laptop.

**Proposed pass:** over 14 scheduled days, at least 90% of planned visits have
usable photos, valid soil observations and their required context; the report
shows gaps and agrees with an inspection of the saved files. A missing or
invalid reading stays marked as missing. For three daily spots, 38 of the
42 visits meet that 90% target. This is a design target, not a measured result.

A practical collection example is ten subjects over 60 days, one visit a day
and two views: 600 plant visits and 1,200 photos before filtering. Collecting
more diverse subjects is a later expansion from the first three spots.

## Prototype 3: investigate automatic probe placement

The main hardware change is a side-mounted mechanism that reaches over the
edge of the bed and lowers a suitable probe. Measure the required reach,
force and stability before selecting the actuator. Insertion and withdrawal
must work while stationary before any combined driving sequence is tested.

Better encoders, a more suitable chassis or a camera mount may be needed if
the original parts limit the route. A Kalman filter can be investigated for
combining gyro and wheel information into a heading estimate. It will not
make wheel slip disappear or guarantee a repeated camera position. Visible
landmarks or other position checks will still need testing.

The route remains supervised and limited to the agreed grass area. Automatic
sampling is a separate capability from safely navigating a whole garden.
Record probe depth, placement success, obstruction and any manual recovery.
Keep the human reference observation separate from the model's prediction.

**Proposed pass:** 20 repeated stationary probe cycles complete at the agreed
depth without tipping or damaging the mechanism, and readings meet a tolerance
chosen from the manual-reference repeatability test. Then complete ten
supervised route-and-sampling visits to the marked spots. Obstruction,
communication-loss and insertion-failure tests must stop motion and report
the failure. The detailed tests are designed when this stage is reached.

One or two rovers can be rotated between two or three consenting gardens.
Two gardens, 15 subjects each, 90 daily visits and two views would produce
2,700 plant visits and 5,400 photos if every scheduled visit succeeds.
The schedule must be feasible; robot count does not guarantee daily coverage.

## Prototype 4: test the first model beyond this garden

The main change is standardising collection across devices and gardens.
Each rover has an ID, a recorded hardware/firmware version and calibration.
Camera framing, labels and visit records follow the same protocol. Retain
failed visits, missing data and changes of sensors rather than hiding them.

Choose one model task. A reviewed flag for visible wilting is a possible
starting point. Dry/damp/wet soil categories can continue to use checked
calibration rules. Neither becomes a diagnosis of nutrient deficiency or
overall soil health. Short video is optional and has its own logging test.

**Proposed model pass:** before evaluation, agree acceptable missed-event and
false-alert rates with the intended users. The model must meet those limits
and improve on the declared simple baseline on gardens excluded from both
training and tuning. Publish the actual counts, performance by condition and
the amount of abstention or uncertainty. Insufficient examples of a target
condition mean its performance remains unestablished. No accuracy target is
claimed as achieved here.

**Proposed hardware pass:** the pilot kits meet Prototype 2's visit-completeness
target over an agreed four-week trial, including documented recovery from
power or network interruption. Any probe attachment must have passed its
own tests. Fixed or manually sampled kits can join data collection earlier.

An example collection campaign uses five rovers at five gardens, 15 subjects
per garden, 90 daily visits and two views: 6,750 plant visits and 13,500 photos
before filtering. Reserve some whole gardens for testing. An initially small
network needs cautious claims about how widely its results apply.

## Prototype 5: use the failures to improve the system

Expand only when the small pilot works and another location or condition
will answer a real gap. Improve connectors, mounting, protection, calibration
checks and recovery according to observed failures. A larger network also
needs reliable file collection, storage, backups and a practical labelling
workflow. A production version would need separate engineering and cost work.

The model cycle is collect, check, label, train, test, review errors, and collect
the missing examples. Use model and dataset versions. Keep final test gardens
out of tuning; a new release needs a fresh untouched test set if the previous
one has been used to choose improvements. Measure performance by plant type,
weather, camera, season and garden. Record uncertainty and review workload.

**Proposed pass:** the revised model meets the pilot's agreed useful-error
limits on new gardens and later visits, and the hardware meets the declared
visit and recovery targets over a season appropriate to the intended use.
A claim covering the whole year needs evidence covering the whole year.
The aim is a dependable research pilot, not an assumed finished product.

20 setups in 20 gardens, 20 subjects per garden, 180 daily visits and two
views could capture 72,000 plant visits and 144,000 photos. That is a capacity
example, not a required dataset size or a promise that all photos are usable.
Reviewed labels and uncommon events may be the limiting factor.

## A separate branch: collecting physical soil samples

After the stationary probe experiments, investigate whether actual soil
collection answers a question the probe cannot. A scoop or sampling tube
would need reliable collection and release, cleaning, labelled containers,
known depth and suitable laboratory or reference tests. Test this on a bench
before adapting a rover; it may need a larger chassis and a separate budget.

This branch can happen beside the data pilot if it is useful. It is not a
prerequisite for photo modelling or calibrated moisture monitoring. See
[the attachment notes](later_prototypes.md) for the distinction between
measuring soil where it is and removing a physical sample.

## The choice for now

I will prepare and build one rover. I do not need to buy a fleet to start
learning or to train a first experimental model. The next action remains S1:
choose the three repeatable subjects and accessible observation positions.
