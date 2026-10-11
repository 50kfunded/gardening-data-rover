# Software preparation

**Planned and hardware-untested.** The counter firmware builds and the computer
tests pass. No firmware has been uploaded, no real UART recording has been
made and no hardware milestone has passed. All invented test inputs and saved
test files are labelled SIMULATED DATA.

## Setup on Windows

Use a terminal in the repository root. There is no need to install Linux on
the computer. Use a virtual environment so these dependencies stay separate:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m simulation.check
.\.venv\Scripts\python.exe -m pi.check
.\.venv\Scripts\python.exe -m platformio run -d firmware -e esp32dev
```

The original simulation needs no extra packages. The serial checks use
pyserial 3.5. Development uses PlatformIO 6.2.0, with the ESP32 platform pinned
in `firmware/platformio.ini`. Build output, virtual environments, local config
and normal run folders are ignored. Do not commit recordings or settings.

## Native C++ tests

PlatformIO's native environment needs GCC on the computer; it does not install
that compiler itself. On Windows, use a GCC/MinGW-w64 installation such as
[MSYS2](https://www.msys2.org/). In the MSYS2 UCRT64 terminal, install:

```sh
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

Back in PowerShell, add the standard compiler location for this terminal only:

```powershell
$env:Path = "C:\msys64\ucrt64\bin;$env:Path"
gcc --version
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
```

Adjust the path if MSYS2 was installed elsewhere. A portable GCC/MinGW-w64
build also works when its `bin` directory is on PATH. The native checks run
on the computer and use simulated values. They need no ESP32 or serial adapter.
See [PlatformIO's native guide](https://docs.platformio.org/en/latest/platforms/native.html).

## Milestone 1 when the ESP32 arrives

First check that it is the classic ESP32-WROOM-32 DevKit, with the expected
pin labels, rather than a C3 or S3 board. This firmware selects `esp32dev`.

**Wiring for this milestone:** one data-capable USB cable from the computer
to the ESP32's USB connector. Leave all header wires disconnected, including
motor power, sensors, the Radxa and the external USB-serial adapter. Do not
feed another supply into VIN or 3V3 while USB powers the board.

List the available ports:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Use the actual ESP32 COM port in place of the example `COM7` below. These
upload and monitor commands are planned, not run against hardware yet:

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e esp32dev -t upload --upload-port COM7
.\.venv\Scripts\python.exe -m platformio device monitor --port COM7 --baud 115200
```

**Pass test, still pending:** see `Counter: 0`, `Counter: 1`, `Counter: 2` and
continued increases for 30 seconds at about one count per second. Opening the
monitor may reset the board and restart at zero. **Fail:** no output, unreadable
text, repeated unexpected resets or a stopped counter. Record what happened
and ask for help before connecting anything else. A successful build alone
does not pass this test.

The counter is diagnostic text, not T telemetry or garden data. Serial2 uses
GPIO16 RX and GPIO17 TX but is idle in this firmware. The pure formatting and
parsing functions are preparation for later work, not live sensor firmware.
Do not continue to motors until the actual counter result is reviewed.

## What the logger checks now

`python -m pi.check` covers simulated loopback, missing sensor cells, malformed
frames, the 256-byte boundary, fragmented reads, counter resets, disconnects
and D/STOP writes. It uses temporary folders and labels every saved file as
simulation. Hardware operation, timing, power and camera capture remain untested.

The later logger will record a receive-time anchor for each split run. For
an ESP32 time `t_ms`, a rough UTC estimate is:

```text
first_received_unix_s + (t_ms - esp32_first_ms) / 1000
```

Dividing by 1000 converts milliseconds to seconds. This estimate still includes
unknown UART delay and clock drift, so it is not a checked timing result.
