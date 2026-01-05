import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = REPO_ROOT / "tests" / "expected" / "example_baseline.json"


def _normalize_model(model_text: str) -> str:
    model_text = model_text.strip()
    # Reporter currently writes models as bytes repr like b'GTR+G'
    if model_text.startswith("b'") and model_text.endswith("'"):
        return model_text[2:-1]
    if model_text.startswith('b"') and model_text.endswith('"'):
        return model_text[2:-1]
    return model_text


def _parse_best_scheme(best_scheme_path: Path) -> dict:
    txt = best_scheme_path.read_text(encoding="utf-8", errors="replace")

    def grab(pattern: str) -> str:
        m = re.search(pattern, txt, flags=re.MULTILINE)
        if not m:
            raise AssertionError(f"Failed to parse {pattern!r} from {best_scheme_path}")
        return m.group(1).strip()

    scheme_name = grab(r"^Scheme Name\s*:\s*(\S+)")
    lnl = float(grab(r"^Scheme lnL\s*:\s*([-0-9.eE]+)"))

    criterion_value = None
    criterion = None
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
        raise AssertionError(f"No Scheme AIC/AICc/BIC line found in {best_scheme_path}")

    num_subsets = int(grab(r"^Number of subsets\s*:\s*(\d+)"))

    subset_models: list[str] = []
    for line in txt.splitlines():
        # Lines look like:
        # 1      | b'GTR+G'   | 490        | ...
        m = re.match(r"^\s*\d+\s*\|\s*(.*?)\s*\|", line)
        if m:
            subset_models.append(_normalize_model(m.group(1)))

    if not subset_models:
        raise AssertionError(f"No subset model lines parsed from {best_scheme_path}")

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

    # Normalize config naming. PartitionFinder requires partition_finder.cfg.
    cfg = dst / "partition_finder.cfg"
    if not cfg.exists():
        # The legacy example used a different cfg filename.
        candidates = list(dst.glob("*.cfg"))
        if len(candidates) == 1:
            shutil.copy2(candidates[0], cfg)
        elif len(candidates) > 1:
            raise AssertionError(f"Multiple .cfg files in {dst}, cannot infer which to use")
        else:
            raise AssertionError(f"No .cfg found in {dst}")

    return dst


@pytest.mark.parametrize("dataset_key", ["aminoacid", "morphology", "nucleotide"])
def test_regression_example_datasets(dataset_key: str, tmp_path: Path):
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    spec = baseline[dataset_key]

    input_dir = REPO_ROOT / spec["input_dir"]
    work_dir = _copy_example_to_tmp(input_dir, tmp_path)

    script_path = REPO_ROOT / spec["script"]
    args = [sys.executable, str(script_path), *spec["args"], str(work_dir)]

    # Stabilize CPU parallelism (PF also uses -p 1).
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("NUMEXPR_NUM_THREADS", "1")

    proc = subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60 * 10,
    )

    assert proc.returncode == 0, f"PartitionFinder failed for {dataset_key}. Output:\n{proc.stdout}"

    best_scheme_path = work_dir / "analysis" / "best_scheme.txt"
    assert best_scheme_path.exists(), f"Missing {best_scheme_path}"

    got = _parse_best_scheme(best_scheme_path)
    exp = spec["expected"]

    assert got["scheme_name"] == exp["scheme_name"]
    assert got["criterion"] == exp["criterion"]
    assert got["num_subsets"] == exp["num_subsets"]
    assert got["subset_best_models"] == exp["subset_best_models"]

    # Floating-point tolerance: allow tiny numeric drift only.
    assert got["lnl"] == pytest.approx(exp["lnl"], abs=1e-6)
    assert got["criterion_value"] == pytest.approx(exp["criterion_value"], abs=1e-3)
