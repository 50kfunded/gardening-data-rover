# planning a future trial

**planning only.** no trial site, observation spots or plants have been selected
or tested. no real readings or photographs have been collected. the only dataset
in Git is the clearly labelled simulation in `data/sample/`.

## what a first trial would try to learn

the proposed aim is repeatable views and measurements over time, then a record
of what changed. compare a moving camera with fixed sensors before claiming
that movement gives better coverage or measurements.

first pass the indoor hardware tests. a later supervised trial would need a
flat accessible route away from plants. prototype 1 has no demonstrated outdoor
navigation or weather protection.

## planning step S1

choose three possible observation spots and give them anonymous IDs such as
`A`, `B` and `C` in separate trial records. this is future work.

for each proposed spot, record:

- a repeatable rover position and camera view.
- an anonymous plant ID and known species, or `unknown`.
- an accessible probe position that avoids roots.
- intended probe depth in metres and whether it was reached.
- whether the loaded rover can reach and stop at that position.

S1 would pass when three spots are practical to revisit using the same method.
it is a planning step, separate from hardware milestones 0–8.

## a future visit

stop, let the camera settle and capture a timestamped image. prototype 1 has
no probe actuator, so probe placement would be manual. a reading taken in air
must not be recorded as a valid soil observation.

save the time, anonymous spot/plant IDs, probe contact and depth, calibration
version, view and lighting notes, and relevant watering or rain observations.
[the dataset plan](dataset_plan.md) describes those proposed visit fields;
the current 11-column simulation does not implement them.

`soil_raw` is an ADC count, not a percentage. calibration and repeatability
must be measured for the actual probe and soil. BME280 measures air temperature
and humidity. photographs alone cannot establish nutrient deficiency or disease.

## records and sharing

agree collection and sharing permissions before a trial. keep originals,
permission records and any identification key outside Git. review any proposed
shared image for identifiable content and location metadata before releasing it.

weekly trends and a dashboard are future work. the simulation implements neither.
