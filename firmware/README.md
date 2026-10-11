# Nucleo firmware

**Planned and hardware-untested.** The only firmware milestone written is the
USB counter for milestone 1. The documented configuration builds on the
computer, but has not been uploaded or run on a NUCLEO-G474RE. No hardware
milestone has passed.

`platformio.ini` selects `platform = ststm32`, `board = nucleo_g474re`,
`framework = arduino`, `upload_protocol = stlink` and `monitor_speed = 115200`.
The computer build used PlatformIO 6.2.0, ST STM32 platform 20.0.0 and
STM32duino 3.0.0. The platform is not pinned, so check the resolved versions
when building again. See [PlatformIO's board page](https://docs.platformio.org/en/stable/boards/ststm32/nucleo_g474re.html).

In that core's `variant_NUCLEO_G474RE.h`, `Serial` uses LPUART1
(`SERIAL_UART_INSTANCE = 101`), PA2 TX and PA3 RX. ST's default routing
connects these to the ST-LINK virtual COM port. Check the actual board
revision and solder bridges on arrival; do not change them for this milestone.
`src/main.cpp` prints an increasing counter at 115200 baud once a second.
USART1 on D1 / PC4 TX and D0 / PC5 RX is reserved for the later Radxa link
and is not initialised here. There is no motor or sensor code.

The mapping comes from the installed official
[Arduino core variant at 3.0.0](https://github.com/stm32duino/Arduino_Core_STM32/blob/3.0.0/variants/STM32G4xx/G473R%28B-C%29T_G473RETx%28Z%29_G474R%28B-C-E%29T_G483RET_G484RET/variant_NUCLEO_G474RE.h) and
[ST's UM2505, section 7.10 and tables 10/11](https://www.st.com/resource/en/user_manual/um2505-stm32g4-nucleo64-boards-mb1367-stmicroelectronics.pdf).
The [wiring plan](../hardware/wiring.md) reserves the VCP, SWD and SWO pins.

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
.\.venv\Scripts\python.exe -m platformio run -d firmware -e nucleo_g474re
.\.venv\Scripts\python.exe -m platformio test -d firmware -e native
```

The native environment needs a desktop GCC toolchain. Its eight tests use
**SIMULATED DATA and commands only**. They do not measure timing or pass any
hardware milestone. See [the Windows setup notes](../docs/software_prep.md).

When the board arrives, use a data-capable Micro-B USB cable as its only power
source. Leave all header wires disconnected. The
[milestone 1 instructions](../docs/software_prep.md#milestone-1-when-the-nucleo-arrives)
give the upload, serial monitor and pass test. Review the result before
continuing to motor wiring.
