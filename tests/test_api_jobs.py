import json
import os
import re
import shutil
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = REPO_ROOT / "tests" / "expected" / "example_baseline.json"

# Some pytest import modes do not automatically add the repository root to
# `sys.path`. Ensure the local package is importable.
sys.path.insert(0, str(REPO_ROOT))


def _normalize_model(model_text: str) -> str:
    model_text = model_text.strip()
    if model_text.startswith("b'") and model_text.endswith("'"):
        return model_text[2:-1]
    if model_text.startswith('b"') and model_text.endswith('"'):
        return model_text[2:-1]
    return model_text


def _parse_best_scheme_text(txt: str) -> dict:
    def grab(pattern: str) -> str:
        m = re.search(pattern, txt, flags=re.MULTILINE)
        if not m:
            raise AssertionError(f"Failed to parse {pattern!r} from best_scheme text")
        return m.group(1).strip()

    scheme_name = grab(r"^Scheme Name\s*:\s*(\S+)")
    lnl = float(grab(r"^Scheme lnL\s*:\s*([-0-9.eE]+)"))

    if re.search(r"^Scheme AICc\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "aicc"
        criterion_value = float(grab(r"^Scheme AICc\s*:\s*([-0-9.eE]+)"))
    elif re.search(r"^Scheme AIC\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "aic"
        criterion_value = float(grab(r"^Scheme AIC\s*:\s*([-0-9.eE]+)"))
    elif re.search(r"^Scheme BIC\s*:\s*", txt, flags=re.MULTILINE):
        criterion = "bic"
        criterion_value = float(grab(r"^Scheme BIC\s*:\s*([-0-9.eE]+)"))
    else:
        raise AssertionError("No Scheme AIC/AICc/BIC line found")

    num_subsets = int(grab(r"^Number of subsets\s*:\s*(\d+)"))

    subset_models: list[str] = []
    for line in txt.splitlines():
        m = re.match(r"^\s*\d+\s*\|\s*(.*?)\s*\|", line)
        if m:
            subset_models.append(_normalize_model(m.group(1)))

    if not subset_models:
        raise AssertionError("No subset model lines parsed")

    return {
        "scheme_name": scheme_name,
        "lnl": lnl,
        "criterion": criterion,
        "criterion_value": criterion_value,
        "num_subsets": num_subsets,
        "subset_best_models": subset_models,
    }


def _copy_example_to_tmp(input_dir: Path, tmp_path: Path) -> Path:
    dst = tmp_path / input_dir.name
    shutil.copytree(input_dir, dst)

    cfg = dst / "partition_finder.cfg"
    if not cfg.exists():
        candidates = list(dst.glob("*.cfg"))
        if len(candidates) == 1:
            shutil.copy2(candidates[0], cfg)
        elif len(candidates) > 1:
            raise AssertionError(f"Multiple .cfg files in {dst}, cannot infer which to use")
        else:
            raise AssertionError(f"No .cfg found in {dst}")

    return dst


def test_api_submit_and_wait_matches_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    spec = baseline["aminoacid"]

    input_dir = REPO_ROOT / spec["input_dir"]
    work_dir = _copy_example_to_tmp(input_dir, tmp_path)

    # Stabilize CPU parallelism (PF also uses -p 1).
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    monkeypatch.setenv("NUMEXPR_NUM_THREADS", "1")

    from partitionfinder.api import service as svc

    # Ensure the test doesn't write job artifacts to the repo root.
    svc.store = svc.JobStore(tmp_path / "jobs")

    req = svc.JobRequest(
        folder=str(work_dir),
        datatype="protein",
        args=list(spec["args"]),
        copy_input=True,
    )

    result = svc.submit_and_wait(req, poll_interval_s=0.5)
    assert result.state == "succeeded"
    assert result.best_scheme_txt is not None

    got = _parse_best_scheme_text(result.best_scheme_txt)
    exp = spec["expected"]

    assert got["scheme_name"] == exp["scheme_name"]
    assert got["criterion"] == exp["criterion"]
    assert got["num_subsets"] == exp["num_subsets"]
    assert got["subset_best_models"] == exp["subset_best_models"]

    assert got["lnl"] == pytest.approx(exp["lnl"], abs=1e-6)
    assert got["criterion_value"] == pytest.approx(exp["criterion_value"], abs=1e-3)
