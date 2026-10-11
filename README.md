I'm building a small ESP32 and Radxa ZERO 3W rover to test driving, sensor logging and timestamped garden photos.

## Current status

**Only the computer simulation runs. I've bought the Radxa board, but no rover has been built or hardware tested.**
The logic board code and ESP32 firmware have not started. None of the hardware milestones
1–8 have passed, and board setup milestone 0 has not passed either. There is no
working garden rover, camera capture, dashboard, PID controller or AI model yet.

The separate software step, S0, passed on 9 October 2026: Python generated and
checked 300 invented rows. The reorganised one-command check also passes.
These results test files and parsing, not motors, sensors, UART or real timing.

**all example readings and the committed sample are SIMULATED DATA.** They
were invented on a computer, not collected from a real garden.

## The data format

One run has `meta.json`, `telemetry.csv` and a `photos/` folder.
The shared contract is [shared/data_format.py](shared/data_format.py).

| CSV column | Meaning / unit |
| --- | --- |
| `t_ms` | Elapsed ESP32 boot time, ms; a virtual clock in the simulation |
| `cmd_left`, `cmd_right` | Requested wheel angular speeds, rad/s; not PWM or measured speed |
| `enc_left`, `enc_right` | Cumulative raw encoder pulse counts |
| `gyro_z` | Body Z angular velocity, rad/s |
| `accel_x`, `accel_y` | Body X/Y accelerometer readings, m/s², including gravity |
| `soil_raw` | 12-bit ADC count, 0–4095; not a moisture percentage |
| `temp_c` | Air temperature, °C |
| `humidity_pct` | Relative humidity, % |

New simulated CSV files start like this. **The numbers below are simulated:**

```csv
# SIMULATED DATA: invented readings; no hardware or real garden measurements.
t_ms,cmd_left,cmd_right,enc_left,enc_right,gyro_z,accel_x,accel_y,soil_raw,temp_c,humidity_pct
100,0.0,0.0,0,0,0.0,0.0062,0.0298,1801,21.0,50.03
```

The notice is followed by the column header and data rows. The reader handles
that notice before reading the CSV. Missing optional sensor readings stay
empty, rather than becoming a misleading zero.

Metadata includes `run_id, date, surface, battery_type, pid_gains, notes`,
plus schema version, `data_source: simulation`, `csv_format_version: 2`,
timing, command units and calibration. Unmeasured calibration and PID gains
are `null`. The sample's date is its generation time, not a garden visit.
Simulation photos are empty apart from a text placeholder in the tracked sample.

[The full data contract](docs/data_contract.md) explains the units, planned
UART messages and encoder maths.

## Running the simulation

Use Python 3.12 from a terminal opened in the repository root. No extra Python
packages or hardware are needed.

The whole pass/fail check is one command:

```powershell
python -m simulation.check
```

It creates and verifies a temporary 30-second simulated run, checks that
damaged files are rejected, then verifies the committed simulated example.
A pass means 300 rows, 11 columns, virtual timestamps 100 ms apart and valid
simulation metadata. It does not pass a hardware milestone.

To keep your own simulated run:

```powershell
python -m simulation.simulate_run
```

This prints the saved folder and the exact `python -m simulation.verify_run ...`
command to copy. Normal runs stay in ignored `runs/`. 30 virtual seconds are
generated immediately; this does not measure live performance.

To inspect the small example already in Git:

```powershell
python -m simulation.verify_run data/sample/example_sim
python -m analysis.inspect_run data/sample/example_sim
```

Legacy CSV format 1 is supported only when simulation metadata accompanies it.
The checker warns when the standalone simulation notice is absent.

## Planned parts

I've bought the Radxa board for £44 including shipping. **The other figures are
unverified planning estimates, not current shop quotes or a confirmed build cost.**
The original aim was roughly £100. The other parts are still planned, and the
C920 is already owned.

| Part | Cost or planning allowance |
| --- | --- |
| Radxa ZERO 3W, planned configuration: 2 GB, soldered header, no eMMC | £44 paid, including shipping; bought, not tested |
| 32 GB A1 microSD | £6–8 |
| USB microSD reader | £5–15 |
| Two data-capable USB-C male to USB-A female adapters, webcam and keyboard | £4–8 for both |
| USB-A to USB-C power cable, power bank to Radxa USB-C 1 | £3–5 |
| Micro-HDMI (type D) to HDMI cable | £4–8 |
| USB keyboard | Borrow if possible; purchase price not estimated |
| Small heatsink for the Radxa | £2–5; fit not verified |
| Inline USB power meter | About £8 |
| ESP32 DevKit, ESP32-WROOM-32 | £5–8 |
| Data-capable ESP32 USB cable, matching its connector | Not priced yet; check micro-USB or USB-C |
| 2WD chassis, two 1:48 motors, wheels, caster, encoder discs, 4xAA holder | £10–20 |
| Two LM393 speed sensors, if not included | £2–4 |
| TB6612FNG driver module | £3–5 |
| MPU6050 IMU module | £2–4 |
| BME280 module | £3–6 |
| Capacitive soil moisture sensor | £2–4 |
| 10,000 mAh USB power bank, at least 5 V / 2 A on the Radxa output, ideally two outputs for separate ESP32 power | £10–15 |
| Four AA NiMH cells and charger | £10–15 |
| Breadboard, mostly female-to-female jumpers, 100 µF capacitor, Velcro and zip ties | £8–12 |
| 5 V / 3 A USB bench supply | £6–15; Radxa recommends its Power PD30W adapter, whose price is not verified here |
| Multimeter, optional | £8–12 |
| 3.3 V USB-serial adapter supporting 1,500,000 baud, optional first-boot fallback | £5–10 |
| Logitech C920 webcam | Already owned |

**Rough estimate for the priced, non-optional rows, including the bought board: about £140–210.**
The £44 board cost and remaining allowances add up to £137–209 before rounding.
This assumes a borrowed keyboard, the existing C920 and separate LM393 modules.
It excludes the optional
multimeter and USB-serial adapter, the unpriced ESP32 cable, soldering supplies,
any extra mounting parts and delivery on the remaining orders. The board's
shipping is already included. It is not a confirmed total.

The USB-C adapters must carry data, and the HDMI cable must be micro-HDMI
(type D). Most jumpers will be female-to-female because the Radxa and ESP32
headers are male pins. I won't buy a powered USB hub unless the C920 misbehaves
on USB-C 2. [The parts list](hardware/parts.md) has the rest of the buying checks.
No seller stock or delivery price is confirmed here.

## Proposed wiring

**Planned and untested: check the actual module labels before connecting power.**

The logic board is Radxa ZERO 3W. Its numbers below are physical header pins;
the ESP32 numbers are GPIO numbers. TX crosses to the other board's RX.

| Connection | Planned pins |
| --- | --- |
| ESP32 → TB6612 | PWMA 25, AIN1 26, AIN2 27, PWMB 13, BIN1 32, BIN2 33, STBY 4 |
| Driver supplies | VCC to ESP32 3V3; VM to AA positive; 100 µF across VM/GND |
| Encoders | Left DO to GPIO34, right DO to GPIO35; VCC 3V3 |
| Shared I2C | SDA GPIO21, SCL GPIO22; MPU6050 and BME280 at 3V3 |
| Soil sensor | AO GPIO39, VCC 3V3 |
| UART3-M0 | ESP32 TX2 GPIO17 → Radxa pin 3, UART3_RX_M0 |
| UART3-M0 | ESP32 RX2 GPIO16 ← Radxa pin 5, UART3_TX_M0 |
| UART ground | ESP32 GND ↔ Radxa pin 6 |
| Logic power | Power bank output, at least 5 V / 2 A, → Radxa USB-C 1; ESP32 on its own USB lead |
| Camera | C920 → Radxa USB-C 2 through a data-capable USB-C to USB-A adapter |
| First boot only | Micro-HDMI to a monitor; keyboard on USB-C 2 through an adapter, unplugged before connecting the C920 |

All grounds join together, including AA negative. The AA pack supplies the
motors through the driver. GPIO34/35 have no internal pull-ups; check the
encoder modules' outputs. Keep Radxa header pins 2/4 disconnected from the
ESP32 until measured and the supply path is checked. Voltage alone does not
establish available current or protection; the planned ESP32 supply is USB.

Use 3.3 V UART logic at 115200 baud, 8 data bits, no parity and one stop bit.
Enable UART3-M0 through the `rsetup` overlays and reboot. `/dev/ttyS3` is expected
but unconfirmed until checked on the board. Avoid Radxa pins 8/10, the UART2
debug console, and pins 27/28. UART4-M1 and UART5-M1 fallbacks are listed in
[the planned wiring](hardware/wiring.md). Do the
[milestone 0 board checks](docs/plan.md#milestone-0-checks-before-wiring) before
connecting the UART wires. Nothing in this wiring has passed a hardware test.

[The full wiring plan](hardware/wiring.md) has motor outputs, capacitor polarity,
ground pins, a diagram and the planned standoffs, straps and camera bracket.
Nothing has been assembled or stability-tested yet.

## Known limits

- The cheap single-channel encoders have low resolution and cannot independently
  measure direction. Measure ticks per revolution; do not assume 20 is correct.
- The planned logic board is a 2 GB Radxa ZERO 3W. Capture and logging are planned
  for that board; heavier image analysis and training belong on a computer.
- The C920 is planned for USB-C 2 through a data adapter. The ESP32 link is UART;
  the Radxa setup and power checks still need testing.
- Motors need their separate AA supply. Loose breadboard connections need
  securing before driving.
- The small 2WD chassis has no proven grass, slope, weather or obstacle capability.
  Indoor tests come first; any garden trial starts supervised.
- Prototype 1 has no probe arm. Soil contact is manual at a stop, and air readings
  must not be presented as soil measurements.
- Raw moisture counts and plant photos cannot establish nutrient deficiency,
  disease or “dead soil” on their own.
- Simulated values are not training evidence for a real garden model.

## Short roadmap

1. Finish software preparation, then pass board setup and the hardware milestones
   one at a time: hello, motors, encoders, PID, sensors, UART, camera and combined run.
2. After real tests pass, collect repeatable supervised observations with manual
   probe placement, calibration and reviewed labels.
3. Later, test a dashboard and narrow image models on a computer; then consider
   better mobility, an automated probe and trials in more than one garden.

[The build plan](docs/plan.md), [garden trial procedure](docs/garden_trial.md),
[prototype roadmap](docs/prototype_roadmap.md), [dataset plan](docs/dataset_plan.md)
and [later attachments](docs/later_prototypes.md) describe proposed work.
Dates, fleet sizes and model dataset counts there are planning targets, not results.

[The nine pending milestone issues](https://github.com/50kfunded/gardening-data-rover/issues)
track the build. [Release notes](docs/releases.md) explain tagging after a pass.

## Where things live

| Folder / file | Purpose now |
| --- | --- |
| `firmware/` | ESP32 placeholder; not started |
| `pi/` | Existing logic board placeholder; not started |
| `shared/` | Telemetry contract for simulation and the future logger |
| `simulation/` | Fake ESP32, run generator, verifier and one-command check |
| `analysis/` | Reads and summarises simulated saved files; no AI yet |
| `hardware/` | Proposed parts and wiring |
| `data/sample/` | Small, clearly labelled simulated example |
| `docs/` | Plans, data contract and preparation notes |
| `CONTEXT.md` | Current state and constraints for continuing the project |
| `CHANGELOG.md` | Changes and honest progress |

## Sharing and licences

Code is MIT licensed. Original documentation, hardware plans and the invented
sample dataset are CC BY 4.0; keep attribution and state changes.
[Licensing details](docs/licensing.md) explain the scope. Linked third-party
materials keep their own licences. Real private garden data is not included
or automatically licensed by this project.

The repository is public and contains source, plans and a labelled simulated
sample. Do not add credentials, raw photos or identifiable records to Git.
Use the [publication checklist](docs/publication.md) before sharing new material.
Keep local runs and recordings outside the published source.
