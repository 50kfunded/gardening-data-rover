# The data format, version 1

This records what each number means, its unit and what to save if a reading
is missing. **All data currently produced by this project is simulated.**
The computer simulation uses the same CSV columns planned for the Radxa logger.
The real firmware and serial connection will come later.

The contract lives in `shared/data_format.py`, imported by both the simulation
and the future logic board code. The demo's 30-second length lives in `simulation/settings.py`.

New simulated CSV files have this first line, followed by the column header:

```text
# SIMULATED DATA: invented readings; no hardware or real garden measurements.
```

`csv_format_version: 2` records that extra notice line. Schema version 1 still
describes the same 11 telemetry fields. `analysis/read_run.py` reads the notice
before parsing the CSV. With pandas later, use `comment="#"`. Old local S0 runs
use CSV format 1 and are accepted only with their simulation metadata; the
checker warns that those CSV files are not labelled on their own.

One CSV row is one snapshot. Do not attach a photo or repeat the run's notes
inside every row. Store the run description once in `meta.json` and photos in
the run's `photos/` directory.

| CSV column | Meaning and unit | Source on the future rover |
| --- | --- | --- |
| `t_ms` | Milliseconds since ESP32 boot, unsigned integer | ESP32 monotonic clock |
| `cmd_left` | Active requested left wheel angular speed, rad/s | Target accepted by the ESP32 |
| `cmd_right` | Active requested right wheel angular speed, rad/s | Target accepted by the ESP32 |
| `enc_left` | Cumulative left pulse count since ESP32 boot | Left LM393 interrupt |
| `enc_right` | Cumulative right pulse count since ESP32 boot | Right LM393 interrupt |
| `gyro_z` | Angular velocity about body Z, rad/s | MPU6050, converted to this unit |
| `accel_x` | Body X accelerometer reading, m/s^2, with gravity included | MPU6050 |
| `accel_y` | Body Y accelerometer reading, m/s^2, with gravity included | MPU6050 |
| `soil_raw` | Raw 12-bit ADC count, integer 0..4095 | GPIO39 ADC, explicitly configured to 12 bits |
| `temp_c` | Air temperature in degrees Celsius | BME280 |
| `humidity_pct` | Relative humidity, 0..100 percent | BME280 |

For body coordinates use X forwards, Y left, Z upwards. A positive `gyro_z`
means an anticlockwise turn viewed from above. Mount the IMU and transform its
axes to these body coordinates when we reach the sensor milestone.

Positive wheel commands mean the wheel pushes the rover forwards; negative
commands request reverse. Zero requests no movement. These commands are speed
targets for the later PID controller. **They are not PWM fractions or measured
wheel speeds.** Open-loop motor exercises will use their own motor-test code.

The specified single-channel encoders give pulse counts, not independent
direction measurements. Raw counts increase for both forward and reverse
rotation. A command's sign alone does not establish the actual wheel direction
while coasting or changing direction. Keep these raw counts; do not claim
signed distance from them without explaining a direction assumption.

## The messages

The proposed ESP32-to-Radxa line includes the active commands so we do not mistake
the last command sent by the Radxa for one actually accepted by the ESP32:

```text
T,t_ms,cmd_left,cmd_right,enc_left,enc_right,gyro_z,accel_x,accel_y,soil_raw,temp_c,humidity_pct
T,1000,6.283185,6.283185,20,18,0.0100,0.0200,0.0000,1800,21.50,48.00
```

The numeric line above is a **simulated example**, not a hardware reading.
The first line above explains the fields; it is not sent as telemetry. Actual
telemetry lines start with `T,`, use ASCII, end with a newline, and have exactly
11 values. The CSV has the same fields without the `T` prefix. Messages must
be at most 256 bytes including their line ending. Metadata records the schema
version; both ends must implement that same version.

Future command examples use the same rad/s speed units:

```text
D,6.283185,6.283185
STOP
```

These commands are documentation only in S0. The simulator does not accept
drive commands. The hardware milestone will implement command limits, STOP
handling, and a command timeout that stops the motors if the Radxa goes silent.

An unavailable sensor reading is an empty field, which becomes an empty CSV
cell. A real zero stays `0`. Do not replace missing readings with zero. For
example, this simulated stopped snapshot has no sensor readings yet:

```text
T,100,0,0,0,0,,,,,,
```

Time, commands and encoder counts are required. The parser rejects wrong field
counts, non-numeric text, NaN, infinity, negative pulse counts, out-of-range ADC
values, and humidity outside 0..100. This checks structure and basic values;
it cannot detect every corruption that still looks like a valid number.

## Sampling and time

The planned control loop is 100 Hz: one update every 0.01 s. Start telemetry
at **10 Hz**: one saved snapshot every 0.1 s. A control update does not have to
produce a CSV row. Environmental sensors may update more slowly; telemetry
can repeat their latest valid reading. This first schema does not record the
age of each individual sensor reading.

With UART configured to 115200 baud, 8 data bits, no parity, one stop bit,
each byte occupies 10 bit periods including start and stop. The theoretical
capacity is 115200 / 10 = 11520 bytes/s in each direction. At our maximum
256-byte line size, 10 telemetry lines/s use at most 2560 bytes/s, leaving
room in the link. This is a link-budget calculation, not measured performance.
See [Espressif's UART documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html)
and [the ESP32 technical reference manual](https://documentation.espressif.com/esp32_technical_reference_manual_en.pdf).

The hardware `t_ms` is elapsed boot time, not a date. On the Radxa we will
record a start-time anchor to relate it to UTC photo times and measure the
alignment error. `date` and `started_unix_s` in this simulation describe when
the computer generated the files; they are not a hardware clock synchronisation.
The virtual clock begins at zero; samples are 100, 200, ..., 30000 ms.

A hardware run must not silently continue through an ESP32 reboot, counter
reset or a 32-bit millisecond rollover (about 49.7 days). We will split or
explicitly handle these events when implementing the live UART logger. S0's
checker expects an uninterrupted, perfectly spaced simulation only.

## The run notes and measurements needed later

`meta.json` includes the required `run_id`, `date`, `surface`, `battery_type`,
`pid_gains`, and `notes`, plus schema version, data source, sampling settings,
time information, command units and calibration. Use UTC with a timezone in
dates. The run ID is a filesystem-safe UTC timestamp with `_sim` appended.

Unmeasured calibration and untuned PID gains are JSON `null`. Null means
"unknown or not done yet"; zero would claim an actual measured value.

When the hardware arrives we need to measure:

| Measurement | Why it matters |
| --- | --- |
| Counted ticks per wheel revolution, separately for each wheel | Convert pulse counts to rotation; measure using the selected interrupt edge |
| Effective radius of each wheel in metres | Convert wheel rotation to distance |
| Track width in metres, between the wheel contact centres | Relate left/right wheel motion to turning |
| Gyro bias while stationary | Correct the apparent rotation of a still rover |
| Raw soil readings in chosen dry/wet reference conditions | Interpret the ADC; raw values are not moisture percentages |
| PID gains and the control/measurement interval used when tuning | Repeat an experiment with the same controller settings |
| Surface, battery type, observations, and straight-line test results | Explain changes between trials |

The first five geometric/encoder calibration values have null entries in this
simulation's metadata. Gyro and soil calibration will be added when we have
real readings. Do not treat an assumed 20-slot disc as a measured count.

Future photographs use `photos/<run_id>_<unix_time>.jpg`; use fractional Unix
seconds to avoid collisions when needed. No pictures are made in S0. When we
implement capture, we will distinguish the recorded capture time from the
camera's actual exposure time, which is not guaranteed by a filename alone.

## The maths for this step

At 10 samples per second, the interval is dt = 1/10 = 0.1 seconds. Over 30
seconds we expect 30 * 10 = 300 rows. The header is not a data row.

Encoder counts are cumulative. If two snapshots contain counts n1 and n2,
the number of new ticks is dn = n2 - n1. If a measured revolution gives N
ticks, those new ticks correspond to dn/N revolutions. Therefore:

```text
angular speed magnitude = 2*pi * dn / (N * dt)       [rad/s]
wheel speed magnitude   = radius * angular speed   [m/s]
```

For an illustrative N = 20, dn = 2 and dt = 0.1 s, the result is one
revolution per second, or 2*pi rad/s. We must measure N on the actual kit.
One tick over that interval changes the estimated angular speed by pi rad/s,
so low-resolution encoders give coarse speed estimates. At 100 Hz this
quantisation is even larger; we will choose a measurement window when we
reach control, while keeping the control updates fast.

We have not introduced PID or a Kalman filter in this milestone. First we
need trustworthy observations with units and time intervals. We will derive
each controller or estimator at the milestone that uses it.

Python's [CSV documentation](https://docs.python.org/3.12/library/csv.html)
explains the `csv.DictWriter` used here. It handles delimiters and converts
`None` to an empty cell. Files are opened with `newline=""` to let the CSV
module manage line endings correctly on Windows.
