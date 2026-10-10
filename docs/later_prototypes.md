# photos, video and later soil sampling

**future design notes.** only the laptop simulation exists and its readings
are invented. no rover photos, videos or physical soil samples have been collected.

i want the rover to show how the garden changes over time. photos and soil
observations should refer to the same spots, with enough context to compare
one visit with another. these are design notes; the camera, attachment and
classification have not been tested on the rover.

## the camera for prototype 1

i already have a Logitech C920. Logitech rates it for 1080p at 30 frames per
second, and 720p at 30 frames per second, with autofocus. see
[the C920 specifications](https://www.logitech.com/en-gb/shop/p/c920-pro-hd-webcam).

the first camera milestone will save JPEG photos at 1280 x 720. i will also
compare 1920 x 1080 stills once capture and logging work on the Pi. 1080p has
2.25 times as many pixels as 720p; that alone does not establish sharpness.
the choice needs real photos and a check that the logger keeps working.

for the garden, i want a view of each marked plant or group. leaf details
need a closer view than a whole-bed photograph. i will keep the camera
position, distance and angle repeatable, stop the rover, allow vibration to
settle and check focus before saving. wind can still move the leaves.

where the camera controls allow it, i will use repeatable focus and exposure
settings. brightness and colour can change with the light, so the visit
record needs to say when lighting or settings changed. suitable exposure
still needs checking for the conditions; a single setting may not work all
day. a sharp photo is evidence of appearance, not a confirmed diagnosis.

the existing camera pass test stays: 20 consecutive timestamped photos at
the chosen resolution, with no motion blur. no real photos have passed yet.

## video later

the C920 can supply video as well as still images. prototype 1's capture
milestone is for photos. a later optional step could save short video clips
to show movement, inspect the rover's behaviour or record a visible event.

the camera's advertised frame rate is not a benchmark of this Pi while it
also logs telemetry. before choosing a recording mode, i will check the
formats the actual camera exposes, capture a short clip, measure any frame
loss and check that the sensor log is complete. resolution, frame rate and
compression can then be chosen from the results. no 1080p/30 recording
performance is promised for the combined system.

for gradual plant changes, i can make a time-lapse on the laptop from dated
photos. that is a useful first video result without continuous recording
on the rover. the first build has no wildlife detection or live video feed.

## the first attachment to investigate

prototype 1 uses a soil probe placed by hand. a later attachment could reach
over the bed edge and lower a probe while the wheels stay on the grass.
this measures the soil where it is; it does not collect soil into a container.

the proposed sequence is:

1. stop at an agreed sampling place beside a marked spot.
2. position the probe and lower it to the recorded depth.
3. wait for a stable reading, then save the raw value and sampling context.
4. lift the probe clear before moving again.

a guided slide or small arm is a possible mechanism. the actuator and probe
are not selected yet. the cheap sensing board may not withstand repeated
insertion, and the required force is not known. i need to measure the bed
edge, reach, soil resistance and loaded rover stability before choosing parts.

the mechanism needs travel limits, a way to stop on an obstruction, a known
sampling depth and an accessible place that avoids roots. it must keep the
probe electronics dry. first test repeated insertion and withdrawal while
stationary, then compare its readings with manual placement. an arm reaching
sideways must not tip or drag the rover. these tests are future work.

## collecting actual soil samples

a scoop or hollow sampling tube would remove soil into a labelled container.
that is a separate, more demanding attachment. it would need a sample tray,
reliable collection and release, cleaning between samples, and labels that
keep the place, depth and time attached to each sample. collected soil would
still need an appropriate test to answer a chemical or biological question.

i will investigate probe placement first. physical sampling may need a
larger chassis and a separate budget. it is not included in prototype 1 or
the current shopping list.

## what the labels would mean

moisture, standing water and soil health need separate records. one label
should not be used as a substitute for all three.

| observation | how i would support it |
| --- | --- |
| dry, damp or wet at the probe depth | calibrate the actual probe in this soil, use a consistent depth and validate labels against separate reference observations |
| possibly saturated | compare against suitable wet references; keep uncertainty if the probe cannot distinguish very wet conditions |
| puddle present | record visible standing water separately, initially by human observation; a future camera detector would need labelled examples and checking |
| a soil health concern | record a specific finding supported by the relevant test, such as pH, nutrient levels, drainage or biological activity |
| unknown | use this when placement, calibration or evidence is insufficient |

a dry/damp/wet boundary will come from measurements, not an invented ADC
number. changing the probe, soil or placement can change its response.
[research on low-cost capacitive probes](https://www.mdpi.com/1424-8220/20/12/3585)
describes characterisation in a defined soil rather than a universal scale.
the raw value is not a measured water percentage.

a high moisture reading alone does not identify a surface puddle. prolonged
saturation is also different from a brief puddle after rain. see
[the RHS explanation of waterlogging](https://www.rhs.org.uk/soil-composts-mulches/waterlogging-flooding).

"dead soil" is not a moisture category. soil health involves several physical,
chemical and biological indicators. a moisture probe and a photo cannot
establish all of those. see
[the NRCS explanation of soil health assessment](https://www.nrcs.usda.gov/conservation-basics/soil/soil-health/soil-health-assessment).

## keeping data useful for later analysis

the existing 11 telemetry columns stay as agreed. the future visit record
will link the spot ID, plant, UTC time, photo, valid soil-reading interval,
probe depth and calibration version. later labels also need their evidence
and method: a human observation, a reference measurement or a model estimate.
missing evidence stays unknown.

i can use ordinary Python rules for moisture categories and weekly trends
once the measurements have been checked. AI could later help flag visible
changes or puddles in labelled photos. those estimates need testing on
different visits and review before being used for decisions. soil health
claims still need suitable confirming measurements.

these notes do not start another milestone. S1, choosing three repeatable
garden observation spots, is still the current planning step.
