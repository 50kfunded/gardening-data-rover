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
.\.venv\Scripts\python.exe -m platformio run -d firmware -e nucleo_g474re
```

The original simulation needs no extra packages. The serial checks use
pyserial 3.5. The checked build uses PlatformIO 6.2.0, ST STM32 platform
20.0.0 and STM32duino 3.0.0. `firmware/platformio.ini` uses the documented
Nucleo configuration; the platform is not pinned, so record resolved versions.
Build output, virtual environments, local config
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
on the computer and use simulated values. They need no Nucleo or serial adapter.
See [PlatformIO's native guide](https://docs.platformio.org/en/latest/platforms/native.html).

## Milestone 1 when the Nucleo arrives

First check the delivered board says NUCLEO-G474RE and record its MB1367
revision. This firmware selects `nucleo_g474re`, Arduino and the built-in
ST-LINK upload method. It has been compiled on the computer only.

**Wiring for this milestone:** one data-capable Micro-B USB cable from the
computer to CN1 on the Nucleo. Leave all header wires disconnected, including
motor power, sensors and the Radxa. No external UART adapter is needed. Use
one power source only; do not add a bank or header supply alongside USB.
Check default jumpers and bridges against the schematic for the delivered
revision. Do not move a jumper based on this plan; UM2505 uses inconsistent
JP2/JP5 names in its power sections.

List the available ports:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Use the actual ST-LINK virtual COM port in place of the example `COM7` below.
These upload and monitor commands are planned, not run against hardware yet:

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e nucleo_g474re -t upload
.\.venv\Scripts\python.exe -m platformio device monitor --port COM7 --baud 115200
```

**Pass test, still pending:** see `Counter: 0`, `Counter: 1`, `Counter: 2` and
continued increases for 30 seconds at about one count per second. If the
monitor missed zero, press RESET once and watch again. **Fail:** no output, unreadable
text, repeated unexpected resets or a stopped counter. Record what happened
and ask for help before connecting anything else. A successful build alone
does not pass this test.

The checked core maps `Serial` to LPUART1 on PA2 TX / PA3 RX, routed to the
ST-LINK VCP by default. The counter is diagnostic text, not T telemetry or
garden data. USART1 on D1 / PC4 TX and D0 / PC5 RX is reserved for the Radxa
and remains uninitialised. The pure protocol functions are later preparation.
D/STOP and T lines will use the VCP for PC tests and USART1 for the Radxa later;
that transport firmware is not written yet. See [Windows serial notes](windows_uart.md)
and the [proposed pin plan](../hardware/wiring.md).
Do not continue to motors until the actual counter result is reviewed.

## What the logger checks now

`python -m pi.check` covers simulated loopback, missing sensor cells, malformed
frames, the 256-byte boundary, fragmented reads, counter resets, disconnects
and D/STOP writes. It uses temporary folders and labels every saved file as
simulation. Hardware operation, timing, power and camera capture remain untested.

The later logger will record a receive-time anchor for each split run. For
a controller time `t_ms`, a rough UTC estimate is:

```text
first_received_unix_s + (t_ms - esp32_first_ms) / 1000
```

Dividing by 1000 converts milliseconds to seconds. This estimate still includes
unknown UART delay and clock drift, so it is not a checked timing result.

`esp32_first_ms` is a legacy metadata key kept for schema compatibility. It
means the first controller boot-time value, including for the planned Nucleo.
The name does not mean a recording came from that older board.
