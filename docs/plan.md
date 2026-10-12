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

This passes the first software step. Hardware still needs the parts. The base
Olimex RP2350-PICO2-BB48 is selected at £14.50, not yet bought or tested.
The previous controller orders/ideas are dropped. Counter and serial software
are prepared with computer checks only. [Software preparation](software_prep.md)
gives the instructions. No hardware milestone has passed.

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
| 1 | Build/upload the base BB48 counter with Arduino-Pico | Increasing counter on native USB serial at monitor setting 115200, once a second for 30 seconds |
| 2 | Check seven driver pull-downs before VM, then test motors | STBY/input logic low at boot/reset; wheels lifted, both motors turn forwards/backwards at three PWM levels |
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

**Planned and untested.** Start with Radxa on its own, BB48 header wires and
motor power disconnected. Use the Radxa Debian image for ZERO 3W, record the
image/kernel, power USB-C 1, and use micro-HDMI plus keyboard on USB-C 2 for
first boot only. Set up WiFi/SSH and the UART3-M0 `rsetup` overlay, then reboot.
Those are configuration changes; the inspection checks don't change settings.

| Inspection or future bench check | What I need to record |
| --- | --- |
| Serial device/console use | Actual UART3-M0 device, boot arguments and getty use. `/dev/ttyS3` remains unconfirmed; seeing a file alone doesn't verify pins. |
| Header 5 V | Pins 2/4 relative to GND 6, no external load. Meter in voltage mode, not current across pins. Keep 2/4 disconnected from BB48; voltage alone doesn't prove current allowance. |
| C920 current | Data-capable inline meter on USB-C 2; idle, startup/capture, voltage and failures. Record instrument limits; descriptors aren't measured current. |
| Power bank stay-on | Each output and both together; Radxa idle/capture and BB48 alone on its own USB-C lead. Record duration, lowest load, voltage, reset/shutoff and recovery. No host-handshake workaround is assumed for BB48. |
| Headless WiFi | Normal shutdown, boot without monitor/keyboard, then SSH. Record the method without credentials or network identifiers. |
| BB48 identity | Base version, headers/PCB revision and A2/A4 silicon. Package markings/read-only chip identification against official docs; unknown stays unknown. Don't alter OTP. |
| ADC groundwork | Measure 3V3/analog reference and disconnected sensor output. Later at milestone 5 compare 12-bit batches with motors off/on, settling and 100 nF loading; don't invent a reference or noise result. |

These future read-only commands run **on Radxa**, not Windows:

```sh
ls -l /dev/ttyS*
cat /proc/cmdline
systemctl list-units --all 'serial-getty@*'
lsusb
v4l2-ctl --list-devices
nmcli -t -f DEVICE,TYPE,STATE device status
```

Check commands on the installed image and review output before sharing. Port
is a config setting with no default. Avoid Radxa 8/10 and 27/28. Main route
and fallbacks are in [the untested pin plan](../hardware/wiring.md).

## Later bench check: BB48 USB and Radxa UART

**Planned and untested.** First pass/review the computer USB counter in
milestone 1. BB48 native USB is also the future PC protocol route; UART0
GPIO0/1 is the later Radxa route. Its power path doesn't require a host to
enable target power, but startup and bank stay-on haven't been tested.
See [the power plan](power_plan.md#my-proposed-usb-host-fix).

| Future bench check | What I need to record |
| --- | --- |
| USB counter and identity | Actual COM or `/dev/ttyACM*`, any by-id link, USB identity/current declaration, board and OS. Counter text is not T telemetry. |
| Reset/unplug/BOOT | Whether native USB disappears/re-enumerates, counter restart and port changes. The logger stops on serial errors; don't hide a reboot with automatic reconnect. |
| Crossed UART | Later firmware only: GPIO0 TX to Radxa 3 RX, GPIO1 RX from 5 TX, GND to 6. Verify 3.3 V, UART3-M0 device and 115200 8N1, then real T/D/STOP and reset/run boundaries at milestone 6. |
| Optional host/hub | Only after separate currents are known. BB48 alone on USB-C 2 first, then hub+C920+BB48; record enumeration, sustained capture, current/voltage and errors. Published 500 mA is the limit to plan against, not the 1.45 A protection calculation. |
| Powered hub | Check its supply and upstream back-feed before connecting boards. It can keep BB48 powered when Radxa is off; no automatic motor safety follows. |
| Whole-bank output | Include all downstream loads once; separate BB48 bank output needs its own measurement. Record per-output limits, drop, startup and lowest-load stay-on. |
| Motor-off defaults before VM | Seven 10 kΩ pull-downs at STBY/PWM/direction inputs. Measure logic low during power-up, reset, BOOT and disconnect, with VM disconnected. Check A2 E9 caveat; revise the circuit if needed before motor power. |

The first measurements don't need a hub. No hub is bought or required for
BB48 power. If shared USB current/declarations don't fit, retain separate
controller power/UART rather than assuming a stronger bank changes USB-C 2.
One BB48 supply at a time; external VSYS must not be combined with USB.

On Radxa, future USB inspection commands are:

```sh
lsusb
lsusb -t
lsusb -v
ls -l /dev/ttyACM* /dev/serial/by-id/
```

A stable path doesn't preserve an open handle through disconnect. BOOTSEL's
mass-storage device is for uploading firmware, not logging garden data.
Keep identifiers private. No check here has passed and no sensor data is
generated by this checklist.

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

Later test PIO-based pulse counting, then magnetic A/B quadrature encoders
with a reviewed pin plan and an RP2350 PIO implementation. No STM32-specific
HAL/LL encoder configuration belongs in this controller plan. Pass only when measured turns in both directions
give the expected signed counts and a repeatable load test loses no counted
pulses against a known reference. No such test or hardware exists yet.
