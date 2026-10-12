# Planned Windows serial check

**Planned and untested. No hardware milestone has passed.** Start with the
[computer checks](software_prep.md), then BB48 on one USB-C data lead from the
computer. Header wires, motor power, sensors and Radxa stay disconnected.
Native USB provides the counter port; no USB-to-TTL adapter is required.
Never add external VSYS or a bank supply alongside computer USB.

| Test or link | Proposed route | Status |
| --- | --- | --- |
| PC counter now, T/D/STOP later | USB-C, native USB `Serial` | Counter only is written; no real board test |
| Radxa later | BB48 UART0 GPIO0 TX to pin 3 RX, GPIO1 RX from pin 5 TX, GND to pin 6 | Planned 3.3 V, 115200 8N1; untested |

`Serial1` maps to UART0 GPIO0/1 in this core. USB and UART are separate.
The current counter emits diagnostic text, not T lines, and ignores D/STOP.
The later protocol transport needs implementing with one command source.
[Core serial documentation][serial], [BB48 variant][variant]

## Finding the port

From the repo root after installing development requirements:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Compare ports before/after plugging in, or use Device Manager. `COM7` below
is only an example; logger port has no default. Upload, RESET or unplug can
remove/change the USB port. Reopen the monitor on the actual running device.
Keep device identifiers out of shared notes.

```powershell
.\.venv\Scripts\python.exe -m platformio device monitor --port COM7 --baud 115200
```

Only after later firmware emits actual T lines, use the hardware logger:

```powershell
.\.venv\Scripts\python.exe -m pi.logger --port COM7 --source hardware --duration 30
```

Invented streams use `--source simulation`. Counter diagnostics aren't sensor
data. Close the logger before a separate sender opens the same port:

```powershell
.\.venv\Scripts\python.exe -m pi.send_command --port COM7 --source hardware STOP
```

**Future pass, pending:** real T lines preserve 11 columns and empty readings,
malformed frames are counted, and resetting the controller splits/stops the
recording visibly. USB disconnect can end the recording rather than split
it automatically. A successful write doesn't prove STOP was received or obeyed.

## Optional adapter test later

A USB-to-TTL adapter is optional for UART0 tests or a separately checked
Radxa debug console. It must be **3.3 V logic**; RS232/DB9 isn't suitable.
With BB48 UART test firmware later, adapter TX goes to GPIO1 RX, adapter RX
to GPIO0 TX, and GND to GND. Keep every adapter power wire disconnected.
Its **5 V pin must never touch a BB48 or Radxa signal pin**. BB48 has one
USB supply; the adapter doesn't power it. This test isn't implemented by
the counter. The optional DSD TECH console mode still needs verification of
1,500,000 baud and its own Radxa wiring instructions.

[serial]: https://arduino-pico.readthedocs.io/en/latest/serial.html
[variant]: https://github.com/earlephilhower/arduino-pico/blob/master/variants/olimex_pico2bb48/pins_arduino.h
