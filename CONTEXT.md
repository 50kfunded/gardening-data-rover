# project context

## what exists

only a laptop simulation is implemented. it generates 300 invented snapshots
over 30 virtual seconds at 10 Hz, writes CSV and JSON, and verifies them.
the readings are SIMULATED DATA, not hardware or garden observations.

S0, the software preparation step, passed on 9 October 2026. the reorganised
check passes too. Pi setup (0) and hardware steps 1–8 are all pending.
firmware, the Pi logger/camera code, PID, Kalman filtering and AI are not started.

## folder roles

- `shared/data_format.py`: the 11-column schema and line parser.
- `simulation/`: invented ESP32 lines, file generation and pass/fail checks.
- `analysis/`: reads and summarises the simulated files, with no AI inference.
- `firmware/` and `pi/`: clearly marked placeholders.
- `hardware/`: proposed parts, wiring and mounting, all untested.
- `data/sample/`: small labelled simulation; no real private data.
- `docs/`: planned milestones, data contract, trial method and future ideas.

from the repository root, run `python -m simulation.check`. Python 3.12 was
used for verification; no third-party Python packages are required.

## planned architecture

ESP32-WROOM-32 handles motors, encoder interrupts and sensors with a 100 Hz
control loop. Pi Zero 2 W handles UART logging, drive commands and a USB C920
camera. UART is proposed at 115200 baud with text lines. telemetry begins at
10 Hz, separately from the control update rate.

wheel command units are rad/s. encoder values are raw cumulative counts,
not signed positions. soil values are raw ADC counts, not moisture percent.
unavailable sensor fields stay blank and unknown calibration stays `null`.
see [the contract](docs/data_contract.md) before changing a field or unit.

motor power is a separate AA pack; the logic/camera power bank shares ground.
the Pi's one USB data port is for the camera. proposed GPIO assignments are
in [hardware/wiring.md](hardware/wiring.md), not an as-built record.

## boundaries for the first build

start with indoor tests. garden movement has not been proved. soil insertion
is manual, so unattended movement does not imply automatic soil sampling.
train any later image model on a computer using reviewed real observations;
invented simulation values are only useful for exercising the pipeline.

teach one milestone at a time, with exact code for the verified parts, wiring
and a pass/fail test. explain the maths and ask for results before continuing
to the next build milestone. future roadmaps are estimates, not instructions
to skip those tests.

## sharing

use the [publication checklist](docs/publication.md) before sharing a snapshot.
keep source-only commits, a GitHub noreply identity and labelled invented examples.
do not add credentials, identifiable records or raw photographs to Git.
normal runs, environments and local screenshots stay ignored.
