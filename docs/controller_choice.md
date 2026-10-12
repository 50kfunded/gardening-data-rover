# Controller choice

**Planned and untested. No hardware milestone has passed.** I've picked the
base Olimex RP2350-PICO2-BB48, with a £14.50 planning price, not yet bought.
Radxa ZERO 3W stays the computer. BB48 will handle motor signals, wheel pulses,
sensors and later actuators; video and navigation stay on Radxa.

## Why this board

Olimex lists 48 exposed GPIOs, 520 KB SRAM, 16 MB flash and USB-C on the base
board. That gives room to plan the controller and later connections at a
lower planning cost than the larger development boards. This is a fit for
proposed work, not a benchmark or proof every future feature fits.
[Olimex specifications][olimex]

Base BB48 has no PSRAM or microSD socket. BB48R adds those parts and uses
pins in our motor plan, so it isn't a drop-in swap. The proposed
[wiring](../hardware/wiring.md) is for the base. Headers and delivered revision
still need inspection.

## Alternatives considered

| Option | Why I didn't choose it for this build |
| --- | --- |
| NUCLEO-G474RE | Useful motor timers and built-in debugging, but the order was cancelled and the plan is dropped. Its board-specific power procedure no longer belongs in this wiring plan. [ST board][nucleo] |
| ESP32-P4-WIFI6-M | More processing/connectivity features, but Radxa already owns the camera/network job. Revision, pin sharing and the P4 toolchain add open checks without an established need here. [Waveshare][p4] |
| Raspberry Pi Pico 2 | Same RP2350 family, but fewer exposed GPIOs than BB48. [Pico 2][pico] |
| Teensy 4.1 | Fast, with many interfaces, but the extra cost/performance isn't an established P1 requirement. [PJRC][teensy] |
| Original ESP32 DevKit idea | Dropped. The ESP32 order idea isn't in the current parts plan; missed encoder pulses on our rover were never tested. |

These alternatives weren't tested against each other. CPU clock speed
doesn't prove encoder accuracy, soil accuracy or a better camera stream.

## Open checks

- Confirm base BB48, fitted headers, board revision and **A2 versus A4** silicon.
- A2 has E9 GPIO input leakage; A4 fixes it. Check ADC pad configuration and
  readings with motors off/on. Don't promise a noise-free ADC.
- Test seven proposed 4.7 kΩ driver pull-downs (±5% or better) at
  boot/reset/BOOT/USB disconnect with VM disconnected. At +5%, 4.935 kΩ is
  about 40% below E9's 8.2 kΩ limit. The value remains planned and untested
  until measured; revise the circuit before motor power if low isn't assured.
  [Errata][rp2350], [A4 announcement][a4]
- Check USB upload/counter, whole-board current and bank stay-on.
- Test UART0 GPIO0/1 to Radxa UART3-M0, including resets and disconnects.
- Review PWM/I2C connector sharing and every later actuator circuit.
- PIO counting, production PCB, environmental protection and remote updates
  remain future work. Final-product suitability hasn't been proved.

Native tests and the computer build check software only. The 11 telemetry
columns, missing-reading rules, T/D/STOP and metadata schema stay unchanged.
No light column, checksum or extra counter is added.

[olimex]: https://www.olimex.com/Products/RaspberryPi/PICO/RP2350-PICO2-BB48/open-source-hardware
[nucleo]: https://www.st.com/en/evaluation-tools/nucleo-g474re.html
[p4]: https://www.waveshare.com/esp32-p4-wifi6.htm
[pico]: https://www.raspberrypi.com/products/raspberry-pi-pico-2/
[teensy]: https://www.pjrc.com/store/teensy41.html
[rp2350]: https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008373-DS-2-rp2350-datasheet.pdf
[a4]: https://www.raspberrypi.com/news/rp2350-a4-rp2354-and-a-new-hacking-challenge/
