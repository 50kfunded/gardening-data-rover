# Planning a future trial

**Planning only.** No trial site, observation spots or plants have been selected
or tested. No real readings or photographs have been collected. The only dataset
in Git is the clearly labelled simulation in `data/sample/`.

## What a first trial would try to learn

The proposed aim is repeatable views and measurements over time, then a record
of what changed. Compare a moving camera with fixed sensors before claiming
that movement gives better coverage or measurements.

First pass the indoor hardware tests. A later supervised trial would need a
flat accessible route away from plants. Prototype 1 has no demonstrated outdoor
navigation or weather protection.

## Planning step S1

Choose three possible observation spots and give them anonymous IDs such as
`A`, `B` and `C` in separate trial records. This is future work.

For each proposed spot, record:

- A repeatable rover position and camera view.
- An anonymous plant ID and known species, or `unknown`.
- An accessible probe position that avoids roots.
- Intended probe depth in metres and whether it was reached.
- Whether the loaded rover can reach and stop at that position.

S1 would pass when three spots are practical to revisit using the same method.
It is a planning step, separate from hardware milestones 0–8.

## A future visit

Stop, let the camera settle and capture a timestamped image. Prototype 1 has
no probe actuator, so probe placement would be manual. A reading taken in air
must not be recorded as a valid soil observation.

Save the time, anonymous spot/plant IDs, probe contact and depth, calibration
version, view and lighting notes, and relevant watering or rain observations.
[The dataset plan](dataset_plan.md) describes those proposed visit fields;
the current 11-column simulation does not implement them.

`soil_raw` is an ADC count, not a percentage. Calibration and repeatability
must be measured for the actual probe and soil. BME280 measures air temperature
and humidity. Photographs alone cannot establish nutrient deficiency or disease.

## Records and sharing

Agree collection and sharing permissions before a trial. Keep originals,
permission records and any identification key outside Git. Review any proposed
shared image for identifiable content and location metadata before releasing it.

Weekly trends and a dashboard are future work. The simulation implements neither.
