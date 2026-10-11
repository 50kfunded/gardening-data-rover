# Radxa logic board code

**Planned and untested.** Not started. There is no Radxa UART logger, camera
script or dashboard here yet. Only the computer simulation runs at the moment.

The folder stays named `pi/` for now so the existing paths and future module
commands do not change. The planned logic board is Radxa ZERO 3W.

The future logger will import the same contract as the simulation:

```python
from shared.data_format import COLUMNS, parse_telemetry
```

Run future logic board modules from the repository root with `python -m pi.<module>`.
The shared contract will stay in `shared/`; it won't need copying into this folder.

## Planned libraries and connections

Use `pyserial` for UART at 115200 baud, 8 data bits, no parity and one stop bit.
The serial port will be a configuration setting. `/dev/ttyS3` is expected for
UART3-M0, but is unconfirmed until checked on the board. Enable the chosen
overlay through `rsetup`, then check the device name and console use before
connecting anything.

Use V4L2 tools to inspect the C920's supported modes and controls, and OpenCV
or `fswebcam` for capture. The C920 is planned for USB-C 2 through a data
adapter. There is no dependency on `RPi.GPIO`, `pigpio` or `picamera`.

The ESP32 will keep the real-time motor loop and sensor reads. The Radxa will
send drive commands and save the returned telemetry and photos. Power goes
to Radxa USB-C 1, with a separate USB lead for the ESP32. No ESP32 power feed
from header pins 2/4 is planned.

See [the planned wiring](../hardware/wiring.md) and
[milestone 0 checks](../docs/plan.md#milestone-0-checks-before-wiring).
No serial connection, camera capture or headless setup has passed a hardware
test yet.
