# Software preparation

**Planned and hardware-untested.** BB48 counter firmware builds on the
computer, and the native/logger/simulation checks pass with SIMULATED inputs.
No upload, real UART recording or hardware milestone has passed.

## Setup on Windows

Use a terminal in the repository root and keep dependencies in a virtual
environment. Don't commit local settings, recordings or build output.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m simulation.check
.\.venv\Scripts\python.exe -m pi.check
.\.venv\Scripts\python.exe -m analysis.check
.\.venv\Scripts\python.exe -m platformio run -d firmware -e olimex_pico2bb48
```

The serial checks use pyserial 3.5 and PlatformIO 6.2.0. The Git platform URL
selects the Arduino-Pico BB48 environment, not the stock Mbed Pico target.
It is unpinned, so record resolved versions. [Core PlatformIO guide][pio]

The 13 October 2026 computer build resolved platform 1.20.0 at `5d4561a`,
Arduino-Pico package 1.60100.0 at `fd65f6d4`, and toolchain
5.160100.260719. It produced a UF2 with 9,608 bytes RAM and 40,844 bytes flash
reported; PSRAM was disabled. These are software build figures, not board tests.

On Linux use `python3 -m pi.check` and `python3 -m simulation.check` from the
root, without `-I`. On Windows use the actual Python 3 executable above if
the `python3` name is only a Microsoft Store shortcut.

## Native C++ tests

The unchanged native environment needs desktop GCC on PATH. Use a local
GCC/MinGW installation such as [MSYS2](https://www.msys2.org/), or a portable
compiler. Add its `bin` directory to this terminal's PATH, then run:

```powershell
gcc --version
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
```

The eight native tests exercise pure protocol functions with SIMULATED DATA
and commands only. No board/adapter is needed. The native environment does
not install GCC itself. [PlatformIO native guide][native]

## Milestone 1 when the BB48 arrives

**Planned pass test, still pending.** Confirm base RP2350-PICO2-BB48 rather
than BB48R, inspect headers/revision and record A2/A4 silicon as checked or
unknown. Identification must be compared with the official errata; a board
revision letter is not the chip stepping. Do not change OTP or boot settings.

Use one data-capable USB-C cable from the computer. Disconnect all header
wires, motor batteries, sensors and Radxa. No USB-to-TTL adapter is needed.
Keep one supply only; no external VSYS alongside USB. [Olimex manual][manual]

List ports before/after connection:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Use the actual BB48 USB serial port, not an assumed `COM7`. The board
definition uses `picotool`. For first upload, enter BOOTSEL using BOOT held
while pressing/releasing RESET, then release BOOT; confirm the ROM device
is detected. Check the delivered controls against the manual. These actions
are planned and have not been run on hardware.

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e olimex_pico2bb48 -t upload
.\.venv\Scripts\python.exe -m platformio device monitor --port COM7 --baud 115200
```

The upload and running USB device may have different identities. Re-list
ports after upload/reset. If `picotool` isn't accessible on Windows, stop and
check its driver/setup instructions; don't install an arbitrary driver over
the running COM device. Copying the built UF2 to the ROM mass-storage device
is a possible documented fallback, also untested here. [Upload guide][pio]

**Pass later:** increasing `Counter: 0`, `Counter: 1`, `Counter: 2` and onward
for 30 seconds, about once per second. If zero was missed, press RESET,
reopen the actual port if needed and watch again. **Fail:** no output,
unreadable text, unexpected resets or a stopped counter. Record/review the
result before wiring motors. A build alone does not pass this.

`Serial` is native USB. The 115200 setting doesn't clock USB. UART0 `Serial1`
on GPIO0/1 remains uninitialised. The current counter isn't T telemetry and
ignores commands. Later USB protocol and UART transports still need writing;
the same T/D/STOP format applies, with one active command source.
[Serial documentation][serial], [BB48 variant][variant]

Before motor power, test STBY and all driver input pull-downs at boot/reset
with VM disconnected. Before sensor collection, verify 12-bit ADC setup,
measured reference/output limits and motors-off/on noise. Before the Radxa
link, check its overlay/device name and test the crossed UART wiring.
[Pin plan](../hardware/wiring.md), [build checks](plan.md)

## What the logger checks now

The 18 logger/sender tests use simulated loopback and fake chunks, covering
empty cells, malformed/oversized frames, fragmented reads, counter resets,
disconnects and D/STOP writes. Temporary recordings are labelled SIMULATED.
The unchanged schema is version 2 with `controller_*` time names. No counter,
checksum, light field or boot message is added.

For `t_ms`, a rough receive-anchored UTC estimate remains:

```text
first_received_unix_s + (t_ms - controller_first_ms) / 1000
```

It includes unknown transport delay/drift. Older metadata needs a separate
migration; no migration is part of this controller change.

[pio]: https://arduino-pico.readthedocs.io/en/latest/platformio.html
[native]: https://docs.platformio.org/en/latest/platforms/native.html
[manual]: https://github.com/OLIMEX/RP2350-PICO2-BB48/blob/main/DOCUMENTS/RP2350-PICO2-BB48-user-manual.pdf
[serial]: https://arduino-pico.readthedocs.io/en/latest/serial.html
[variant]: https://github.com/earlephilhower/arduino-pico/blob/master/variants/olimex_pico2bb48/pins_arduino.h
