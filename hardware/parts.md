# Prototype 1 parts

I'm planning Prototype 1 around the Radxa ZERO 3W and ESP32.
**I've bought the Radxa board for £44 including shipping. No hardware has been
tested or assembled into a rover.** The C920 is already owned. The other figures
are rough planning estimates, not checked shop prices, a live basket or a confirmed
total. Delivery on the remaining orders, VAT, tools and module quality can change
the amount.

| Part | Cost or planning allowance | What to check |
| --- | --- | --- |
| Radxa ZERO 3W, planned configuration: 2 GB, soldered 40-pin header, no eMMC | £44 paid, including shipping | Bought, not tested. Check the exact variant and fitted header before wiring |
| 32 GB A1 microSD card | £6–8 | Genuine card from a reliable seller |
| USB microSD reader | £5–15 | Reads microSD and fits the computer's USB port |
| Two data-capable USB-C male to USB-A female adapters | £4–8 for both | One for the C920 and one for a USB keyboard on USB-C 2 at different times |
| USB-A to USB-C power cable | £3–5 | Power bank to the Radxa's USB-C 1; suitable for the planned 5 V / 2 A supply |
| Micro-HDMI (type D) to HDMI cable | £4–8 | First boot and recovery with a monitor; not mini-HDMI |
| USB keyboard | Borrow if possible; purchase price not estimated | USB connection for first boot |
| Small heatsink for the Radxa | £2–5 | Heatsink fit and clearance have not been verified |
| Inline USB power meter | About £8 | Matching connectors; data passes through when measuring the C920 |
| ESP32 DevKit, ESP32-WROOM-32 | £5–8 | Classic ESP32, board pin labels and 5 V input |
| Data-capable ESP32 USB cable | Not priced yet | Check whether the exact board uses micro-USB or USB-C; a charging-only cable will not program it |
| 2WD chassis, two 1:48 geared motors, wheels, caster, encoder discs, 4xAA holder | £10–20 | Both discs fit the motors and the wheel size suits the chassis |
| Two LM393 slotted speed sensor modules, if not included | £2–4 | Slots fit the discs; modules work at 3.3 V |
| TB6612FNG motor driver module | £3–5 | Genuine device; motor stall current is within its limits |
| MPU6050 module | £2–4 | 3.3 V I2C compatibility |
| BME280 temperature/humidity module | £3–6 | BME280, not a BMP280 which lacks humidity |
| Capacitive soil moisture sensor | £2–4 | 3.3 V operation and analogue output within ESP32 limits |
| 10,000 mAh USB power bank, at least 5 V / 2 A on the output feeding the Radxa | £10–15 | Ideally two outputs so the ESP32 has its own lead; check per-output limits and that it stays on at the actual load |
| Four AA NiMH cells and compatible charger | £10–15 | Cells match; holder polarity and charger suit NiMH |
| Breadboard, mostly F-F jumpers plus some M-F/M-M, 100 µF capacitor, Velcro and zip ties | £8–12 | The Radxa and ESP32 headers are male pins, so most jumpers will be female-to-female; capacitor rating above motor supply |
| 5 V / 3 A USB bench supply | £6–15 | Radxa recommends its Power PD30W adapter. This allowance is not a verified price for that model |
| Multimeter, optional but useful | £8–12 | Continuity and voltage ranges |
| 3.3 V USB-serial adapter, optional first-boot fallback | £5–10 | Must support 1,500,000 baud and 3.3 V logic; do not connect its power wire to the board |
| Logitech C920 webcam | Already owned | Test USB capture on the Radxa's USB-C 2 later |

**Rough estimate for the priced, non-optional rows, including the bought board: about £140–210.**
The £44 board cost and remaining allowances add up to £137–209 before rounding.
This assumes a borrowed keyboard, the existing C920 and separate LM393 modules.
It excludes the optional
multimeter and USB-serial adapter, the unpriced ESP32 cable, soldering supplies,
any extra mounting parts and delivery on the remaining orders. The board's
shipping is already included. If the kit includes the LM393 sensors,
I can remove their separate allowance. This is not a confirmed total.

The original aim was roughly £100 for the test platform. The updated estimate
doesn't show that a working rover can be built for that exact amount.

## Extras to allow for

The USB microSD reader is included above because the computer needs one to flash
the card. Basic soldering supplies could add another £10–25, also an unverified
estimate outside the subtotal above. I'll borrow tools if possible.

The ESP32 USB cable still needs pricing. Small standoffs, screws, a top mounting
plate and a camera bracket may add more, depending on what the chassis kit
includes. Soldering and secure cable connections are needed before driving
trials; a loose breadboard alone is a bench setup.

## Buying checks

Check the actual board labels and seller photos before choosing a listing.
Low-cost modules can have different pin layouts or substitute chips. A cheaper
listing is not automatically the correct part, and old prices do not show
present stock or delivery costs. Confirm the final basket before spending.

The USB-C adapters must carry data. The HDMI cable must be micro-HDMI (type D),
not mini-HDMI. I won't buy a powered USB hub unless the C920 misbehaves on
USB-C 2. Radxa recommends its Power PD30W in the
[preparation guide](https://docs.radxa.com/en/zero/zero3/getting-started/preparation).

I won't assume the Radxa's mounting holes match a Pi Zero. Mounting hole spacing
and heatsink fit still need checking; see the [logic board plan](../docs/logic_board.md).

The power bank feeds the Radxa through USB-C 1, with a separate USB lead for the
ESP32 at first. The AA pack powers only the motors through the driver, with a
shared ground. The [existing wiring document](wiring.md) still describes the
earlier Pi plan and needs a Radxa update before use.
