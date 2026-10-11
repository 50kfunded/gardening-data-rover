# Planned Windows serial check

**Planned and untested.** No COM-port test or hardware logger test has passed.
Use the [software checks](software_prep.md) without hardware first.

For milestone 1, connect a data-capable Micro-B USB cable from the computer
to CN1 on the NUCLEO-G474RE. Its built-in ST-LINK provides programming and a
virtual COM port, so no external USB-to-TTL adapter or header wiring is needed.
Leave the Radxa, driver, batteries and sensors disconnected. Use only the
computer USB supply; do not add a power bank or header supply at the same time.
Check the actual revision and default routing before use.

The current counter firmware sends diagnostic text, not T telemetry, and
ignores D/STOP commands. It cannot produce a valid telemetry recording.
Counter output being rejected by the logger is expected, not a hardware pass.

## Planned protocol routes

| Test or link | Route | Status |
| --- | --- | --- |
| PC counter now; D/STOP and T lines in later firmware | CN1 Micro-B USB, ST-LINK VCP, LPUART1 PA2 TX / PA3 RX | Planned and hardware-untested; only counter firmware is written |
| Radxa in the later UART milestone | USART1 D1 / PC4 TX to Radxa pin 3 RX; D0 / PC5 RX from Radxa pin 5 TX; GND to Radxa pin 6 | Planned and untested |

The installed STM32duino 3.0.0 core maps `Serial` to LPUART1 on PA2/PA3.
ST's manual describes this default ST-LINK route separately from USART1 on
D1/D0. Do not move solder bridges to use the PC test. Check on the board
that its revision has the documented default routing.

The later PC test will use the **same** `D,left,right`, `STOP` and T-line
protocol as USART1, at 115200 baud, 8 data bits, no parity and one stop bit.
That firmware transport is still to be written. Do not forward unrelated
counter text into the telemetry CSV or enable two command sources together.

## Finding the port and running the future logger

From the repository root, after installing the development requirements:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
```

Find the ST-LINK VCP by comparing the list before and after plugging the board
in, or inspect Device Manager. `COM7` below is only an example. The logger's
port has no default. Keep device identifiers and local information out of
shared screenshots. Close serial monitors that already have that port open.

Only after later firmware produces real T lines on the VCP, use the actual port:

```powershell
.\.venv\Scripts\python.exe -m pi.logger --port COM7 --source hardware --duration 30
```

This is a future hardware check. For invented input on any port, use
`--source simulation`; never label a computer-generated stream as hardware data.

For a later sender check, close the logger before opening the same port:

```powershell
.\.venv\Scripts\python.exe -m pi.send_command --port COM7 --source hardware STOP
```

**Future pass test, still pending:** a 30-second real T stream gives the same
11 CSV columns, missing readings stay empty, malformed lines are counted,
and deliberately resetting the Nucleo splits the run with a visible reason.
Test command handling separately at milestone 6. A successful local write
alone does not prove that the Nucleo received or obeyed STOP.

The optional DSD TECH SH-U09C5 remains a possible **Radxa debug-console
fallback**, not a required PC-to-Nucleo adapter. Before using it, verify its
TX logic is 3.3 V and that it supports the Radxa console's 1,500,000 baud.
Keep every adapter power wire disconnected. A 5 V adapter pin must never
connect to a Nucleo or Radxa signal pin. PA3 and PC5 are not 5 V tolerant.
Its Radxa console wiring needs its own checked instructions before use.

Sources: [ST UM2505, sections 3.1, 7.4 and 7.10](https://www.st.com/resource/en/user_manual/um2505-stm32g4-nucleo64-boards-mb1367-stmicroelectronics.pdf)
and [STM32G474 datasheet, table 12](https://www.st.com/resource/en/datasheet/stm32g474re.pdf).
