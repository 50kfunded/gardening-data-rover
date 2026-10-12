# Prototype 1 parts

**Planned and untested. No hardware milestone has passed.** I'm keeping the
Radxa ZERO 3W bought for £44 including shipping, and choosing the **base
Olimex RP2350-PICO2-BB48 at £14.50, not yet bought**. The C920 is already owned.
There is no assembled or tested rover. Other allowances are rough estimates,
not current delivered quotes, and unknown costs stay unpriced.

| Part | Cost or planning allowance | Status and checks |
| --- | --- | --- |
| Radxa ZERO 3W, 2 GB, fitted 40-pin header, no eMMC planned configuration | £44 paid including shipping | Bought, untested; verify exact variant and header |
| Olimex RP2350-PICO2-BB48 **base** | £14.50 planning price | **Not yet bought, untested**; inspect headers, revision and A2/A4 silicon; not BB48R |
| USB-C data/power cable for BB48 | Not priced; reuse a suitable data cable | Planned; computer USB first, separate bank output later |
| Integral 64 GB microSD and UGREEN SD/microSD reader | Not repriced in this update | Planned choices; genuine card and usable USB reader; not tested |
| Two USB-C male to USB-A female data adapters | Check the spares first; no purchase planned if suitable | One for C920, one for first-boot keyboard; confirm data support |
| USB-A to USB-C Radxa power cable | £3–5 estimate | Bank to USB-C 1; check current rating and voltage drop |
| Micro-HDMI type D to HDMI cable | £4–8 estimate | First boot/recovery; not mini-HDMI |
| USB keyboard | Borrow/reuse | First boot only |
| Small Radxa heatsink | £2–5 estimate | Fit/clearance and temperature untested |
| Inline USB power meter | About £8 planning allowance | Not bought; correct connectors and data pass-through for C920; peak capture ability unknown |
| 2WD chassis, two 1:48 motors, wheels, caster, encoder discs and 4xAA holder | £10–20 estimate | Disc fit, motor ratings, stall current and traction unverified |
| Two LM393 slotted encoder modules, if absent from kit | £2–4 estimate | 3.3 V output/pull-ups; one pulse signal per wheel |
| TB6612FNG driver | £3–5 estimate | Exact module, pull-ups and motor-current limits |
| Seven 4.7 kΩ pull-down resistors, ±5% or better | Not priced; not bought | Proposed and untested; one each for STBY, PWMA/PWMB and four direction inputs; reset-low check required, especially on A2 |
| 100 nF ceramic capacitor for soil ADC | Not priced; not bought | GPIO40 to GND near ADC pin; settling/loading still untested |
| MPU6050 | £2–4 estimate | I2C1 at 3.3 V |
| BME280 | £3–6 estimate | Humidity-capable BME280, not BMP280; 3.3 V I2C |
| Capacitive soil module | £2–4 estimate | Actual timer/regulator, 3.3 V operation and output/reference limits |
| Analog light sensor | Not selected or priced | Reserve GPIO41; output must suit 3.3 V ADC |
| USB power bank | £10–15 old planning allowance | Prefer a checked 5 V/3 A Radxa output, plus separate BB48 output; actual combined limits and stay-on unverified |
| Four AA NiMH cells and matched charger | £10–15 estimate | Motor supply only; polarity/current capability |
| Breadboard, mixed jumpers, 100 µF capacitor, straps and ties | £8–12 estimate | F-F for fitted BB48/Radxa pins; other types for modules; capacitor rating/polarity |
| Spare USB-A bench charger/supply | Reuse spares; no wall charger purchase planned | Check 5 V current rating, cable and stable boot |
| Multimeter | Borrow or £8–12 estimate | Voltage/continuity; required for the bring-up checks |
| Logitech C920 | Already owned | Capture and USB-C 2 current untested |
| DSD TECH SH-U09C5 or 3.3 V USB-to-TTL adapter | Optional fallback, not required for BB48 USB | Radxa console only after its own wiring check; verify 1,500,000 baud and 3.3 V TX; power wire stays disconnected |
| Small USB hub | Not bought; type/price not selected | Optional after milestone 0. Hub+C920+BB48 share the published 500 mA bus budget unless separately powered with checked isolation |

Don't add these estimates into a claimed delivered build price. Components,
tools, mounting, VAT and delivery aren't all known. The £14.50 BB48 figure is
the agreed planning price, not a new live checkout quote.

## Dropped controller orders and ideas

- **NUCLEO-G474RE: cancelled/dropped.** It is not the current controller and
  is not recorded as received or tested. No replacement Nucleo order is planned.
- **ELEGOO ESP32 two-pack / ESP32 order idea: dropped.** It is not needed for
  this build. ESP32-P4 was considered but is not selected either.
- A Micro-B controller cable is no longer the BB48 cable. Keep a spare if
  useful elsewhere; BB48 needs USB-C. The `pi/` folder name stays unchanged.

## Before wiring

The BB48 base has no PSRAM or microSD socket, so GPIO8/9/10/11 are available
for the proposed motor plan. That is not true of BB48R. Check the delivered
labels and headers against [Olimex's schematic][schematic].

The seven 4.7 kΩ pull-downs are proposed motor-off defaults, untested until
measured. Buy ±5% or better: the highest resistance at +5% is 4.935 kΩ,
about 40% below the A2 E9 external pull-down limit of 8.2 kΩ. This checks
the resistor value, not the whole circuit. Keep the A2/A4 silicon check and
measure STBY and every motor input at boot/reset with VM disconnected;
revise the circuit before motor power if logic low isn't assured.
[RP2350 errata][rp2350], [reset checks](wiring.md#motor-driver-and-reset-defaults)

Use BB48 computer USB for the first counter. Later give it its own checked
USB bank lead. Never combine external VSYS with USB; keep Radxa pins 2/4
disconnected until measured and reviewed. A hub is optional now, not needed
to enable controller power. See [the power plan](../docs/power_plan.md).

Secure boards, batteries, camera and leads before floor trials. A breadboard
is a bench tool, not a proven moving-rover power connection. These mechanical
and electrical checks remain planned and untested.

[schematic]: https://github.com/OLIMEX/RP2350-PICO2-BB48/blob/main/HARDWARE/RP2350-PICO2-BB48.REV.A/PICO2-BB48_Rev_A.pdf
[rp2350]: https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008373-DS-2-rp2350-datasheet.pdf
