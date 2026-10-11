I'm building a small NUCLEO-G474RE and Radxa ZERO 3W rover to test driving, sensor logging and timestamped garden photos.

## Current status

**Software preparation is tested on the computer only. I've bought the Radxa
and ordered the NUCLEO-G474RE, but no rover has been built or hardware tested.**
The Nucleo was ordered from Anglia on 11 October 2026 at a listed £11.98 ex VAT.
Its VAT-inclusive total is unconfirmed, and it has not arrived or been tested.
Milestone 1 counter firmware builds, and the serial logger and command sender
have only been tested with SIMULATED input. Hardware operation is planned and
untested. None of the hardware milestones
1–8 have passed, and board setup milestone 0 has not passed either. There is no
working garden rover, camera capture, dashboard, PID controller or AI model yet.

The separate software step, S0, passed on 9 October 2026: Python generated and
checked 300 invented rows. The reorganised one-command check also passes.
These results test files and parsing, not motors, sensors, UART or real timing.

**All example readings and the committed sample are SIMULATED DATA.** They
were invented on a computer, not collected from a real garden.

## The data format

One run has `meta.json`, `telemetry.csv` and a `photos/` folder.
The shared contract is [shared/data_format.py](shared/data_format.py).

| CSV column | Meaning / unit |
| --- | --- |
| `t_ms` | Elapsed Nucleo boot time, ms; a virtual clock in the simulation |
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

[Software preparation](docs/software_prep.md) gives the Windows setup, native
C++ tests and the pending USB counter test. The serial logger uses the unchanged
shared parser, preserves missing cells, counts malformed lines and splits on
visible time or encoder resets. Its port has no default.

After installing `requirements-dev.txt` in a virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pi.check
.\.venv\Scripts\python.exe -m pi.demo
.\.venv\Scripts\python.exe -m platformio run -d firmware -e nucleo_g474re
```

The demo saves 300 invented rows through `loop://`, clearly labelled simulation.
It does not send anything to a board. [The firmware notes](firmware/README.md)
and [logger notes](pi/README.md) explain what is prepared and still untested.
The firmware only prints a counter through the ST-LINK virtual COM port.
`Serial` maps to LPUART1 PA2/PA3 in the checked STM32duino core. USART1 for
the Radxa remains uninitialised, and no motors or sensors are used.
[Windows UART checks](docs/windows_uart.md) are for later hardware testing.
[Protocol additions](docs/protocol_proposals.md) are proposals awaiting approval.

## Planned parts

I've bought the Radxa board for £44 including shipping and ordered the Nucleo
at a listed £11.98 ex VAT, with its invoice total still unconfirmed. **The other
figures are unverified planning estimates, not current shop quotes or a confirmed
build cost.** The original aim was roughly £100. The other parts are still
planned, and the C920 is already owned.

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
| ST NUCLEO-G474RE | Ordered 11 October 2026, £11.98 ex VAT listing; invoice total unconfirmed, not arrived or tested |
| Data-capable Micro-B USB cable to Nucleo CN1 | Not priced yet; reuse a suitable cable if possible |
| 2WD chassis, two 1:48 motors, wheels, caster, encoder discs, 4xAA holder | £10–20 |
| Two LM393 speed sensors, if not included | £2–4 |
| TB6612FNG driver module | £3–5 |
| MPU6050 IMU module | £2–4 |
| BME280 module | £3–6 |
| Capacitive soil moisture sensor | £2–4 |
| 10,000 mAh USB power bank, at least 5 V / 2 A on the Radxa output, ideally two outputs for separate Nucleo power | £10–15 |
| Four AA NiMH cells and charger | £10–15 |
| Breadboard, mixed F-F/M-F/M-M jumpers, 100 µF capacitor, Velcro and zip ties | £8–12 |
| 5 V / 3 A USB bench supply | £6–15; Radxa recommends its Power PD30W adapter, whose price is not verified here |
| Multimeter, optional | £8–12 |
| DSD TECH SH-U09C5 or suitable 3.3 V USB-serial adapter, optional Radxa console fallback | £5–10 allowance; verify 1,500,000 baud and logic voltage, not required for Nucleo |
| Logitech C920 webcam | Already owned |

**Rough planning subtotal for the other priced, non-optional rows: £132–201,
including the £44 Radxa. Add the Nucleo invoice total once it is confirmed.**
The Nucleo listing was £11.98 ex VAT; its VAT-inclusive total and delivery are
not confirmed here. I am not treating that listing as a delivered price.
This subtotal assumes a borrowed keyboard, the existing C920 and separate
LM393 modules. It excludes the optional multimeter and USB-serial adapter,
the unpriced Micro-B cable, soldering supplies, extra mounting parts and
delivery on the remaining orders. The Radxa shipping is already included.
This is a planning allowance, not a confirmed whole-build total.

The USB-C adapters must carry data, and HDMI must be micro-HDMI (type D).
Use female-to-female jumpers for Radxa/morpho male pins and male-to-female
for the Nucleo's Arduino sockets. The Micro-B cable serves the built-in
ST-LINK programmer and virtual COM port; no separate PC serial adapter is
required. I won't buy a powered USB hub unless the C920 misbehaves on USB-C 2.
[The parts list](hardware/parts.md) has the buying and power checks.


## Proposed wiring

**Planned and untested. I will check each pin against ST's user manual and the
actual board revision before wiring.** Nucleo D/A labels and MCU pin names
are different from the Radxa's physical header pin numbers.

| Connection | Planned pins |
| --- | --- |
| Left driver PWM and direction | PWMA D12 / PA6, TIM3_CH1; AIN1 D6 / PB10; AIN2 D7 / PA8 |
| Right driver PWM and direction | PWMB D9 / PC7, TIM3_CH2; BIN1 D8 / PA9; BIN2 D11 / PA7 |
| Driver standby | STBY A2 / PA4, digital output |
| Driver supplies | VCC to checked Nucleo 3V3; VM to AA positive; 100 µF across VM/GND |
| Encoders | Left DO D2 / PA10; right DO D4 / PB5; checked 3.3 V supply and outputs |
| Shared I2C | SDA D14 / PB9; SCL D15 / PB8; MPU6050 and BME280 at 3V3 |
| Soil sensor | AO A0 / PA0, planned 12-bit ADC; check actual reference voltage |
| Spare light input | A1 / PA1; sensor and circuit not chosen |
| USART1 to UART3-M0 | Nucleo D1 / PC4 TX → Radxa pin 3, UART3_RX_M0 |
| USART1 to UART3-M0 | Nucleo D0 / PC5 RX ← Radxa pin 5, UART3_TX_M0 |
| UART ground | Nucleo GND CN6 pin 6 or 7 ↔ Radxa pin 6 |
| Logic power | Bank output at least 5 V / 2 A → Radxa USB-C 1; Nucleo on its own Micro-B USB lead, power selection to check |
| Camera | C920 → Radxa USB-C 2 through a data-capable USB-C to USB-A adapter |
| First boot only | Micro-HDMI to monitor; keyboard on USB-C 2 through an adapter, then unplug before the C920 |

All signal logic is 3.3 V; PA3 and PC5 are not 5 V tolerant. Reserve PA2/PA3
for the ST-LINK VCP, PA13/PA14 for SWD and PB3 / D3 for SWO. Check sensor
pull-ups and ADC voltage limits. All grounds join, including AA negative.
The AA pack supplies only the motors through the driver.

The Nucleo gets one USB power source at a time. Standalone bank power still
needs checking: ST's default USB path depends on enumeration, and the manual
uses inconsistent JP2/JP5 names. Do not move a jumper before checking the
schematic for the delivered revision. Keep Radxa header pins 2/4 disconnected
from the Nucleo until measured and the supply path checked. Voltage alone
does not establish available current or protection.

Use crossed TX/RX, 115200 baud, 8 data bits, no parity and one stop bit.
Enable Radxa UART3-M0 through `rsetup` and reboot. `/dev/ttyS3` is expected
but unconfirmed until checked. Avoid Radxa pins 8/10, the UART2 debug console,
and 27/28. UART4-M1 and UART5-M1 fallbacks stay in
[the full wiring plan](hardware/wiring.md), with connector positions, sources,
a diagram and mounting checks. Do the
[milestone 0 checks](docs/plan.md#milestone-0-checks-before-wiring) before connecting.
Nothing has been assembled or stability-tested yet.

## Known limits

- The cheap single-channel encoders have low resolution and cannot independently
  measure direction. Count pulses with interrupts first. Command direction is
  only an assumption during coasting or reversal. Measure ticks per revolution;
  do not assume 20 is correct. Timer counting and magnetic quadrature need a
  separate later milestone using HAL or LL; `HardwareTimer` has no encoder mode.
- The planned logic board is a 2 GB Radxa ZERO 3W. Capture and logging are planned
  for that board; heavier image analysis and training belong on a computer.
- The C920 is planned for USB-C 2 through a data adapter. The Nucleo link is UART;
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
