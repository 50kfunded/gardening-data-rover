# Prototype 1 parts

I'm planning Prototype 1 around the Radxa ZERO 3W and NUCLEO-G474RE.
**I've bought the Radxa board for £44 including shipping. No hardware has been
tested or assembled into a rover.** The NUCLEO-G474RE was ordered from Anglia
on 11 October 2026 at a listed £11.98 ex VAT. It has not arrived or been
tested, and the VAT-inclusive invoice total is not confirmed. The C920 is
already owned. The other figures are rough planning estimates, not checked shop prices, a live basket or a confirmed
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
| ST NUCLEO-G474RE, real-time controller | £11.98 ex VAT listing; invoice total unconfirmed | Ordered from Anglia on 11 October 2026, not arrived or tested; check board revision |
| Data-capable Micro-B USB cable for the Nucleo | Not priced yet; reuse a suitable cable if possible | Computer or separate bank output to CN1; ST-LINK programming and virtual COM port |
| 2WD chassis, two 1:48 geared motors, wheels, caster, encoder discs, 4xAA holder | £10–20 | Both discs fit the motors and the wheel size suits the chassis |
| Two LM393 slotted speed sensor modules, if not included | £2–4 | Slots fit the discs; modules work at 3.3 V |
| TB6612FNG motor driver module | £3–5 | Genuine device; motor stall current is within its limits |
| MPU6050 module | £2–4 | 3.3 V I2C compatibility |
| BME280 temperature/humidity module | £3–6 | BME280, not a BMP280 which lacks humidity |
| Capacitive soil moisture sensor | £2–4 | 3.3 V operation and analogue output within the measured ADC reference and Nucleo limits |
| 10,000 mAh USB power bank, at least 5 V / 2 A on the output feeding the Radxa | £10–15 | Ideally two outputs so the Nucleo has its own lead; check per-output limits and that it stays on at the actual load |
| Four AA NiMH cells and compatible charger | £10–15 | Cells match; holder polarity and charger suit NiMH |
| Breadboard, mixed F-F/M-F/M-M jumper pack, 100 µF capacitor, Velcro and zip ties | £8–12 | F-F for Radxa/morpho male pins; M-F for Arduino female sockets to male pins; capacitor rating above motor supply |
| 5 V / 3 A USB bench supply | £6–15 | Radxa recommends its Power PD30W adapter. This allowance is not a verified price for that model |
| Multimeter, optional but useful | £8–12 | Continuity and voltage ranges |
| DSD TECH SH-U09C5 or suitable 3.3 V USB-serial adapter, optional Radxa console fallback | £5–10 planning allowance, exact price unconfirmed | Verify 1,500,000 baud and TX logic voltage; power wire disconnected. Not needed for the Nucleo VCP |
| Logitech C920 webcam | Already owned | Test USB capture on the Radxa's USB-C 2 later |

**Rough planning subtotal for the other priced, non-optional rows: £132–201,
including the £44 Radxa. Add the Nucleo invoice total once it is confirmed.**
The Nucleo listing was £11.98 ex VAT; its VAT-inclusive total and delivery are
not confirmed here. I am not treating that listing as a delivered price.
This subtotal assumes a borrowed keyboard, the existing C920 and separate
LM393 modules. It excludes the optional multimeter and USB-serial adapter,
the unpriced Micro-B cable, soldering supplies, extra mounting parts and
delivery on the remaining orders. The Radxa shipping is already included.
This is a planning allowance, not a confirmed whole-build total.
If the chassis includes the LM393 sensors, remove their separate allowance.

The original aim was roughly £100 for the test platform. The updated estimate
doesn't show that a working rover can be built for that exact amount.

## Extras to allow for

The USB microSD reader is included above because the computer needs one to flash
the card. Basic soldering supplies could add another £10–25, also an unverified
estimate outside the subtotal above. I'll borrow tools if possible.

The Micro-B data cable still needs pricing. Small standoffs, screws, a top mounting
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
Nucleo at first. Check its standalone USB power-source selection on the
actual board revision before moving any jumper; the manual uses inconsistent
JP2/JP5 names. The AA pack powers only the motors through the driver, with a
shared ground. The [planned wiring](wiring.md) now records the Radxa power
and UART connections. It is untested; do the milestone 0 board checks before
connecting the UART.

The built-in ST-LINK replaces the need for a separate programmer and PC UART
adapter. The previous two-pack controller is no longer on the planned list.
Nothing here confirms module compatibility, standalone power or a hardware pass.
See [ST UM2505](https://www.st.com/resource/en/user_manual/um2505-stm32g4-nucleo64-boards-mb1367-stmicroelectronics.pdf)
for Micro-B USB, connector types and power-source checks.
