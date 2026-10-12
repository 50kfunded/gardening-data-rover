# Radxa logic board code

**Planned and hardware-untested.** A serial logger and small command sender
are prepared. They have only been tested with SIMULATED input on a computer.
There is no camera script or dashboard yet. No hardware milestone has passed.

The folder stays named `pi/` for now so the existing paths and future module
commands do not change. The planned logic board is Radxa ZERO 3W.

The logger imports the same contract as the simulation:

```python
from shared.data_format import COLUMNS, parse_telemetry
```

Run the modules from the repository root. The shared contract stays in `shared/`.

## Computer check

Install `pi/requirements.txt` in a virtual environment, or use the development
setup in [software preparation](../docs/software_prep.md). Then run:

```powershell
.\.venv\Scripts\python.exe -m pi.check
.\.venv\Scripts\python.exe -m pi.demo
```

This uses pyserial's `loop://` and fake chunks. All files it creates are
labelled **SIMULATED DATA** and removed with the temporary test folders.
The separate demo keeps a labelled simulated run under ignored `runs/`, using
300 invented lines through loopback. Neither command opens a real serial port.

## Logger and commands

Copy `pi/config.example.json` to ignored `pi/config.local.json` and choose the
serial port there, or supply `--port`. There is no default port. The example
has `null` deliberately, so it cannot accidentally open a board. The source
defaults to simulation. Use `--source hardware` only with real telemetry;
that option records the operator's choice, not a hardware validation result.
The logger refuses to label `loop://` as hardware.

Future hardware examples, **not run on a board yet**:

```sh
python -m pi.logger --config pi/config.local.json --source hardware --duration 30
python -m pi.send_command --config pi/config.local.json --source hardware STOP
python -m pi.send_command --config pi/config.local.json --source hardware D 1 1
```

Milestone 1 only prints a counter on BB48 native USB and leaves UART0
uninitialised. Future PC protocol tests will use USB `Serial`; Radxa uses
UART0 `Serial1` GPIO0 TX / GPIO1 RX. These examples need later telemetry
firmware; the counter is never recorded as sensor data.

The logger creates ignored `runs/<run_id>/telemetry.csv`, `meta.json` and an
empty `photos/`. The CSV keeps the same 11 columns. Invalid ASCII, bad values,
oversized frames and unfinished lines are dropped and counted. A timeout
keeps a partial line until more bytes arrive. Nothing is saved as a valid row
until the shared parser accepts a complete newline-terminated line.

Time moving backwards or repeating, or either encoder count decreasing,
closes the current run and starts a new one. The reason appears in the terminal
and both runs' metadata. Disconnects stop recording; there is no silent
reconnect. Malformed totals are printed and saved when a run closes. A power
loss can still leave metadata counts incomplete; flushing is not a power-loss
guarantee. The receive-time anchor is not a measured exposure or boot time.

A reset with no visible counter regression cannot be proved from this format.
See [the protocol proposal](../docs/protocol_proposals.md). No extra counter,
checksum or boot message has been implemented. The existing simulation
verifier remains for its original S0 files; use `pi.check` for this logger.

The command sender uses D/STOP and checks complete writes, but has no reply or
motor effect to verify yet. Close the standalone logger before opening the
same port in the sender. A future combined script can call `send_command()`
with the logger's already-open serial handle instead of opening it twice.

## Planned libraries and connections

Use `pyserial` for UART at 115200 baud, 8 data bits, no parity and one stop bit.
The serial port is a configuration setting. `/dev/ttyS3` is expected for
UART3-M0, but is unconfirmed until checked on the board. Enable the chosen
overlay through `rsetup`, then check the device name and console use before
connecting anything.

Use V4L2 tools to inspect the C920's supported modes and controls, and OpenCV
or `fswebcam` for capture. The C920 is planned for USB-C 2 through a data
adapter. There is no dependency on `RPi.GPIO`, `pigpio` or `picamera`.

BB48 will keep the real-time motor loop and sensor reads. Radxa sends commands
and saves telemetry/photos. Power uses Radxa USB-C 1 and a separate BB48
USB-C lead. Use one controller source at a time; never external VSYS with USB.
No supply from Radxa header 2/4 is planned. Optional hub measurements must
respect the published 500 mA USB-C 2 budget.

See [the planned wiring](../hardware/wiring.md) and
[milestone 0 checks](../docs/plan.md#milestone-0-checks-before-wiring).
No real serial connection, camera capture or headless setup has passed a
hardware test yet. [The Windows USB serial notes](../docs/windows_uart.md) are
planned checks, with the native USB route and single-power-source rule.
