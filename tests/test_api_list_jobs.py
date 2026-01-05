from __future__ import annotations

from pathlib import Path

import pytest


def test_list_jobs_orders_by_updated_at(tmp_path: Path):
    from partitionfinder.api import service as svc

    svc.store = svc.JobStore(tmp_path / "jobs")

    # Create two fake job metas with different updated_at timestamps.
    meta_old = svc.JobMetadata(
        id="old",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        state="succeeded",
        datatype="DNA",
        input_folder="C:/in/old",
        working_folder="C:/work/old",
        argv=[],
        exit_code=0,
        error=None,
    )

    meta_new = svc.JobMetadata(
        id="new",
        created_at="2026-01-02T00:00:00Z",
        updated_at="2026-01-03T00:00:00Z",
        state="failed",
        datatype="protein",
        input_folder="C:/in/new",
        working_folder="C:/work/new",
        argv=["-p", "1"],
        exit_code=1,
        error="boom",
    )

    svc.store.write_meta(meta_old)
    svc.store.write_meta(meta_new)

    jobs = svc.list_jobs(limit=10)
    assert [j.id for j in jobs] == ["new", "old"]

    # Ensure endpoint model includes metadata for dashboard.
    items = svc.get_jobs(limit=10)
    assert items[0].id == "new"
    assert items[0].datatype == "protein"
    assert items[0].input_folder == "C:/in/new"
