# Soil calibration plan

Status: planned and untested on hardware. The Python checks use SIMULATED DATA
only. No hardware milestone has passed.

I want repeatable readings before I use them for watering advice or a model.
For now, `moisture_pct` means a relative 0–100 wetness index. Air and water
references do not tell me the percentage of water in soil. Raw `soil_raw`
stays in the existing telemetry, with a blank cell for a missing reading.
The T/D/STOP protocol and metadata schema are unchanged.

## Which sensor I would start with

| Type | What it measures | Fit for the planned rover |
| --- | --- | --- |
| Cheap capacitive PCB | A change in dielectric response | My starting choice for bench work. Covered electrodes avoid passing measurement current directly through exposed soil contacts, but the PCB still needs protection. [DFRobot SEN0193](https://wiki.dfrobot.com/sen0193/) |
| Cheap exposed resistive fork | A change in conductivity | Easy to try, but conductivity also depends on dissolved salts. Exposed electrodes can corrode. I would not choose this for repeated outdoor use. [Comparison study](https://arxiv.org/pdf/2210.03019), [DFRobot](https://wiki.dfrobot.com/sen0193/) |
| Sealed dielectric probe, including commercial FDR/TDR designs | Dielectric response using a more controlled measurement | A later option if the cheap PCB cannot repeat its readings. Soil-specific calibration still matters. I have not selected a model or checked its insertion-force rating. [METER calibration guide](https://publications.metergroup.com/Sales%20and%20Support/METER%20Environment/Website%20Articles/how-calibrate-soil-moisture-sensors.pdf) |
| Tensiometer or granular-matrix sensor | Soil water tension, usually reported in kPa | Useful for plant water availability. These need installation and contact with the soil; I would use them as fixed references rather than assume they work as a quick moving probe. That rover choice is my inference. [IRROMETER](https://www.irrometer.com/sensors.html), [installation FAQ](https://www.irrometer.com/faq.html) |

This is a choice about cost, corrosion and repeatability, not a claim that every
capacitive sensor is more accurate than every resistive sensor. The comparison
study above found different strengths in calibration fit and repeated response.
A thin PCB is also not a tool for forcing through stones. The later slide needs
a depth stop and a way to stop if insertion meets too much resistance. That
mechanism has not been designed or tested.

## What can go wrong with a v1.2 module

The version printed on the board is not enough to identify its circuit.

- Timer and regulator: a first-hand maker report found boards advertised for
  3.3 V arriving with NE555 timers, and regulator headroom problems on some
  variants. It also reported a missing R4 ground connection and slow response.
  These are reports about tested batches, not guaranteed faults on my sensor.
  [Cave Pearl report](https://thecavepearlproject.org/2020/10/27/hacking-a-capacitive-soil-moisture-sensor-for-frequency-output/)
- TI specifies NE555 operation at 5–15 V, while TLC555 supports 2–15 V. An NE555
  is not a part I can assume works at 3.3 V. The exact chip and regulator need
  checking on the delivered board. [NE555](https://www.ti.com/product/NE555),
  [TLC555](https://www.ti.com/product/TLC555)
- Water and wear: the electronics on SEN0193 are not waterproof. The maker
  report also describes exposed cut edges absorbing water and scratches leading
  to corrosion. I will inspect the coating, protect the upper board and cable,
  and recalibrate after any coating change. I will not cover the sensing area
  with a thick unknown layer and assume its response is unchanged.
  [DFRobot calibration notes](https://wiki.dfrobot.com/sen0193/docs/18037),
  [Cave Pearl report](https://thecavepearlproject.org/2020/10/27/hacking-a-capacitive-soil-moisture-sensor-for-frequency-output/)
- Soil contact: insertion depth and packing change the output. Air gaps can
  affect a dielectric reading. Use the same depth and contact each time, and
  avoid a loose oversized hole. [DFRobot](https://wiki.dfrobot.com/sen0193/docs/18037),
  [METER evaluation note](https://library.metergroup.com/Application%20Notes/13492_Calibration%20and%20Evaluation%20of%20an%20Improved%20Low-Cost%20Soil%20Moisture%20Sensor_Print.pdf)
- Soil chemistry and temperature: dielectric calibration can shift with soil
  type, salinity, temperature and bulk density. A moisture reading alone cannot
  separate these effects. I will record temperature and whether feed was added,
  then compare like conditions. I have not found a correction curve for the
  particular generic module that will arrive.
  [METER explanation](https://learning.metergroup.com/courses/water-content/lessons/measuring-water-content/)

## Before connecting the ADC

The proposed controller is NUCLEO-G474RE. About 3.25 V is an assumed ADC reference,
not a measurement from this board. For a 12-bit conversion, the ideal step at
that reference is `3.25 / 4096`, about 0.793 mV. More counts do not automatically
mean better moisture accuracy.

The branded SEN0193 specifies a 3.3–5.5 V supply and 0–3.0 V output. Those limits
are not proof that a generic v1.2 board has the same circuit.
[SEN0193 specifications](https://wiki.dfrobot.com/sen0193/)

With the ADC disconnected, check the delivered sensor's supply requirement,
pin labels and output in air and water. Check the actual reference on the
Nucleo. The planned ADC signal must stay between ground and the measured
reference. A meter will not show every startup spike, so use a scope if there
is one available. Do not feed a 5 V analog signal into this ADC input. Do not
bypass a regulator just because an online example does.

ADC reference stability, source impedance and sample time also affect the
reading. I need to check these during the sensor milestone, including with
motors stopped and then running. This change adds no ADC firmware or wiring.
[ST AN2834](https://www.st.com/resource/en/application_note/an2834-how-to-optimize-the-adc-accuracy-in-the-stm32-mcus-stmicroelectronics.pdf)

## Air and water checks

Use one sensor, one supply and the same cable throughout. Keep a depth mark or
stop below the electronics. Use a non-metal container with room around the
probe and keep it away from the sides and bottom.

1. Clean the probe and let its sensing surface dry completely. Record a settled
   batch in air as the dry reference. Repeat this three times.
2. Put only the permitted sensing section into water, at the marked depth.
   Keep the electronics and connector dry. Record three settled batches as
   the wet reference, including separate removals and insertions.
3. Use the median of the three batch medians for each endpoint. Record the raw
   values, voltage, temperature, supply and depth. Check that the endpoints
   are distinct and repeatable, and repeat the dry check after drying again.

Air/water endpoints follow [DFRobot's procedure](https://wiki.dfrobot.com/sen0193/docs/18037).
Three repeats and the stability checks here are my proposed starting procedure.
Wet residue on a supposed dry probe is not a valid dry reference.

The module calculates:

```text
relative index = 100 * (raw - dry_raw) / (wet_raw - dry_raw)
```

It handles either output direction and clamps the index to 0–100, with a flag
if the reading falls outside the calibrated span. Invalid ADC codes are
rejected instead of being hidden by that clamp.

## Soil samples with known wetness

My starting plan is six moisture levels from dry to very wet, with three
separate insertions at each level. A low-cost sensor study used six soil samples
and three replications. That does not establish a universal number of points
or guarantee accuracy for a different soil.
[Study and method](https://arxiv.org/pdf/2210.03019)

1. Take a mixed soil sample and split it into six labelled non-metal containers.
   Keep the packing, container size and insertion depth consistent. Make sure
   each has enough soil around the whole sensing area.
2. Add increasing measured amounts of water, mix thoroughly and cover the
   containers. I would start with 12–24 hours for redistribution, then check
   for uneven wet patches. That wait is a proposed starting point, not a
   measured settling specification.
3. At each level, take three settled batches at the marked depth. Remove and
   reinsert between batches. Keep temperature similar and note any air gaps.
4. Immediately weigh a representative soil portion after each batch. Record
   the container tare and wet mass. Dry that portion and weigh it again to
   constant mass, subtracting the tare from both masses.

For mineral soil, the gravimetric reference method uses an oven around 105 °C
until constant mass. Use a lab or dedicated soil-drying equipment, not an oven
used for food. High-organic material needs a different drying procedure:
METER warns that 105 °C can lose volatile organics and recommends 60–70 °C for
at least 48 hours for those materials. Record the method and check constant
mass rather than silently treating air-dried soil as zero water.
[University of Arizona method](https://www.extension.arizona.edu/publication/guide-maintaining-and-calibrating-field-installed-soil-and-plant-moisture-sensors),
[METER Method B](https://library.metergroup.com/Sales%20and%20Support/METER%20Environment/Website%20Articles/Method_b-_soil_specific_calibrations_for_meter_soil_moisture_sensors.pdf)

```text
GWC (%) = 100 * (wet soil mass - dry soil mass) / dry soil mass
```

SIMULATED DATA example: 125 g wet soil and 100 g dry soil, with the container
already removed, gives 25% gravimetric water content. This is water mass per
dry soil mass. Volumetric water content also needs measured soil bulk density
or a known bulk sample volume. The relative index is neither of these.
[Gravimetric and volumetric definitions](https://arxiv.org/pdf/2210.03019)

Plot raw batch medians against measured GWC. Look for repeatability, a sensible
direction and curvature. Make one extra independently prepared soil sample
for a later validation check. The current module does not fit a six-point GWC
curve or claim volumetric accuracy. If the response is nonlinear, two endpoints
will not fix it. If no suitable drying equipment is available, use approximate
wetness comparisons and leave measured GWC blank.

## Reading and filtering plan

Start with the rover stationary and motors off. These timings are proposed
bench settings, not verified sensor specifications:

- Wait at least two seconds after power-up or insertion, then inspect repeated
  windows. Accept settling only when three consecutive window medians differ
  by no more than five counts. If it is still moving after 30 seconds, mark the
  attempt unsettled and investigate rather than treating it as a valid reading.
- Start with nine samples from one settled position. At the existing 10 Hz
  telemetry rate, the first to last sample spans 0.8 seconds. Do not combine
  different locations, an insertion transient or a genuine wetting change.
- Use a median and reject isolated spikes with the rule below. Keep the original
  raw rows so rejected values can still be inspected.

The Cave Pearl tests reported roughly one-second startup settling on their
boards, but over 35 seconds for an air-to-water change on faulty variants.
I have not found a dependable settling time for every v1.2 module.
[First-hand report](https://thecavepearlproject.org/2020/10/27/hacking-a-capacitive-soil-moisture-sensor-for-frequency-output/)

Oversampling is a later firmware option. Averaging independent noise can improve
SNR; it cannot remove a wrong reference, salinity bias or poor soil contact.
I would compare 16 conversions per reading with single conversions on the
bench. Any transmitted result must keep the agreed 12-bit raw-count scale.
Nothing in this commit enables ADC oversampling. Sampling waits must later
use a state machine so they do not block motor control.
[ST AN5537](https://www.st.com/resource/en/application_note/an5537-how-to-use-adc-oversampling-techniques-to-improve-signaltonoise-ratio-on-stm32-mcus-stmicroelectronics.pdf)

## What the Python module checks

`analysis/soil_calibration.py` and `analysis/soil_quality.py` are pure functions.
They do not read ports, drive hardware, modify a run or replace raw telemetry.
Calibration endpoints have no defaults. Supply measured values when available.

The outlier rule uses median absolute deviation (MAD). Reject a sample when
its distance from the median exceeds `max(8, 3.5 * MAD / 0.6745)` counts. The
modified Z-score cutoff comes from [NIST](https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm);
the eight-count floor is my starting setting for repeated ADC codes with zero MAD.

| Check | Proposed default | Meaning |
| --- | --- | --- |
| Enough data | At least five retained samples | Otherwise no percentage is returned |
| ADC range | 0–4095; median at either rail is suspect | Invalid input or a rail fault gives no percentage |
| Noise | Original MAD above 20 counts, or over 25% rejected outliers | Flag noisy and reduce confidence, even after filtering |
| Weak calibration | Endpoint span below 200 counts at the default noise limit | Reduce confidence; inspect the references |
| Drift | Either repeated reference shifts by more than 25 counts | Flag drift; do not silently replace the endpoints |
| Stuck | At least 20 challenge samples spanning no more than one count | Only use after deliberately changing the probe from dry to wet |

The stuck challenge must include settled readings before and after the change.
Flat readings in unchanged soil are not automatically a stuck sensor. Noise
can hide a stuck output. Missing or invalid challenge values get their own flag.
Drift needs fresh air/water reference batches taken under matching conditions;
changes between soil locations do not prove sensor drift.

Confidence is a batch-quality score between 0 and 1, not an accuracy claim or
a probability. Before warning penalties, it is:

```text
(samples used / samples supplied) / (1 + (original MAD / noisy MAD limit)^2)
```

The score is multiplied by 0.25 for noise; 0.5 each for drift, clamping or a
weak calibration; and 0.8 each for unchecked drift, an incomplete reference or
an incomplete challenge. An unreliable reference or challenge gives zero
confidence. A missing reading lowers the retained fraction. Invalid readings,
out-of-range codes, ADC rail faults, insufficient data and stuck faults return
no percentage and zero confidence.

These limits need changing if real repeatability tests justify it. A high score
cannot detect consistently bad contact, a wrong reference or a batch where
most samples are corrupted. It does not certify that a sensor is healthy.

## Drift and recalibration

Before each measurement session, repeat the same clean dry-air and water checks.
Log both endpoint shifts, their span and the temperature and supply. A shifted
pair can be an offset problem; a changed span can be a sensitivity problem.
Both need investigation. The default 25-count warning is a proposed threshold,
not the manufacturer's drift specification.

I would check references daily during the first few days and repeat the full
soil procedure weekly while learning how stable the sensor is. Repeat it after
coating, changing sensor, soil, cable, supply or ADC settings, or unexplained
reference drift. This schedule is a starting plan; I have not found a published
recalibration interval for the generic v1.2 module. Do not recalibrate away a
normal drying or watering trend.

## Using the module with an invented example

```python
# SIMULATED DATA ONLY: invented endpoints and readings, no hardware connected.
from analysis.soil_calibration import Calibration, calibrate

calibration = Calibration(dry_raw=3000, wet_raw=1000)
reading = calibrate([1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809], calibration)
print(reading)  # Relative index, quality flags and hardware-untested status.
```

Do not copy these invented endpoints into a real calibration. The tests read
the committed SIMULATED sample and inject invented noise, drift and faults.
They also check the conversion maths, invalid inputs and missing readings.

From the repository root, with the existing development environment active:

```text
python3 -m analysis.check
python3 -m pi.check
python3 -m simulation.check
```

On Windows, use `python` if that is the Python 3 command in the active environment.
No check here uses `-I`. Software passes do not pass a hardware milestone.

## Results template for later

Leave this blank until there are real measurements. Use an anonymous sensor ID
and keep completed raw runs outside the committed sample folder. Do not replace
the SIMULATED sample with sensor data. A completed record must state whether
its readings are real or simulated.

| Setup field | Result |
| --- | --- |
| Data source, date and calibration ID | |
| Sensor ID, board version, timer and regulator markings | |
| Controller, ADC resolution and measured reference voltage | |
| Sensor supply, cable length and coating | |
| Temperature, soil description and feed added | |
| Insertion depth, container size and packing method | |
| Sample interval, settling time, batch size and limits | |
| Dry-air batch medians, MADs and final endpoint | |
| Water batch medians, MADs and final endpoint | |
| Dry/wet repeat shifts, span and challenge result | |
| Drying method and constant-mass check | |
| Validation result, limits found and next check date | |

Use one row per insertion, giving three rows per soil moisture level:

| Level / repeat | Tare g | Wet + container g | Dry + container g | GWC % | Raw median | MAD | Depth | Temperature | Settled / flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | | |

Real sensor behaviour, insertion force, voltage limits, settling time, drift,
soil calibration accuracy and performance with motors are all still untested.
