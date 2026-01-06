from __future__ import annotations


def test_accel_import_and_fallback_backend():
    from partitionfinder.accel import add_i64, backend

    # Should always be importable, even without Rust.
    assert backend() in {"python", "rust"}
    assert add_i64(2, 3) == 5
