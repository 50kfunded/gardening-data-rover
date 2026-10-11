# The build plan

I'm starting with the software while I choose the parts. This is the order I
want to build and test the rover in. Each step needs a recorded pass before
the next one starts.

## The first software step

**S0: Make and inspect a simulated run on the computer. Passed on 9 October 2026.**

Run `python -m simulation.simulate_run`, then the verification command it prints. The
pass is 300 valid rows with the agreed 11 columns, timestamps 100 ms apart,
metadata marked as simulation, and a photos folder with no photographs.

I ran the simulation and the checker myself. It passed with 300 valid rows,
11 columns and timestamps 100 ms apart. I also displayed the header and the
first two readings at 100 and 200 ms and shared them for review. The metadata
is marked as simulation and the photos folder is present and empty.

This passes the first software step. The hardware tests still need the parts.
The NUCLEO-G474RE has been ordered, not received or tested. Counter firmware
and serial logging are now prepared, with computer checks only. [Software preparation](software_prep.md) gives the instructions. No
hardware milestone has passed; continue through the hardware steps one at a time.

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
| 0 | Set up the Radxa Debian image for ZERO 3W, WiFi, SSH and the UART3-M0 overlay | SSH into the Radxa from the computer and record the checks below before wiring |
| 1 | Make a small PlatformIO project for NUCLEO-G474RE with Arduino and ST-LINK | See an increasing counter over the ST-LINK virtual COM port at 115200 baud |
| 2 | Connect the motor driver and test each motor at three PWM levels | Both wheels turn forwards and backwards as commanded; record any direction correction |
| 3 | Count encoder pulses with interrupts | Several full turns by hand give a consistent count per wheel revolution; record both counts |
| 4 | Control wheel speed with PID and test straight driving | Drive 2 m on a flat floor within 10 cm of the marked line, three runs in a row; save gains and results |
| 5 | Read the IMU, temperature, humidity and raw soil value | Motion readings respond to tilting/turning; humidity responds to a breath; soil readings differ sensibly between dry and wet references |
| 6 | Send telemetry and commands over UART; save it on the Radxa | One 30 s run makes a clean CSV with no malformed rows; drive commands and STOP work |
| 7 | Take timestamped C920 photos on the Radxa | 20 consecutive photos at the chosen resolution, with correct filenames and no motion blur; stop and settle before every shot |
| 8 | Combine driving, logging and photos in one script | Five drive-2-m, stop, photo and logging cycles run unattended on the flat test surface; one folder contains all CSV, metadata and photos |

The sensor test will keep the soil probe's electronics and connector dry.
Only the sensing section goes into soil or a suitable wet reference. The
combined driving test will not include automatic soil insertion.
Soil readings without valid soil contact must stay missing; the unattended
floor test logs motion and air conditions. Manual garden sampling is a
separate attended visit, not an automatic capability of Prototype 1.

## Milestone 0 checks before wiring

**Planned and untested.** Start with the Radxa on its own. Leave the Nucleo
UART and motor wiring disconnected. Use the Radxa Debian image for ZERO 3W
and record its exact version. For first boot, use power on USB-C 1, a monitor
on micro-HDMI and a keyboard on USB-C 2 through a data adapter.

WiFi, SSH and the UART overlay need setting up first. Enable UART3-M0 through
the `rsetup` overlays, then reboot. These setup actions change configuration;
the checks below only inspect the result. Menu options and headless WiFi
preconfiguration still need checking on the installed image. Do not assume
`before.txt` works. If preconfiguration does not work, use the monitor and
keyboard to set up WiFi and SSH, then check booting without them.

| Read-only check | What I need to record |
| --- | --- |
| Serial device and console use | Confirm which device belongs to UART3-M0. `/dev/ttyS3` is expected but unconfirmed. Inspect the boot arguments and serial getty services; the selected port must not be used by a console or getty. Seeing a device file alone does not prove its pin mapping. |
| Header 5 V | Measure DC voltage at pins 2 and 4 relative to GND pin 6, with no external load connected. Record both values and the supply used. Use the meter's voltage mode, not current mode across the pins. Keep pins 2/4 disconnected from the Nucleo; voltage alone does not establish available current or protection. |
| C920 current | Unplug the keyboard and connect the C920 to USB-C 2 through a data adapter. Use a data-capable inline USB meter to record its current while idle and capturing. Record the meter position and any voltage drops or capture failures. A USB descriptor is not a measured current. |
| Power bank staying on | Check the Nucleo power-source selection against the board revision schematic first. Then test the bank, cables and separate Micro-B lead under idle and camera-capture loads. Record the test duration, current, voltage and any power-off or reset. A bench-supply test does not establish that the bank stays on. |
| Headless WiFi | After a normal shutdown, boot without the monitor or keyboard and SSH in from the computer over WiFi. Record whether it works and how WiFi was configured. Keep network names and credentials out of Git. |

These are future inspection commands to run **on the Radxa**, not in Windows
PowerShell. The serial commands help identify the port and console use:

```sh
ls -l /dev/ttyS*
cat /proc/cmdline
systemctl list-units --all 'serial-getty@*'
```

Once the camera tools are installed, inspect the USB/video devices and network
state without changing settings:

```sh
lsusb
v4l2-ctl --list-devices
nmcli -t -f DEVICE,TYPE,STATE device status
```

Review command output before sharing it. Keep the selected serial port as a
configuration setting in the future logger. Avoid Radxa pins 8/10, the UART2
debug console, and pins 27/28. The main UART3-M0 and fallback wiring is in
[the planned wiring](../hardware/wiring.md). No checks above have passed yet.

## Later bench check: Nucleo on the Radxa host

**Planned and untested.** This is my proposed USB power fix, not a hardware
pass. Start after the Radxa boots reliably and the milestone 1 counter has
been checked on computer USB. Motors stay disconnected. The pin table and
planned UART link stay unchanged. See [the research and open questions](power_plan.md#my-proposed-usb-host-fix).

First try the Nucleo alone on Radxa USB-C 2 using its Micro-B data lead and
the data adapter. Keep the verified default Nucleo power selection. Record
whether ST-LINK enumerates, target power turns on and the counter is visible.
Measure the C920 separately before choosing a hub. The combined setup would
put both devices on the hub, with the Radxa powered through USB-C 1.

| Proposed check | What I need to record |
| --- | --- |
| USB identity and power declarations | Exact OS/kernel, board revision, ST-LINK version, hub model, USB tree, available interfaces and each device's declared power. Check for configuration errors; low measured current alone does not prove enumeration will work. |
| Nucleo VCP | Actual `/dev/ttyACM*` path and any `/dev/serial/by-id/` link. Use the actual path as logger configuration. Check permissions. Do not assume `/dev/ttyACM0` is permanent. |
| USB-C 2 with both devices | Data-capable meter upstream of the hub; idle, startup and simultaneous counter/camera capture current and voltage. Record meter limits. Compare against Radxa's published 500 mA budget, not the load-switch calculation. |
| Hub behaviour | Both devices configure and stay connected during a sustained capture test. Record USB errors, capture failures and counter gaps. For a powered hub, verify its specified supply and check upstream back-feed with boards disconnected before connecting it. Stop if isolation is unclear. |
| Whole bank output | Measure at USB-C 1 with all downstream loads attached. Do not add those loads twice. Record voltage drop, average current, any captured peaks and lowest-load stay-on duration, including any timed mode. |
| Reset and reboot | With motors disconnected, compare the Nucleo target reset, a normal Radxa reboot and a controlled USB unplug. Record target power, ACM/by-id paths and counter restart. An open serial handle may need reopening; the logger currently stops on errors. |
| Power bank recovery | Check idle, capture, normal shutdown and restart. Record whether the chosen output shuts off and whether it restarts. The Radxa keeping a bank awake remains unverified. |

The first measurements can be made without a hub. Borrow one for the combined
bench check if possible. Do not buy a bus-powered hub if the current or
advertised power budget cannot fit; an externally powered bench hub is a
separate option, with its own supply and isolation checks. This is a proposal
based on the [sourced power plan](power_plan.md), not a passed test.

These inspection commands run on the Radxa. They do not flash the Nucleo,
mount a disk or change settings. A missing glob or permission message is a
result to record, not a reason to invent a device name:

```sh
lsusb
lsusb -t
lsusb -v
ls -l /dev/ttyACM* /dev/serial/by-id/
lsblk
```

Review the output before sharing it. Keep device serial IDs and any personal
information out of public notes. The serial logger still needs real T lines
later; milestone 1's counter text is not telemetry and will not pass its
parser. D/STOP and T lines keep the existing contract. No sensor values or
hardware results are generated by this checklist.

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

## Later encoder milestone, separate from Prototype 1

**Planned and untested.** First count the LM393 single pulse signals with
interrupts in milestone 3. Direction comes from the accepted command only as
an assumption; coasting and reversal can break it. Keep raw counts unsigned.

Later test timer-based pulse counting, then magnetic A/B quadrature encoders
with a new pin plan. `HardwareTimer` has no encoder mode; that stage needs
HAL or LL configuration. Pass only when measured turns in both directions
give the expected signed counts and a repeatable load test loses no counted
pulses against a known reference. No such test or hardware exists yet.
