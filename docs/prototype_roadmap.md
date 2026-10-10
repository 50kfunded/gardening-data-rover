# how the prototypes could progress

**planning only.** only the laptop simulation exists. no hardware milestone
has passed; the proposed dates and fleet sizes below are not achieved results.

i want to build one useful rover first, then improve the parts that limit the
garden trial. each prototype is a stage of the project. it does not mean i
need to buy a completely new robot every time.

this is a proposed roadmap, written on 10 October 2026. it assumes roughly
5-8 hours a week for learning and building, with delivery time still to be checked.
the month ranges are elapsed time from starting preparation, not deadlines.
parts availability, weather and failed tests can move them. a stage starts when its
prerequisites pass. collecting another season of data takes calendar time.

S0, the laptop simulation, has passed. S1, choosing three repeatable garden
spots, is pending. no real rover, garden dataset or AI model has passed yet.
the original hardware milestones still happen one at a time.

## the progression

| stage | approximate window | main change | collection scale to investigate |
| --- | --- | --- | --- |
| preparation | now to week 4 | agree the observations, prepare the software and order parts when the buying checks are complete | one laptop; no fabricated readings counted as real training data |
| prototype 1 | months 2-3 | build the instrumented rover: closed-loop driving, sensors, CSV and stopped photos | one rover, one garden, initially three observation spots |
| prototype 2 | months 3-5 | make repeated garden visits useful: consistent photos, calibrated soil observations, visit notes and a dashboard | the same rover, one garden, roughly 8-12 subjects if access and time allow |
| prototype 3 | months 5-8 | test automatic probe placement and more reliable movement along a supervised garden route | one or two rovers visiting two or three consenting gardens |
| prototype 4 | months 8-12 | standardise a small fleet and evaluate one narrow model on gardens it has not learned from | roughly 3-5 rovers serving 5-10 gardens through an agreed visit schedule |
| prototype 5 | months 12-24 | improve reliability and the model using a wider pilot and missing conditions found in testing | roughly 10-20 rovers or equivalent camera/sensor setups; 10-20 or more gardens |

these fleet sizes are collection proposals, not scientific minimums for AI.
one rover can visit several gardens. a fixed camera/sensor setup can also
contribute if it follows the same protocol, but a soil-only sensor node does
not produce photographs. [the dataset plan](dataset_plan.md) separates robot
count, gardens, plants, visits, photographs and reliable labels.

## prototype 1: get trustworthy records

the Pi Zero 2 W and ESP32 control the two motors, read the encoders and
sensors, and save timestamped CSV and C920 photos. the camera milestone starts
with still photos. the soil probe is placed by hand. the first driving tests
are on a flat floor, followed by a separate loaded test on the short grass.

the maths here is wheel motion, encoder sampling and PID. the aim is to hold
a requested wheel speed and understand the measurements used to do it.
AI is not needed for controlling this first rover or saving the readings.

**pass:** all original hardware milestones and their tests pass, the checked
wiring and code are on GitHub, the two-minute demo exists, and i can explain
PID and what a Kalman filter might add. a floor driving pass does not establish
garden navigation. these requirements are still in [the build plan](plan.md).

an initial garden collection target is three spots, one visit per day for
30 days, and one or two views at each visit: 90 plant visits and 90-180 photos
before failures or filtering. this is an extra garden trial, not a change to
the definition of done. use the actual plants present at the time.

## prototype 2: make comparisons across days

the main change is repeatability and context. secure the camera and boards,
check that the chassis works on the chosen route, mark camera positions,
check the Pi clock, and use a consistent probe depth. calibrate the actual
probe in the actual soil. retain raw readings and record which measurements
were valid. housing and power changes depend on the first build's results.

the Pi will show a photo timeline, calibrated moisture trends and weekly
summaries with missing visits visible. watering, rain, compost, plant identity
and visible symptoms are recorded. one or more fixed probes could be added
as references for what happens between rover visits; that is optional extra
hardware with its own calibration.

ordinary Python rules and graphs come first. a first AI experiment can begin
on the PC once useful labels exist: for example, visible wilting in tomato
photos. this remains a learning experiment if it has only seen this garden.
"no visible wilting" does not mean "confirmed healthy". the Pi keeps capturing
and logging; training and heavier analysis happen on the PC or laptop.

**proposed pass:** over 14 scheduled days, at least 90% of planned visits have
usable photos, valid soil observations and their required context; the report
shows gaps and agrees with an inspection of the saved files. a missing or
invalid reading stays marked as missing. for three daily spots, 38 of the
42 visits meet that 90% target. this is a design target, not a measured result.

a practical collection example is ten subjects over 60 days, one visit a day
and two views: 600 plant visits and 1,200 photos before filtering. collecting
more diverse subjects is a later expansion from the first three spots.

## prototype 3: investigate automatic probe placement

the main hardware change is a side-mounted mechanism that reaches over the
edge of the bed and lowers a suitable probe. measure the required reach,
force and stability before selecting the actuator. insertion and withdrawal
must work while stationary before any combined driving sequence is tested.

better encoders, a more suitable chassis or a camera mount may be needed if
the original parts limit the route. a Kalman filter can be investigated for
combining gyro and wheel information into a heading estimate. it will not
make wheel slip disappear or guarantee a repeated camera position. visible
landmarks or other position checks will still need testing.

the route remains supervised and limited to the agreed grass area. automatic
sampling is a separate capability from safely navigating a whole garden.
record probe depth, placement success, obstruction and any manual recovery.
keep the human reference observation separate from the model's prediction.

**proposed pass:** 20 repeated stationary probe cycles complete at the agreed
depth without tipping or damaging the mechanism, and readings meet a tolerance
chosen from the manual-reference repeatability test. then complete ten
supervised route-and-sampling visits to the marked spots. obstruction,
communication-loss and insertion-failure tests must stop motion and report
the failure. the detailed tests are designed when this stage is reached.

one or two rovers can be rotated between two or three consenting gardens.
two gardens, 15 subjects each, 90 daily visits and two views would produce
2,700 plant visits and 5,400 photos if every scheduled visit succeeds.
the schedule must be feasible; robot count does not guarantee daily coverage.

## prototype 4: test the first model beyond this garden

the main change is standardising collection across devices and gardens.
each rover has an ID, a recorded hardware/firmware version and calibration.
camera framing, labels and visit records follow the same protocol. retain
failed visits, missing data and changes of sensors rather than hiding them.

choose one model task. a reviewed flag for visible wilting is a possible
starting point. dry/damp/wet soil categories can continue to use checked
calibration rules. neither becomes a diagnosis of nutrient deficiency or
overall soil health. short video is optional and has its own logging test.

**proposed model pass:** before evaluation, agree acceptable missed-event and
false-alert rates with the intended users. the model must meet those limits
and improve on the declared simple baseline on gardens excluded from both
training and tuning. publish the actual counts, performance by condition and
the amount of abstention or uncertainty. insufficient examples of a target
condition mean its performance remains unestablished. no accuracy target is
claimed as achieved here.

**proposed hardware pass:** the pilot kits meet prototype 2's visit-completeness
target over an agreed four-week trial, including documented recovery from
power or network interruption. any probe attachment must have passed its
own tests. fixed or manually sampled kits can join data collection earlier.

an example collection campaign uses five rovers at five gardens, 15 subjects
per garden, 90 daily visits and two views: 6,750 plant visits and 13,500 photos
before filtering. reserve some whole gardens for testing. an initially small
network needs cautious claims about how widely its results apply.

## prototype 5: use the failures to improve the system

expand only when the small pilot works and another location or condition
will answer a real gap. improve connectors, mounting, protection, calibration
checks and recovery according to observed failures. a larger network also
needs reliable file collection, storage, backups and a practical labelling
workflow. a production version would need separate engineering and cost work.

the model cycle is collect, check, label, train, test, review errors, and collect
the missing examples. use model and dataset versions. keep final test gardens
out of tuning; a new release needs a fresh untouched test set if the previous
one has been used to choose improvements. measure performance by plant type,
weather, camera, season and garden. record uncertainty and review workload.

**proposed pass:** the revised model meets the pilot's agreed useful-error
limits on new gardens and later visits, and the hardware meets the declared
visit and recovery targets over a season appropriate to the intended use.
a claim covering the whole year needs evidence covering the whole year.
the aim is a dependable research pilot, not an assumed finished product.

20 setups in 20 gardens, 20 subjects per garden, 180 daily visits and two
views could capture 72,000 plant visits and 144,000 photos. that is a capacity
example, not a required dataset size or a promise that all photos are usable.
reviewed labels and uncommon events may be the limiting factor.

## a separate branch: collecting physical soil samples

after the stationary probe experiments, investigate whether actual soil
collection answers a question the probe cannot. a scoop or sampling tube
would need reliable collection and release, cleaning, labelled containers,
known depth and suitable laboratory or reference tests. test this on a bench
before adapting a rover; it may need a larger chassis and a separate budget.

this branch can happen beside the data pilot if it is useful. it is not a
prerequisite for photo modelling or calibrated moisture monitoring. see
[the attachment notes](later_prototypes.md) for the distinction between
measuring soil where it is and removing a physical sample.

## the choice for now

i will prepare and build one rover. i do not need to buy a fleet to start
learning or to train a first experimental model. the next action remains S1:
choose the three repeatable subjects and accessible observation positions.
