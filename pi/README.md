# Raspberry Pi code

not started. there is no Pi UART logger, camera script or dashboard here yet.
only the laptop simulation runs at the moment.

the future Pi logger will import the same contract as the simulation:

```python
from shared.data_format import COLUMNS, parse_telemetry
```

run future Pi modules from the repository root with `python -m pi.<module>`.
the shared contract will stay in `shared/`; it wont need copying into this folder.
