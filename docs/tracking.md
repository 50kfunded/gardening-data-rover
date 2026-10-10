# Tracking Prototype 1

Use the [public Issues page](https://github.com/50kfunded/gardening-data-rover/issues)
to track steps 0–8.
None of the hardware pass tests have passed. The laptop simulation check passes.

0 is Pi setup, followed by build milestones 1–8: nine issues in total.

| Step | GitHub issue | Pass test |
| --- | --- | --- |
| 0 | [Set up the Raspberry Pi](https://github.com/50kfunded/gardening-data-rover/issues/1) | SSH into the actual Pi |
| 1 | [Print an ESP32 counter](https://github.com/50kfunded/gardening-data-rover/issues/2) | Increasing counter visible over USB serial |
| 2 | [Test both motors](https://github.com/50kfunded/gardening-data-rover/issues/3) | Forward/reverse at three PWM levels |
| 3 | [Count encoder ticks](https://github.com/50kfunded/gardening-data-rover/issues/4) | Repeated full turns give consistent counts |
| 4 | [Drive straight with PID](https://github.com/50kfunded/gardening-data-rover/issues/5) | 2 m within 10 cm, three consecutive runs |
| 5 | [Read the sensors](https://github.com/50kfunded/gardening-data-rover/issues/6) | Readings respond sensibly to controlled tests |
| 6 | [Log real UART telemetry](https://github.com/50kfunded/gardening-data-rover/issues/7) | Clean 30 s hardware CSV; drive/STOP/timeout tested |
| 7 | [Capture C920 photos](https://github.com/50kfunded/gardening-data-rover/issues/8) | 20 timestamped photos without motion blur |
| 8 | [Complete a combined run](https://github.com/50kfunded/gardening-data-rover/issues/9) | Five unattended indoor drive/stop/photo/log cycles; complete folder |

Keep each hardware issue open while work is pending. Close it only after
recording the actual pass evidence. Do not close an issue for a simulation result.

Soil insertion is manual in Prototype 1. The combined run does not establish
automatic soil sampling. Readings without valid soil contact stay missing.

See [release tagging](releases.md) after a real milestone passes.
