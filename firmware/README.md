# BB48 firmware

**Planned and hardware-untested. No hardware milestone has passed.** The base
Olimex RP2350-PICO2-BB48 replaces the earlier controller plans. Milestone 1
only prints an increasing counter once a second on native USB `Serial`.
There are no motor, encoder, sensor or live protocol transports yet.

```ini
[env:olimex_pico2bb48]
platform = https://github.com/maxgerhardt/platform-raspberrypi.git
board = olimex_pico2bb48
framework = arduino
monitor_speed = 115200
```

The [board definition][board] selects Arduino-Pico and `picotool` upload.
`Serial` is native USB; 115200 is the monitor setting, not a USB bit clock.
`Serial1` is UART0 GPIO0 TX / GPIO1 RX for the later Radxa link and stays
uninitialised now. `Wire1` GPIO2/3 is reserved for later I2C sensors.
[USB/UART documentation][serial], [BB48 variant][variant]

The Git platform URL is intentionally not pinned. Record resolved platform,
core and toolchain versions on each build. A computer build is not an upload,
hardware result or milestone pass.

From the repository root, after [software setup](../docs/software_prep.md):

```powershell
.\.venv\Scripts\python.exe -m platformio run -d firmware -e olimex_pico2bb48
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
```

The native environment and `lib/rover_protocol/` are unchanged. Its eight
tests use **SIMULATED DATA and commands only**. Pure helpers retain T-line
formatting, empty missing readings, 256-byte maximum and D/STOP parsing.
They don't run a control loop or make STOP operate a motor.

On arrival, use one USB-C data lead from the computer with header wires and
motor power disconnected. Follow [milestone 1](../docs/software_prep.md#milestone-1-when-the-bb48-arrives)
to upload and watch the counter. Identify the actual USB COM port; examples
aren't defaults. BOOT/RESET can enter the ROM uploader; the running serial
port may disappear/change on upload/reset. Check this on the board. No
separate UART adapter is required for the planned USB counter.

The [pin plan](../hardware/wiring.md) is for base BB48, not BB48R. Check silicon
revision and motor-off pull-down behaviour before later wiring. Keep ADC
resolution at 12 bits when that milestone is implemented.

[board]: https://github.com/maxgerhardt/platform-raspberrypi/blob/develop/boards/olimex_pico2bb48.json
[serial]: https://arduino-pico.readthedocs.io/en/latest/serial.html
[variant]: https://github.com/earlephilhower/arduino-pico/blob/master/variants/olimex_pico2bb48/pins_arduino.h
