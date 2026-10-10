# tracking prototype 1

use the [repository issues](https://github.com/50kfunded/gardening-data-rover-clean/issues)
and [project board](https://github.com/50kfunded/gardening-data-rover-clean/projects)
to track steps 0–8. the board uses **Todo → In Progress → Done**.
none of the hardware pass tests have passed. the laptop simulation check passes.

0 is Pi setup, followed by build milestones 1–8: nine issues in total.

| step | GitHub issue | pass test |
| --- | --- | --- |
| 0 | [set up the Raspberry Pi](https://github.com/50kfunded/gardening-data-rover-clean/issues/1) | SSH into the actual Pi |
| 1 | [print an ESP32 counter](https://github.com/50kfunded/gardening-data-rover-clean/issues/2) | increasing counter visible over USB serial |
| 2 | [test both motors](https://github.com/50kfunded/gardening-data-rover-clean/issues/3) | forward/reverse at three PWM levels |
| 3 | [count encoder ticks](https://github.com/50kfunded/gardening-data-rover-clean/issues/4) | repeated full turns give consistent counts |
| 4 | [drive straight with PID](https://github.com/50kfunded/gardening-data-rover-clean/issues/5) | 2 m within 10 cm, three consecutive runs |
| 5 | [read the sensors](https://github.com/50kfunded/gardening-data-rover-clean/issues/6) | readings respond sensibly to controlled tests |
| 6 | [log real UART telemetry](https://github.com/50kfunded/gardening-data-rover-clean/issues/7) | clean 30 s hardware CSV; drive/STOP/timeout tested |
| 7 | [capture C920 photos](https://github.com/50kfunded/gardening-data-rover-clean/issues/8) | 20 timestamped photos without motion blur |
| 8 | [complete a combined run](https://github.com/50kfunded/gardening-data-rover-clean/issues/9) | five unattended indoor drive/stop/photo/log cycles; complete folder |

keep every hardware issue in Todo until work begins. move it to Done only after
recording the actual pass evidence. do not close an issue for a simulation result.

soil insertion is manual in prototype 1. the combined run does not establish
automatic soil sampling. readings without valid soil contact stay missing.

project visibility is controlled separately from repository visibility.
see [release tagging](releases.md) after a real milestone passes.
