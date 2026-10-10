# Raspberry Pi code

Not started. There is no Pi UART logger, camera script or dashboard here yet.
Only the laptop simulation runs at the moment.

The future Pi logger will import the same contract as the simulation:

```python
from shared.data_format import COLUMNS, parse_telemetry
```

Run future Pi modules from the repository root with `python -m pi.<module>`.
The shared contract will stay in `shared/`; it won't need copying into this folder.
