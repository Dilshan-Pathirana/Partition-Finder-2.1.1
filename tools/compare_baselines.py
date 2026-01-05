import argparse
import json
import re
from pathlib import Path


def normalize_model(model_text: str) -> str:
    model_text = model_text.strip()
    if model_text.startswith("b'") and model_text.endswith("'"):
        return model_text[2:-1]
    if model_text.startswith('b"') and model_text.endswith('"'):
        return model_text[2:-1]
    return model_text


def parse_best_scheme(best_scheme_path: Path) -> dict:
    txt = best_scheme_path.read_text(encoding="utf-8", errors="replace")

    def grab(pattern: str) -> str:
        m = re.search(pattern, txt, flags=re.MULTILINE)
        if not m:
            raise ValueError(f"Failed to parse {pattern!r} from {best_scheme_path}")
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
        raise ValueError(f"No Scheme AIC/AICc/BIC line found in {best_scheme_path}")

    num_subsets = int(grab(r"^Number of subsets\s*:\s*(\d+)"))

    subset_models: list[str] = []
    for line in txt.splitlines():
        m = re.match(r"^\s*\d+\s*\|\s*(.*?)\s*\|", line)
        if m:
            subset_models.append(normalize_model(m.group(1)))

    return {
        "scheme_name": scheme_name,
        "lnl": lnl,
        "criterion": criterion,
        "criterion_value": criterion_value,
        "num_subsets": num_subsets,
        "subset_best_models": subset_models,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare PartitionFinder best_scheme.txt between two runs")
    ap.add_argument("--py2", required=True, type=Path, help="Path to Python2 PF2 best_scheme.txt")
    ap.add_argument("--py3", required=True, type=Path, help="Path to Python3 PF2.1.1-py3 best_scheme.txt")
    ap.add_argument("--abs-tol", type=float, default=1e-3, help="Absolute tolerance for score comparison")
    ap.add_argument("--lnl-abs-tol", type=float, default=1e-6, help="Absolute tolerance for lnL comparison")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = ap.parse_args()

    left = parse_best_scheme(args.py2)
    right = parse_best_scheme(args.py3)

    diffs: dict[str, object] = {}

    for key in ["scheme_name", "criterion", "num_subsets", "subset_best_models"]:
        if left.get(key) != right.get(key):
            diffs[key] = {"py2": left.get(key), "py3": right.get(key)}

    def within(a: float, b: float, tol: float) -> bool:
        return abs(a - b) <= tol

    if not within(left["lnl"], right["lnl"], args.lnl_abs_tol):
        diffs["lnl"] = {"py2": left["lnl"], "py3": right["lnl"], "abs_diff": abs(left["lnl"] - right["lnl"])}

    if left["criterion"] == right["criterion"]:
        if not within(left["criterion_value"], right["criterion_value"], args.abs_tol):
            diffs["criterion_value"] = {
                "criterion": left["criterion"],
                "py2": left["criterion_value"],
                "py3": right["criterion_value"],
                "abs_diff": abs(left["criterion_value"] - right["criterion_value"]),
            }

    ok = len(diffs) == 0

    if args.json:
        print(json.dumps({"ok": ok, "diffs": diffs, "py2": left, "py3": right}, indent=2, sort_keys=True))
    else:
        if ok:
            print("OK: No differences outside tolerance")
        else:
            print("DIFFS:")
            for k, v in diffs.items():
                print(f"- {k}: {v}")

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
