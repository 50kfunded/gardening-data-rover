im building a small ESP32 and Raspberry Pi rover to test driving, sensor logging and timestamped garden photos.

## current status

**only the laptop simulation exists. no hardware has been built.**
the Pi code and ESP32 firmware have not started. none of hardware milestones
1–8 have passed, and Pi setup milestone 0 has not passed either. there is no
working garden rover, camera capture, dashboard, PID controller or AI model yet.

the separate software step, S0, passed on 9 October 2026: Python generated and
checked 300 invented rows. the reorganised one-command check also passes.
these results test files and parsing, not motors, sensors, UART or real timing.

**all example readings and the committed sample are SIMULATED DATA.** they
were invented on a laptop, not collected from a real garden.

## the data format

one run has `meta.json`, `telemetry.csv` and a `photos/` folder.
the shared contract is [shared/data_format.py](shared/data_format.py).

| CSV column | meaning / unit |
| --- | --- |
| `t_ms` | elapsed ESP32 boot time, ms; a virtual clock in the simulation |
| `cmd_left`, `cmd_right` | requested wheel angular speeds, rad/s; not PWM or measured speed |
| `enc_left`, `enc_right` | cumulative raw encoder pulse counts |
| `gyro_z` | body Z angular velocity, rad/s |
| `accel_x`, `accel_y` | body X/Y accelerometer readings, m/s², including gravity |
| `soil_raw` | 12-bit ADC count, 0–4095; not a moisture percentage |
| `temp_c` | air temperature, °C |
| `humidity_pct` | relative humidity, % |

new simulated CSV files start like this. **the numbers below are simulated:**

```csv
# SIMULATED DATA: invented readings; no hardware or real garden measurements.
t_ms,cmd_left,cmd_right,enc_left,enc_right,gyro_z,accel_x,accel_y,soil_raw,temp_c,humidity_pct
100,0.0,0.0,0,0,0.0,0.0062,0.0298,1801,21.0,50.03
```

the notice is followed by the column header and data rows. the reader handles
that notice before reading the CSV. missing optional sensor readings stay
empty, rather than becoming a misleading zero.

metadata includes `run_id, date, surface, battery_type, pid_gains, notes`,
plus schema version, `data_source: simulation`, `csv_format_version: 2`,
timing, command units and calibration. unmeasured calibration and PID gains
are `null`. the sample's date is its generation time, not a garden visit.
simulation photos are empty apart from a text placeholder in the tracked sample.

[the full data contract](docs/data_contract.md) explains the units, planned
UART messages and encoder maths.

## running the simulation

use Python 3.12 from a terminal opened in the repository root. no extra Python
packages or hardware are needed.

the whole pass/fail check is one command:

```powershell
python -m simulation.check
```

it creates and verifies a temporary 30-second simulated run, checks that
damaged files are rejected, then verifies the committed simulated example.
a pass means 300 rows, 11 columns, virtual timestamps 100 ms apart and valid
simulation metadata. it does not pass a hardware milestone.

to keep your own simulated run:

```powershell
python -m simulation.simulate_run
```

this prints the saved folder and the exact `python -m simulation.verify_run ...`
command to copy. normal runs stay in ignored `runs/`. 30 virtual seconds are
generated immediately; this does not measure live performance.

to inspect the small example already in Git:

```powershell
python -m simulation.verify_run data/sample/example_sim
python -m analysis.inspect_run data/sample/example_sim
```

legacy CSV format 1 is supported only when simulation metadata accompanies it.
the checker warns when the standalone simulation notice is absent.

## planned parts

these approximate ranges come from the original brief. **they are unverified
planning estimates, not current shop quotes or a confirmed build cost.**
the original aim is roughly £100, with tools and extras depending on what is available.

| part | approximate allowance |
| --- | --- |
| Raspberry Pi Zero 2 W, WH with soldered header | £16–22 |
| 32 GB A1 microSD | £6–8 |
| micro-USB OTG adapter | £2–3 |
| ESP32 DevKit, ESP32-WROOM-32 | £5–8 |
| 2WD chassis, two 1:48 motors, wheels, caster, encoder discs, 4xAA holder | £10–20 |
| two LM393 speed sensors, if not included | £2–4 |
| TB6612FNG driver module | £3–5 |
| MPU6050 IMU module | £2–4 |
| BME280 module | £3–6 |
| capacitive soil moisture sensor | £2–4 |
| 10,000 mAh USB power bank, at least 2 A output | £10–15 |
| four AA NiMH cells and charger | £10–15 |
| breadboard, jumpers, 100 µF capacitor, velcro and zip ties | £8–12 |
| multimeter, optional | £8–12 |
| Logitech C920 webcam | already owned |

a USB microSD reader, soldering equipment, cables and secure mounting may add
to this. [the parts list](hardware/parts.md) includes buying checks and those
extra allowances. no basket, seller stock or delivery price is confirmed here.

## proposed wiring

**untested: check the actual module labels before connecting power.**

| connection | planned pins |
| --- | --- |
| ESP32 → TB6612 | PWMA 25, AIN1 26, AIN2 27, PWMB 13, BIN1 32, BIN2 33, STBY 4 |
| driver supplies | VCC to ESP32 3V3; VM to AA positive; 100 µF across VM/GND |
| encoders | left DO to GPIO34, right DO to GPIO35; VCC 3V3 |
| shared I2C | SDA GPIO21, SCL GPIO22; MPU6050 and BME280 at 3V3 |
| soil sensor | AO GPIO39, VCC 3V3 |
| UART | ESP32 TX GPIO17 → Pi RX GPIO15, physical pin 10 |
| UART | ESP32 RX GPIO16 ← Pi TX GPIO14, physical pin 8 |
| logic power | power bank → Pi PWR IN; Pi 5 V pin 2 → verified ESP32 5 V/VIN input |
| camera | C920 → Pi USB data port through OTG |

all grounds join together, including AA negative. the AA pack supplies the
motors through the driver. GPIO34/35 have no internal pull-ups; check the
encoder modules' outputs. disconnect the Pi 5 V feed when USB-programming the
ESP32 unless its documented power circuit allows both supplies.

[the full wiring plan](hardware/wiring.md) has motor outputs, capacitor polarity,
ground pins, a diagram and the planned standoffs, straps and camera bracket.
nothing has been assembled or stability-tested yet.

## known limits

- the cheap single-channel encoders have low resolution and cannot independently
  measure direction. measure ticks per revolution; do not assume 20 is correct.
- the Pi Zero 2 W has 512 MB RAM. capture and logging are planned for the Pi;
  heavier image analysis and training belong on a computer.
- the webcam uses the Pi's only USB data port, so the planned ESP32 link is UART.
- motors need their separate AA supply. loose breadboard connections need
  securing before driving.
- the small 2WD chassis has no proven grass, slope, weather or obstacle capability.
  indoor tests come first; any garden trial starts supervised.
- prototype 1 has no probe arm. soil contact is manual at a stop, and air readings
  must not be presented as soil measurements.
- raw moisture counts and plant photos cannot establish nutrient deficiency,
  disease or “dead soil” on their own.
- simulated values are not training evidence for a real garden model.

## short roadmap

1. finish software preparation, then pass Pi setup and the hardware milestones
   one at a time: hello, motors, encoders, PID, sensors, UART, camera and combined run.
2. after real tests pass, collect repeatable supervised observations with manual
   probe placement, calibration and reviewed labels.
3. later, test a dashboard and narrow image models on a computer; then consider
   better mobility, an automated probe and trials in more than one garden.

[the build plan](docs/plan.md), [garden trial procedure](docs/garden_trial.md),
[prototype roadmap](docs/prototype_roadmap.md), [dataset plan](docs/dataset_plan.md)
and [later attachments](docs/later_prototypes.md) describe proposed work.
dates, fleet sizes and model dataset counts there are planning targets, not results.

[nine pending milestone issues and the private project board](docs/tracking.md)
track the build. [release notes](docs/releases.md) explain tagging after a pass.

## where things live

| folder / file | purpose now |
| --- | --- |
| `firmware/` | ESP32 placeholder; not started |
| `pi/` | Pi placeholder; not started |
| `shared/` | telemetry contract for simulation and future Pi imports |
| `simulation/` | fake ESP32, run generator, verifier and one-command check |
| `analysis/` | reads and summarises simulated saved files; no AI yet |
| `hardware/` | proposed parts and wiring |
| `data/sample/` | small, clearly labelled simulated example |
| `docs/` | plans, data contract and preparation notes |
| `CONTEXT.md` | current state and constraints for continuing the project |
| `CHANGELOG.md` | changes and honest progress |

## sharing and licences

code is MIT licensed. original documentation, hardware plans and the invented
sample dataset are CC BY 4.0; keep attribution and state changes.
[licensing details](docs/licensing.md) explain the scope. linked third-party
materials keep their own licences. real private garden data is not included
or automatically licensed by this project.

the repository stays private while preparing. do not add credentials, raw
photos or identifiable records to Git. use the [publication checklist](docs/publication.md)
before sharing a source snapshot. keep local runs and recordings outside the
published source.
