import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
# Ensure local package import works under different pytest import modes.
sys.path.insert(0, str(REPO_ROOT))


def test_effective_argv_default_no_injection():
    from partitionfinder.api import service as svc

    req = svc.JobRequest(folder=str(REPO_ROOT), datatype="DNA", args=["-n", "-f"], copy_input=True)
    assert svc._effective_argv(req) == ["-n", "-f"]


def test_effective_argv_injects_cpus_when_opted_in():
    from partitionfinder.api import service as svc

    req = svc.JobRequest(
        folder=str(REPO_ROOT),
        datatype="DNA",
        cpus=4,
        args=["-n", "-f"],
        copy_input=True,
    )
    assert svc._effective_argv(req)[:2] == ["-p", "4"]
    assert svc._effective_argv(req)[2:] == ["-n", "-f"]


@pytest.mark.parametrize("flag", ["-p", "--processors"])
def test_effective_argv_conflict_with_explicit_p(flag: str):
    from partitionfinder.api import service as svc

    req = svc.JobRequest(
        folder=str(REPO_ROOT),
        datatype="DNA",
        cpus=2,
        args=[flag, "1", "-n"],
        copy_input=True,
    )
    with pytest.raises(ValueError, match="conflicts"):
        svc._effective_argv(req)
