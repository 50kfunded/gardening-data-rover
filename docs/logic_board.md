# Logic board plan

I've bought the Radxa ZERO 3W for £44 including shipping. The planned configuration
is 2 GB RAM, a soldered 40-pin header and microSD boot, without eMMC; the exact
variant still needs checking. The board has not been tested. Only the computer
simulation runs, and all hardware milestones are still pending.

The earlier £31 allowance came from a listing seen on 10 Oct 2026 with stock
unconfirmed. The £44 paid cost replaces that estimate. The other prices in the
[parts list](../hardware/parts.md) are still unverified planning allowances.

## Open questions to check on the hardware

- Mounting hole spacing and heatsink fit not verified. I won't assume the holes
  match a Pi Zero. Check the actual board, heatsink clearance and mounting parts
  before choosing a bracket or top plate.

- UART3-M0's device name is expected to be `/dev/ttyS3`, but is unconfirmed.
  Check the selected overlay and that no console or getty uses the port.
- Header 5 V, C920 current, power bank behaviour and headless WiFi still need
  the [milestone 0 checks](plan.md#milestone-0-checks-before-wiring).

The [wiring plan](../hardware/wiring.md) now uses Radxa USB power and UART3-M0.
It is planned and untested. Keep the BB48 on its own USB lead and do not use
header pins 2/4 as its power supply before measurement and supply-path checks.
