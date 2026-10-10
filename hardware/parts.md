# prototype 1 parts

this is the planned bill of materials, copied from the original brief.
**nothing has been bought or tested for this build yet.** the ranges below are
rough planning estimates, not checked shop prices, a live basket or a confirmed
total. delivery, VAT, tools and module quality can change the amount.

| part | approximate allowance | what to check before ordering |
| --- | --- | --- |
| Raspberry Pi Zero 2 W, WH with soldered header | £16–22 | the header is fitted; this is the Zero 2 W |
| 32 GB A1 microSD card | £6–8 | genuine card from a reliable seller |
| micro-USB OTG adapter | £2–3 | data adapter for the Pi's USB port |
| ESP32 DevKit, ESP32-WROOM-32 | £5–8 | classic ESP32, board pin labels and 5 V input |
| 2WD chassis, two 1:48 geared motors, wheels, caster, encoder discs, 4xAA holder | £10–20 | both discs fit the motors and the wheel size suits the chassis |
| two LM393 slotted speed sensor modules, if not included | £2–4 | slots fit the discs; modules work at 3.3 V |
| TB6612FNG motor driver module | £3–5 | genuine device; motor stall current is within its limits |
| MPU6050 module | £2–4 | 3.3 V I2C compatibility |
| BME280 temperature/humidity module | £3–6 | BME280, not a BMP280 which lacks humidity |
| capacitive soil moisture sensor | £2–4 | 3.3 V operation and analogue output within ESP32 limits |
| 10,000 mAh USB power bank, at least 2 A output | £10–15 | suitable output and it stays on at the rover's load |
| four AA NiMH cells and compatible charger | £10–15 | cells match; holder polarity and charger suit NiMH |
| breadboard, M-M/M-F/F-F jumpers, 100 µF capacitor, velcro and zip ties | £8–12 | capacitor rating above motor supply; enough mounting materials |
| multimeter, optional but useful | £8–12 | continuity and voltage ranges |
| Logitech C920 webcam | already owned | test USB capture on the Pi later |

the original aim was roughly £100 for the test platform. these estimates are
not evidence that a working rover can be built for that exact amount.

## extras to allow for

the brief did not include a USB microSD reader or soldering equipment. a reader
is needed to flash the microSD from a computer without a card slot. a rough
extra allowance is £5–15 for a reader and £10–25 for basic soldering supplies;
these are also unverified estimates. borrow tools if available.

allow for a data-capable ESP32 USB cable, a Pi power cable, small standoffs,
screws, a top mounting plate and a camera bracket. the amount depends on what
the chassis kit includes. soldering and secure cable connections are needed
before driving trials; a loose breadboard alone is a bench setup.

## buying checks

check the actual board labels and seller photos before choosing a listing.
low-cost modules can have different pin layouts or substitute chips. a cheaper
listing is not automatically the correct part, and old prices do not show
present stock or delivery costs. confirm the final basket before spending.

keep the USB power bank for the Pi, ESP32 and camera. the AA pack powers the
motors through the driver, with a shared ground. see [proposed wiring](wiring.md).
