I'm building a small Olimex BB48 and Radxa ZERO 3W rover to test driving, sensor logging and timestamped garden photos.

## Current status

**Software checks run on the computer only. Radxa is bought, but no rover is
built or hardware tested.** The base Olimex RP2350-PICO2-BB48 is the planned
controller, £14.50 and not yet bought. The earlier controller orders/ideas
are dropped. [The choice and open checks](docs/controller_choice.md)

Milestone 1 USB counter builds for BB48. Native protocol tests, serial logger
tests and soil calibration checks use SIMULATED inputs. Hardware steps 0–8
are all pending. Camera capture, PID, dashboard and AI are not implemented.

S0 passed on 9 October 2026 with 300 invented rows. That checks parsing/files,
not motors, sensors, UART or real timing. **All example readings and the
committed sample are SIMULATED DATA**, invented on a computer.

## The data format

One run has `meta.json`, `telemetry.csv` and a `photos/` folder.
The shared contract is [shared/data_format.py](shared/data_format.py).

| CSV column | Meaning / unit |
| --- | --- |
| `t_ms` | Elapsed controller boot time, ms; a virtual clock in the simulation |
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

## Software ready for the parts

The prepared firmware is milestone 1 only: an increasing USB counter once a
second. `Serial` is native USB; `Serial1` UART0 GPIO0/1 stays uninitialised.
There is no motor/sensor firmware. A computer build is not a hardware pass.

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e olimex_pico2bb48
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
.\.venv\Scripts\python.exe -m pi.check
.\.venv\Scripts\python.exe -m analysis.check
```

See [software preparation](docs/software_prep.md) for setup and native GCC.
The unchanged pure protocol library keeps T/D/STOP, missing cells and the
256-byte limit. Logger and calibration tests use SIMULATED input only.

## Planned parts

Radxa ZERO 3W stays the computer, bought at £44 including shipping, untested.
Base Olimex RP2350-PICO2-BB48 is the controller choice at £14.50, **not yet
bought**. The C920 is already owned. No working-rover total is confirmed.

The [parts list](hardware/parts.md) includes a BB48 USB-C data lead, seven
10 kΩ driver pull-downs, a 100 nF soil-input capacitor and an inline USB
power meter. Use checked spare chargers/adapters where possible. A hub is
optional after measurements, not required to power BB48. The Nucleo and
ESP32 order ideas are dropped.

## Proposed wiring

**Planned and untested.** Check the base board, GPIO/header numbering and
actual module levels before wiring. Use 3.3 V signal logic only.

| Connection | Planned pins |
| --- | --- |
| BB48 → TB6612 | PWMA 6, AIN1 7, AIN2 8, PWMB 9, BIN1 10, BIN2 11, STBY 12 |
| Driver supplies/defaults | Checked 3V3 VCC, separate AA VM, common GND; 100 µF VM capacitor and seven input pull-downs |
| Encoders | Left DO GPIO14, right DO GPIO15; verified 3.3 V output/pull-ups |
| Shared I2C1 | `Wire1` SDA GPIO2, SCL GPIO3; leave default QWST empty because GPIO12 is STBY |
| Soil and light | GPIO40 ADC0 and GPIO41 ADC1; later 12-bit reads, 100 nF soil input capacitor |
| UART0 to Radxa UART3-M0 | GPIO0 TX → pin 3 RX; GPIO1 RX ← pin 5 TX; GND ↔ pin 6 |
| Logic power | Radxa USB-C 1, BB48 separate USB-C lead; one BB48 supply at a time |
| Camera | C920 on USB-C 2; published 500 mA budget, current still unknown |

Keep Radxa pins 2/4 disconnected until measured/reviewed. External BB48 VSYS
must not be combined with USB. ADC noise, A2/A4 revision and STBY-low at reset
are open checks. The [full wiring](hardware/wiring.md) includes later pin
reservations, unchanged Radxa fallbacks and the proposed diagram.

## Known limits

- The cheap single-channel encoders have low resolution and cannot independently
  measure direction. Count pulses with interrupts first. Command direction is
  only an assumption during coasting or reversal. Measure ticks per revolution;
  do not assume 20 is correct. Timer counting and magnetic quadrature need a
  separate later milestone using HAL or LL; `HardwareTimer` has no encoder mode.
- The planned logic board is a 2 GB Radxa ZERO 3W. Capture and logging are planned
  for that board; heavier image analysis and training belong on a computer.
- The C920 is planned for USB-C 2 through a data adapter. The BB48 link is UART;
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
| `firmware/` | Planned USB counter firmware and computer-tested pure protocol functions |
| `pi/` | Serial logger and command sender, tested only with simulated input |
| `shared/` | Telemetry contract for simulation and the future logger |
| `simulation/` | Simulated controller, run generator, verifier and one-command check |
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
