# Photos, video and later soil sampling

**Future design notes.** Only the computer simulation exists and its readings
are invented. No rover photos, videos or physical soil samples have been collected.

I want the rover to show how the garden changes over time. Photos and soil
observations should refer to the same spots, with enough context to compare
one visit with another. These are design notes; the camera, attachment and
classification have not been tested on the rover.

## The camera for Prototype 1

I already have a Logitech C920. Logitech rates it for 1080p at 30 frames per
second, and 720p at 30 frames per second, with autofocus. See
[the C920 specifications](https://www.logitech.com/en-gb/shop/p/c920-pro-hd-webcam).

The first camera milestone will save JPEG photos at 1280 x 720. I will also
compare 1920 x 1080 stills once capture and logging work on the Pi. 1080p has
2.25 times as many pixels as 720p; that alone does not establish sharpness.
The choice needs real photos and a check that the logger keeps working.

For the garden, I want a view of each marked plant or group. Leaf details
need a closer view than a whole-bed photograph. I will keep the camera
position, distance and angle repeatable, stop the rover, allow vibration to
settle and check focus before saving. Wind can still move the leaves.

Where the camera controls allow it, I will use repeatable focus and exposure
settings. Brightness and colour can change with the light, so the visit
record needs to say when lighting or settings changed. Suitable exposure
still needs checking for the conditions; a single setting may not work all
day. A sharp photo is evidence of appearance, not a confirmed diagnosis.

The existing camera pass test stays: 20 consecutive timestamped photos at
the chosen resolution, with no motion blur. No real photos have passed yet.

## Video later

The C920 can supply video as well as still images. Prototype 1's capture
milestone is for photos. A later optional step could save short video clips
to show movement, inspect the rover's behaviour or record a visible event.

The camera's advertised frame rate is not a benchmark of this Pi while it
also logs telemetry. Before choosing a recording mode, I will check the
formats the actual camera exposes, capture a short clip, measure any frame
loss and check that the sensor log is complete. Resolution, frame rate and
compression can then be chosen from the results. No 1080p/30 recording
performance is promised for the combined system.

For gradual plant changes, I can make a time-lapse on the computer from dated
photos. That is a useful first video result without continuous recording
on the rover. The first build has no wildlife detection or live video feed.

## The first attachment to investigate

Prototype 1 uses a soil probe placed by hand. A later attachment could reach
over the bed edge and lower a probe while the wheels stay on the grass.
This measures the soil where it is; it does not collect soil into a container.

The proposed sequence is:

1. Stop at an agreed sampling place beside a marked spot.
2. Position the probe and lower it to the recorded depth.
3. Wait for a stable reading, then save the raw value and sampling context.
4. Lift the probe clear before moving again.

A guided slide or small arm is a possible mechanism. The actuator and probe
are not selected yet. The cheap sensing board may not withstand repeated
insertion, and the required force is not known. I need to measure the bed
edge, reach, soil resistance and loaded rover stability before choosing parts.

The mechanism needs travel limits, a way to stop on an obstruction, a known
sampling depth and an accessible place that avoids roots. It must keep the
probe electronics dry. First test repeated insertion and withdrawal while
stationary, then compare its readings with manual placement. An arm reaching
sideways must not tip or drag the rover. These tests are future work.

## Collecting actual soil samples

A scoop or hollow sampling tube would remove soil into a labelled container.
That is a separate, more demanding attachment. It would need a sample tray,
reliable collection and release, cleaning between samples, and labels that
keep the place, depth and time attached to each sample. Collected soil would
still need an appropriate test to answer a chemical or biological question.

I will investigate probe placement first. Physical sampling may need a
larger chassis and a separate budget. It is not included in Prototype 1 or
the current shopping list.

## What the labels would mean

Moisture, standing water and soil health need separate records. One label
should not be used as a substitute for all three.

| Observation | How I would support it |
| --- | --- |
| Dry, damp or wet at the probe depth | Calibrate the actual probe in this soil, use a consistent depth and validate labels against separate reference observations |
| Possibly saturated | Compare against suitable wet references; keep uncertainty if the probe cannot distinguish very wet conditions |
| Puddle present | Record visible standing water separately, initially by human observation; a future camera detector would need labelled examples and checking |
| A soil health concern | Record a specific finding supported by the relevant test, such as pH, nutrient levels, drainage or biological activity |
| Unknown | Use this when placement, calibration or evidence is insufficient |

A dry/damp/wet boundary will come from measurements, not an invented ADC
number. Changing the probe, soil or placement can change its response.
[Research on low-cost capacitive probes](https://www.mdpi.com/1424-8220/20/12/3585)
describes characterisation in a defined soil rather than a universal scale.
The raw value is not a measured water percentage.

A high moisture reading alone does not identify a surface puddle. Prolonged
saturation is also different from a brief puddle after rain. See
[the RHS explanation of waterlogging](https://www.rhs.org.uk/soil-composts-mulches/waterlogging-flooding).

"Dead soil" is not a moisture category. Soil health involves several physical,
chemical and biological indicators. A moisture probe and a photo cannot
establish all of those. See
[the NRCS explanation of soil health assessment](https://www.nrcs.usda.gov/conservation-basics/soil/soil-health/soil-health-assessment).

## Keeping data useful for later analysis

The existing 11 telemetry columns stay as agreed. The future visit record
will link the spot ID, plant, UTC time, photo, valid soil-reading interval,
probe depth and calibration version. Later labels also need their evidence
and method: a human observation, a reference measurement or a model estimate.
Missing evidence stays unknown.

I can use ordinary Python rules for moisture categories and weekly trends
once the measurements have been checked. AI could later help flag visible
changes or puddles in labelled photos. Those estimates need testing on
different visits and review before being used for decisions. Soil health
claims still need suitable confirming measurements.

These notes do not start another milestone. S1, choosing three repeatable
garden observation spots, is still the current planning step.
