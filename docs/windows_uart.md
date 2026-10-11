# Planned Windows UART check

**Planned and untested.** No COM-port wiring or hardware logger test has passed.
Use the [software checks](software_prep.md) without hardware first.

For milestone 1, the ESP32's own USB cable is enough. An external adapter is
for a later Serial2 test. The current counter firmware sends no Serial2
telemetry and ignores commands, so an empty logger run is expected with it.
Do not treat that as a sensor or UART milestone pass.

## Wiring for the later adapter test

Switch power off before wiring. Use a **3.3 V logic USB-to-TTL serial adapter**,
not an RS-232 adapter. Confirm its TX logic voltage, not just the voltage of
a selectable power pin. Do not assume a jumper labelled 3V3 changes TX levels.

| Adapter | ESP32 |
| --- | --- |
| TX, 3.3 V logic | GPIO16, RX2 |
| RX | GPIO17, TX2 |
| GND | GND |
| 5 V, VCC, 3V3, DTR and RTS | Leave disconnected |

**The adapter's 5 V pin must never go near an ESP32 pin.** Leave every adapter
power wire disconnected. Power the ESP32 through its own USB cable only.
Do not power it from two sources at once: no power bank/VIN feed alongside
USB, and no adapter power feed. The adapter itself plugs into the computer's
USB port; the only connections between the boards are TX, RX and GND.
Leave the Radxa, driver, motor batteries and sensors disconnected for this test.

TX crosses to RX. Use 115200 baud, 8 data bits, no parity and one stop bit.
GPIO12 is not used. Check the actual labels before fitting the wires.

## Finding the port and running the future logger

From the repository root, after installing the development requirements:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Find the adapter's COM port by comparing the list before and after plugging
it in. Keep USB device identifiers and any local information out of shared
screenshots. Close serial monitors that already have that COM port open.

Only after later firmware produces real T lines on Serial2, replace `COM7`
with the adapter's actual port and run:

```powershell
.\.venv\Scripts\python.exe -m pi.logger --port COM7 --source hardware --duration 30
```

This command is a future hardware check. Do not run it expecting telemetry
from milestone 1. For invented input on any adapter or port, keep the source
as `simulation`; never label a computer-generated stream as hardware data.

For a later sender check, close the logger before opening the same port:

```powershell
.\.venv\Scripts\python.exe -m pi.send_command --port COM7 --source hardware STOP
```

**Future pass test, still pending:** a 30-second real Serial2 stream gives the
same 11 CSV columns, missing sensors stay empty, malformed lines are counted,
and deliberately resetting the ESP32 splits the run with a visible reason.
Verify the real board's command handling separately at milestone 6. A local
successful write alone does not prove that the ESP32 received or obeyed STOP.
