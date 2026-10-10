# The build plan

I'm starting with the software while I choose the parts. This is the order I
want to build and test the rover in. Each step needs a recorded pass before
the next one starts.

## The first software step

**S0: Make and inspect a simulated run on the laptop. Passed on 9 October 2026.**

Run `python -m simulation.simulate_run`, then the verification command it prints. The
pass is 300 valid rows with the agreed 11 columns, timestamps 100 ms apart,
metadata marked as simulation, and a photos folder with no photographs.

I ran the simulation and the checker myself. It passed with 300 valid rows,
11 columns and timestamps 100 ms apart. I also displayed the header and the
first two readings at 100 and 200 ms and shared them for review. The metadata
is marked as simulation and the photos folder is present and empty.

This passes the first software step. The hardware tests still need the parts.

## The next planning step

**S1: Choose three repeatable garden observation spots. Pending.**

[The general trial procedure](garden_trial.md) describes how to choose
anonymous observation spots and repeatable camera positions. This planning
step needs no code or wiring; the spots have not been selected or tested yet.

Pass when the same subjects and positions can be found on a second visit,
with an accessible route and a sampling place accepted by the gardener.
Revise any spot that is ambiguous or would disturb plants. The
soil probe will be placed by hand. A rover grass test is still required.

## The hardware steps

These are planned tests. None have passed yet.

| Step | What I will build | What counts as a pass |
| --- | --- | --- |
| 0 | Set up Raspberry Pi OS Lite, WiFi, SSH and UART with the serial console disabled | SSH into the Pi from the laptop |
| 1 | Make a small PlatformIO project for the exact ESP32 board | See an increasing counter over USB serial |
| 2 | Connect the motor driver and test each motor at three PWM levels | Both wheels turn forwards and backwards as commanded; record any direction correction |
| 3 | Count encoder pulses with interrupts | Several full turns by hand give a consistent count per wheel revolution; record both counts |
| 4 | Control wheel speed with PID and test straight driving | Drive 2 m on a flat floor within 10 cm of the marked line, three runs in a row; save gains and results |
| 5 | Read the IMU, temperature, humidity and raw soil value | Motion readings respond to tilting/turning; humidity responds to a breath; soil readings differ sensibly between dry and wet references |
| 6 | Send telemetry and commands over UART; save it on the Pi | One 30 s run makes a clean CSV with no malformed rows; drive commands and STOP work |
| 7 | Take timestamped C920 photos on the Pi | 20 consecutive photos at the chosen resolution, with correct filenames and no motion blur; stop and settle before every shot |
| 8 | Combine driving, logging and photos in one script | Five drive-2-m, stop, photo and logging cycles run unattended on the flat test surface; one folder contains all CSV, metadata and photos |

The sensor test will keep the soil probe's electronics and connector dry.
Only the sensing section goes into soil or a suitable wet reference. The
combined driving test will not include automatic soil insertion.
Soil readings without valid soil contact must stay missing; the unattended
floor test logs motion and air conditions. Manual garden sampling is a
separate attended visit, not an automatic capability of Prototype 1.

## Measurements to keep

Before using encoder counts as distance or speed, measure each wheel's
ticks per revolution and effective radius. Measure the distance between
the wheel contact centres too. Record gyro bias, the soil reference
readings and the PID gains when those steps are tested.

For every real run, record the surface, battery type and observations in
`meta.json`. For the straight-line test, keep all three distances and
sideways errors. Unmeasured values stay `null`.

## Collecting garden data

Once the sensors and logger work, I can use a few fixed spots in the garden
and return to them on different days. Use simple spot IDs such as `bed_a`
and `pot_1`, the same probe depth, and a similar camera position each time.
Record the time, watering and anything else that changed in the run notes.

The small 2WD chassis will first be tested on dry, firm, fairly level paths.
Soil measurements can also be taken while it is stationary or carried to a
spot. Rough ground and wet weather need separate mechanical tests.

Raw readings alone will not tell me whether a plant needs water. Repeated
measurements with calibration and notes are the starting point. If I later
train an image model, I will need consistent photos and useful labels.

## Prototype 1 finished

All hardware steps pass, the code and a checked wiring diagram are on
GitHub, and there is a two-minute demo video. I can explain what PID does
and what a Kalman filter could add in the next phase.

The source, plans and simulated sample are public. There is no finished wiring
diagram, physical build, demo video or trained AI model yet.

## Ideas after Prototype 1

[The camera and later attachment notes](later_prototypes.md) record optional
video, automatic probe placement and possible physical soil collection.
These are future design ideas. Prototype 1 keeps its photo capture milestone
and manually placed soil probe. Dry/damp/wet labels need checked calibration;
puddles and soil health need their own evidence. S1 remains the current step.

[The prototype roadmap](prototype_roadmap.md) gives the full proposed
progression through a small fleet and wider pilot. [The dataset plan](dataset_plan.md)
records the collection examples and how model improvement will be measured.
These documents are an overview; the next build step still waits for its pass.
