# proposed prototype 1 wiring

**planned and untested.** this is copied from the original brief, with the
ground and mounting details made explicit. check the actual board labels
before connecting power. ESP32 GPIO numbers and Pi physical header pin numbers
are different numbering systems.

## motor driver

| ESP32 / supply | TB6612FNG module |
| --- | --- |
| GPIO25 | PWMA |
| GPIO26 | AIN1 |
| GPIO27 | AIN2 |
| GPIO13 | PWMB |
| GPIO32 | BIN1 |
| GPIO33 | BIN2 |
| GPIO4 | STBY |
| 3V3 | logic VCC |
| AA pack positive, about 4.8 V nominal with four NiMH cells | VM |
| common ground | GND |

connect the left motor to AO1/AO2 and right motor to BO1/BO2. module labels may
use A01/A02 and B01/B02. direction will be checked with the wheels lifted in
milestone 2 and corrected in software if needed.

put the 100 µF capacitor close to the driver across VM and GND. for an
electrolytic capacitor, positive goes to VM and the marked negative lead goes
to GND. choose a voltage rating above the highest battery voltage.

## encoders and sensors

| part | connection |
| --- | --- |
| left LM393 digital output, DO | GPIO34 |
| right LM393 digital output, DO | GPIO35 |
| both encoder modules | VCC to 3V3, GND to common ground |
| MPU6050 and BME280 SDA | GPIO21 |
| MPU6050 and BME280 SCL | GPIO22 |
| both I2C modules | VCC to 3V3, GND to common ground |
| soil sensor analogue output, AO | GPIO39, ADC1 |
| soil sensor supply | VCC to 3V3, GND to common ground |

GPIO34 and GPIO35 are input-only and have no internal pull-ups. check whether
the selected encoder modules already provide a suitable output pull-up; an
open-collector output needs one to 3V3. do not assume `INPUT_PULLUP` fixes this.
I2C pull-ups must also go to 3V3, not 5 V. confirm module supply/output limits.

keep the soil sensor's upper electronics and connector dry. prototype 1 uses
manual probe insertion at a stop; it has no arm, sampler or insertion mechanism.
BME280 measures air conditions, not soil temperature or plant nutrients.

## UART between ESP32 and Pi

| ESP32 | Raspberry Pi Zero 2 W |
| --- | --- |
| TX2, GPIO17 | RXD, GPIO15, physical pin 10 |
| RX2, GPIO16 | TXD, GPIO14, physical pin 8 |
| GND | GND, physical pin 6 |

TX connects to the other board's RX. both use 3.3 V logic. use 115200 baud,
8 data bits, no parity and one stop bit. disable the Pi serial console before
using the UART. avoid ESP32 GPIO12, which is a boot strapping pin.

## power and mounting

- power bank USB output to the Pi's **PWR IN** micro-USB port.
- Pi 5 V, physical pin 2, to the ESP32 board's verified 5 V/VIN input.
- camera to the Pi's **USB data** micro-USB port through the OTG adapter.
- AA pack positive to driver VM; AA negative to the common ground.
- join Pi, ESP32, driver, encoder and sensor grounds together.

the Pi's power supply does not feed driver VM or the motors. verify what VIN
means on the chosen ESP32 DevKit. when using its USB port for programming,
disconnect the Pi-to-ESP32 5 V wire unless the board's documented power circuit
allows both sources; clone boards can differ.

```mermaid
flowchart LR
    bank[USB power bank] --> pi[Pi Zero 2 W: PWR IN]
    pi -->|verified 5 V input| esp[ESP32]
    camera[C920 webcam] -->|OTG USB data| pi
    pi <-->|3.3 V UART: crossed TX / RX| esp
    cells[4 AA NiMH cells] -->|VM| driver[TB6612FNG]
    esp -->|3.3 V logic and PWM| driver
    driver --> motors[two geared motors]
    ground[common GND] --- pi
    ground --- esp
    ground --- driver
    ground --- cells
```

this diagram is proposed wiring, not proof that a powered build has passed.

bolt the Pi and ESP32 to standoffs on the chassis or a top plate. strap the
power bank and battery holder down with velcro and zip ties. attach the C920
to a rigid bracket with a strap or clamp; its monitor clip alone needs checking
on the moving chassis. strain-relieve cables so plugs cannot carry the load.
replace loose breadboard motor-power connections with secure suitable joints
before floor trials. keep the centre of mass low and check stability while
stationary before testing movement.

mounting strength, wheel traction, motor stall current and runtime have not
been measured. these checks belong to the real hardware milestones.

reference: [ESP32 GPIO documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html)
and [Raspberry Pi hardware documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html).
