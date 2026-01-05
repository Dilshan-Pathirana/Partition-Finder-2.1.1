from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the local package is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_delete_job_removes_artifacts(tmp_path: Path):
    from partitionfinder.api import service as svc

    svc.store = svc.JobStore(tmp_path / "jobs")

    # Create a fake job
    meta = svc.JobMetadata(
        id="test123",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        state="succeeded",
        datatype="DNA",
        input_folder="C:/in",
        working_folder="C:/work",
        argv=[],
        exit_code=0,
        error=None,
    )
    svc.store.write_meta(meta)
    svc.store.append_log("test123", "Sample log line")

    # Verify it exists
    assert svc.store.exists("test123")
    assert svc.store.log_path("test123").exists()

    # Delete it
    result = svc.delete_job("test123")
    assert result["status"] == "deleted"
    assert result["job_id"] == "test123"

    # Verify removed
    assert not svc.store.exists("test123")
    assert not svc.store.job_dir("test123").exists()


def test_delete_running_job_raises_409(tmp_path: Path):
    from partitionfinder.api import service as svc
    from fastapi import HTTPException

    svc.store = svc.JobStore(tmp_path / "jobs")

    meta = svc.JobMetadata(
        id="running123",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        state="running",
        datatype="DNA",
        input_folder="C:/in",
        working_folder="C:/work",
        argv=[],
    )
    svc.store.write_meta(meta)

    with pytest.raises(HTTPException) as exc_info:
        svc.delete_job("running123")
    
    assert exc_info.value.status_code == 409
    assert "running" in exc_info.value.detail.lower()


def test_validate_input_folder_checks_cfg_file(tmp_path: Path):
    from partitionfinder.api import service as svc

    # Empty folder should fail
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()

    with pytest.raises(ValueError, match="No .cfg file found"):
        svc._validate_input_folder(empty_folder)

    # Folder with .cfg should pass
    valid_folder = tmp_path / "valid"
    valid_folder.mkdir()
    (valid_folder / "partition_finder.cfg").write_text("# mock config")

    svc._validate_input_folder(valid_folder)  # Should not raise
