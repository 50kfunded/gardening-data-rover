# Prototype 1 parts

This is the planned bill of materials, copied from the original brief.
**Nothing has been bought or tested for this build yet.** The ranges below are
rough planning estimates, not checked shop prices, a live basket or a confirmed
total. Delivery, VAT, tools and module quality can change the amount.

| Part | Approximate allowance | What to check before ordering |
| --- | --- | --- |
| Raspberry Pi Zero 2 W, WH with soldered header | £16–22 | The header is fitted; this is the Zero 2 W |
| 32 GB A1 microSD card | £6–8 | Genuine card from a reliable seller |
| Micro-USB OTG adapter | £2–3 | Data adapter for the Pi's USB port |
| ESP32 DevKit, ESP32-WROOM-32 | £5–8 | Classic ESP32, board pin labels and 5 V input |
| 2WD chassis, two 1:48 geared motors, wheels, caster, encoder discs, 4xAA holder | £10–20 | Both discs fit the motors and the wheel size suits the chassis |
| Two LM393 slotted speed sensor modules, if not included | £2–4 | Slots fit the discs; modules work at 3.3 V |
| TB6612FNG motor driver module | £3–5 | Genuine device; motor stall current is within its limits |
| MPU6050 module | £2–4 | 3.3 V I2C compatibility |
| BME280 temperature/humidity module | £3–6 | BME280, not a BMP280 which lacks humidity |
| Capacitive soil moisture sensor | £2–4 | 3.3 V operation and analogue output within ESP32 limits |
| 10,000 mAh USB power bank, at least 2 A output | £10–15 | Suitable output and it stays on at the rover's load |
| Four AA NiMH cells and compatible charger | £10–15 | Cells match; holder polarity and charger suit NiMH |
| Breadboard, M-M/M-F/F-F jumpers, 100 µF capacitor, Velcro and zip ties | £8–12 | Capacitor rating above motor supply; enough mounting materials |
| Multimeter, optional but useful | £8–12 | Continuity and voltage ranges |
| Logitech C920 webcam | Already owned | Test USB capture on the Pi later |

The original aim was roughly £100 for the test platform. These estimates are
not evidence that a working rover can be built for that exact amount.

## Extras to allow for

The brief did not include a USB microSD reader or soldering equipment. A reader
is needed to flash the microSD from a computer without a card slot. A rough
extra allowance is £5–15 for a reader and £10–25 for basic soldering supplies;
these are also unverified estimates. Borrow tools if available.

Allow for a data-capable ESP32 USB cable, a Pi power cable, small standoffs,
screws, a top mounting plate and a camera bracket. The amount depends on what
the chassis kit includes. Soldering and secure cable connections are needed
before driving trials; a loose breadboard alone is a bench setup.

## Buying checks

Check the actual board labels and seller photos before choosing a listing.
Low-cost modules can have different pin layouts or substitute chips. A cheaper
listing is not automatically the correct part, and old prices do not show
present stock or delivery costs. Confirm the final basket before spending.

Keep the USB power bank for the Pi, ESP32 and camera. The AA pack powers the
motors through the driver, with a shared ground. See [proposed wiring](wiring.md).
