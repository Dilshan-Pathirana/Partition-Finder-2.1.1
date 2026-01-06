# Rust acceleration (optional)

This folder contains **optional** Phase 4 performance scaffolding.

PartitionFinder runs normally without Rust.

## Build (optional)

Prereqs:
- Rust toolchain (MSVC on Windows)
- Python venv activated

From the repo root:

```powershell
cd rust\pf_accel
pip install maturin
maturin develop --release
```

This builds and installs a native extension at `partitionfinder.accel._pf_accel`.

## Verify

In Python:

```python
from partitionfinder.accel import backend, add_i64
print(backend())
print(add_i64(1, 2))
```

If the extension is not installed, `backend()` returns `"python"` and everything still works.
