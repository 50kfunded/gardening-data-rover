# the build plan

im starting with the software while i choose the parts. this is the order i
want to build and test the rover in. each step needs a recorded pass before
the next one starts.

## the first software step

**S0: make and inspect a simulated run on the laptop. passed on 9 October 2026.**

run `python -m simulation.simulate_run`, then the verification command it prints. the
pass is 300 valid rows with the agreed 11 columns, timestamps 100 ms apart,
metadata marked as simulation, and a photos folder with no photographs.

i ran the simulation and the checker myself. it passed with 300 valid rows,
11 columns and timestamps 100 ms apart. i also displayed the header and the
first two readings at 100 and 200 ms and shared them for review. the metadata
is marked as simulation and the photos folder is present and empty.

this passes the first software step. the hardware tests still need the parts.

## the next planning step

**S1: choose three repeatable garden observation spots. pending.**

[the general trial procedure](garden_trial.md) describes how to choose
anonymous observation spots and repeatable camera positions. this planning
step needs no code or wiring; the spots have not been selected or tested yet.

pass when the same subjects and positions can be found on a second visit,
with an accessible route and a sampling place accepted by the gardener.
revise any spot that is ambiguous or would disturb plants. the
soil probe will be placed by hand. a rover grass test is still required.

## the hardware steps

these are planned tests. none have passed yet.

| step | what i will build | what counts as a pass |
| --- | --- | --- |
| 0 | set up Raspberry Pi OS Lite, WiFi, SSH and UART with the serial console disabled | SSH into the Pi from the laptop |
| 1 | make a small PlatformIO project for the exact ESP32 board | see an increasing counter over USB serial |
| 2 | connect the motor driver and test each motor at three PWM levels | both wheels turn forwards and backwards as commanded; record any direction correction |
| 3 | count encoder pulses with interrupts | several full turns by hand give a consistent count per wheel revolution; record both counts |
| 4 | control wheel speed with PID and test straight driving | drive 2 m on a flat floor within 10 cm of the marked line, three runs in a row; save gains and results |
| 5 | read the IMU, temperature, humidity and raw soil value | motion readings respond to tilting/turning; humidity responds to a breath; soil readings differ sensibly between dry and wet references |
| 6 | send telemetry and commands over UART; save it on the Pi | one 30 s run makes a clean CSV with no malformed rows; drive commands and STOP work |
| 7 | take timestamped C920 photos on the Pi | 20 consecutive photos at the chosen resolution, with correct filenames and no motion blur; stop and settle before every shot |
| 8 | combine driving, logging and photos in one script | five drive-2-m, stop, photo and logging cycles run unattended on the flat test surface; one folder contains all CSV, metadata and photos |

the sensor test will keep the soil probe's electronics and connector dry.
only the sensing section goes into soil or a suitable wet reference. the
combined driving test will not include automatic soil insertion.
soil readings without valid soil contact must stay missing; the unattended
floor test logs motion and air conditions. manual garden sampling is a
separate attended visit, not an automatic capability of prototype 1.

## measurements to keep

before using encoder counts as distance or speed, measure each wheel's
ticks per revolution and effective radius. measure the distance between
the wheel contact centres too. record gyro bias, the soil reference
readings and the PID gains when those steps are tested.

for every real run, record the surface, battery type and observations in
`meta.json`. for the straight-line test, keep all three distances and
sideways errors. unmeasured values stay `null`.

## collecting garden data

once the sensors and logger work, i can use a few fixed spots in the garden
and return to them on different days. use simple spot IDs such as `bed_a`
and `pot_1`, the same probe depth, and a similar camera position each time.
record the time, watering and anything else that changed in the run notes.

the small 2WD chassis will first be tested on dry, firm, fairly level paths.
soil measurements can also be taken while it is stationary or carried to a
spot. rough ground and wet weather need separate mechanical tests.

raw readings alone will not tell me whether a plant needs water. repeated
measurements with calibration and notes are the starting point. if i later
train an image model, i will need consistent photos and useful labels.

## prototype 1 finished

all hardware steps pass, the code and a checked wiring diagram are on
GitHub, and there is a two-minute demo video. i can explain what PID does
and what a Kalman filter could add in the next phase.

the repo is private while preparing. there is no finished wiring diagram,
physical build, demo video or trained AI model yet.

## ideas after prototype 1

[the camera and later attachment notes](later_prototypes.md) record optional
video, automatic probe placement and possible physical soil collection.
these are future design ideas. prototype 1 keeps its photo capture milestone
and manually placed soil probe. dry/damp/wet labels need checked calibration;
puddles and soil health need their own evidence. S1 remains the current step.

[the prototype roadmap](prototype_roadmap.md) gives the full proposed
progression through a small fleet and wider pilot. [the dataset plan](dataset_plan.md)
records the collection examples and how model improvement will be measured.
these documents are an overview; the next build step still waits for its pass.
