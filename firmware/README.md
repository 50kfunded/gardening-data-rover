# ESP32 firmware

**Planned and hardware-untested.** The only firmware milestone written is the
USB counter for milestone 1. It has been compiled, not uploaded or tested on
an ESP32. No hardware milestone has passed.

`platformio.ini` selects `esp32dev` with the Arduino framework. `src/main.cpp`
prints an increasing counter at 115200 baud, once a second. It reserves Serial2
on GPIO16 RX and GPIO17 TX for the later Radxa link, but sends and receives
nothing there. GPIO12 is not used. There is no motor wiring or motor code.

`lib/rover_protocol/` holds pure telemetry formatting and D/STOP parsing
functions. They make no hardware calls and are not called by milestone 1.
Missing sensor fields stay empty. Lines include a newline and must fit within
256 bytes. Speeds are rad/s, not PWM. Numeric output uses six decimal places;
soil ADC counts stay integers. Invalid input returns failure, not a partial line.

The parser checks syntax and finite numbers. Physical speed limits, command
timeout behaviour and motor control still need their later milestone. A parsed
STOP is only a value here; it does not operate any motor.

From the repository root, after [software setup](../docs/software_prep.md):

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e esp32dev
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
```

The native environment needs a desktop GCC toolchain. Its eight tests use
**SIMULATED DATA and commands only**. They do not measure timing or pass any
hardware milestone. See [the Windows setup notes](../docs/software_prep.md).

When the board arrives, use a data-capable USB cable as its only power source.
Leave the motors, sensors, Radxa and external UART adapter disconnected.
The [milestone 1 instructions](../docs/software_prep.md#milestone-1-when-the-esp32-arrives)
give the upload, serial monitor and pass test. Ask for the result before
continuing to motor wiring.
