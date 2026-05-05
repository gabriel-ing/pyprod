import os
import sys
import time
from pathlib import Path

import iris
import pytest


PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from intersystems_pyprod._prod_controls import (  # noqa: E402
    RUNNING,
    STATUS_MESSAGES,
    STOPPED,
    TROUBLED,
    get_prod_status,
    restart_prod,
    start_prod,
    stop_prod,
)
from intersystems_pyprod._parser import main as parser_main  # noqa: E402


PRODUCTION_NAME = "AllPyComponents.Production"
SETUP_TIMEOUT = 12


def _detect_repo_root() -> Path:
    ws = os.environ.get("GITHUB_WORKSPACE")
    if ws:
        return Path(ws).resolve()

    here = Path(__file__).resolve()
    for path in [here] + list(here.parents):
        if (path / "pyproject.toml").exists() or (path / ".git").exists():
            return path
    return Path.cwd()


def _read_director_status():
    production_name = iris.ref("")
    production_status = iris.ref("")
    response = iris.Ens.Director.GetProductionStatus(production_name, production_status)
    assert response == 1, f"GetProductionStatus failed with status {response}"
    return {
        "name": production_name.value,
        "status": production_status.value,
        "status_message": STATUS_MESSAGES.get(production_status.value, "Unknown"),
    }


def _wait_for_status(expected_status, timeout=SETUP_TIMEOUT, production_name=None):
    deadline = time.time() + timeout
    last_status = None

    while time.time() < deadline:
        last_status = _read_director_status()
        if last_status["status"] != expected_status:
            time.sleep(0.5)
            continue
        if production_name is not None and last_status["name"] != production_name:
            time.sleep(0.5)
            continue
        return last_status

    raise AssertionError(
        f"Timed out waiting for production status {expected_status} "
        f"for {production_name or 'current production'}; last status was {last_status}"
    )


def _stop_active_production(timeout=SETUP_TIMEOUT):
    current_status = _read_director_status()
    if current_status["status"] == STOPPED:
        return current_status

    if current_status["status"] == TROUBLED and current_status["name"] == PRODUCTION_NAME:
        return _recover_troubled_production(timeout)

    response = iris.Ens.Director.StopProduction(timeout, False)
    assert response == 1, f"StopProduction failed during test setup with status {response}"

    deadline = time.time() + timeout
    while time.time() < deadline:
        current_status = _read_director_status()
        if current_status["status"] == STOPPED:
            return current_status
        time.sleep(0.5)

    response = iris.Ens.Director.StopProduction(timeout, True)
    assert response == 1, f"Force StopProduction failed during test setup with status {response}"

    try:
        return _wait_for_status(STOPPED, timeout=timeout)
    except AssertionError:
        current_status = _read_director_status()
        if current_status["status"] == TROUBLED and current_status["name"] == PRODUCTION_NAME:
            return _recover_troubled_production(timeout)
        raise


def _recover_troubled_production(timeout=SETUP_TIMEOUT):
    response = iris.Ens.Director.StartProduction(PRODUCTION_NAME)
    assert response == 1, f"StartProduction recovery failed during test setup with status {response}"
    _wait_for_status(RUNNING, timeout=timeout, production_name=PRODUCTION_NAME)

    response = iris.Ens.Director.StopProduction(timeout, True)
    assert response == 1, f"Force StopProduction recovery failed during test setup with status {response}"
    return _wait_for_status(STOPPED, timeout=timeout)


def _start_active_production(timeout=SETUP_TIMEOUT):
    current_status = _read_director_status()
    if current_status["status"] == RUNNING and current_status["name"] == PRODUCTION_NAME:
        return current_status

    response = iris.Ens.Director.StartProduction(PRODUCTION_NAME)
    assert response == 1, f"StartProduction failed during test setup with status {response}"
    return _wait_for_status(RUNNING, timeout=timeout, production_name=PRODUCTION_NAME)


@pytest.fixture(scope="module", autouse=True)
def load_production_definition():
    repo_root = _detect_repo_root()
    cls_host = repo_root / "tests" / "helpers" / "AllPyComponents" / "Production.cls"
    py_host = repo_root / "tests" / "helpers" / "AllPyComponents" / "AllPyComponents.py"
    if not cls_host.exists():
        raise FileNotFoundError(f"IRIS class file not found: {cls_host}")
    if not py_host.exists():
        raise FileNotFoundError(f"Python helper file not found: {py_host}")

    parser_main([str(py_host)])
    status = iris._SYSTEM.OBJ.Load(str(cls_host), "ck")
    print("production loading status = ", status)
    _stop_active_production()

    yield

    _stop_active_production()


@pytest.fixture(autouse=True)
def clean_production_state():
    _stop_active_production()
    yield
    _stop_active_production()


def test_get_prod_status_reports_stopped_when_no_production_is_running():
    result = get_prod_status()

    assert result["status"] == STOPPED
    assert result["status_message"] == "Stopped"


def test_start_production_starts_the_named_production():
    result = start_prod(PRODUCTION_NAME)

    assert result == {
        "ok": True,
        "message": f"Production {PRODUCTION_NAME} started successfully.",
    }

    status = _wait_for_status(RUNNING, production_name=PRODUCTION_NAME)
    assert status["name"] == PRODUCTION_NAME
    assert status["status_message"] == "Running"


def test_start_production_rejects_an_already_running_production():
    _start_active_production()

    duplicate_result = start_prod(PRODUCTION_NAME)

    assert duplicate_result == {
        "ok": False,
        "message": (
            f"Production {PRODUCTION_NAME} is already active with status Running. "
            "Use -r flag to restart the production."
        ),
    }


def test_restart_production_restarts_the_running_production():
    _start_active_production()

    restart_result = restart_prod(timeout=10, force=False)

    assert restart_result == {
        "ok": True,
        "message": "Production restarted successfully.",
    }

    status = _wait_for_status(RUNNING, production_name=PRODUCTION_NAME)
    assert status["name"] == PRODUCTION_NAME


def test_stop_production_stops_the_running_production():
    _start_active_production()

    stop_result = stop_prod(timeout=10, force=False)

    assert stop_result == {
        "ok": True,
        "message": f"Production {PRODUCTION_NAME} stopped successfully.",
    }

    status = _wait_for_status(STOPPED)
    assert status["status_message"] == "Stopped"


def test_forced_stop_production_stops_the_running_production():
    _start_active_production()

    stop_result = stop_prod(timeout=10, force=True)

    assert stop_result == {
        "ok": True,
        "message": f"Production {PRODUCTION_NAME} stopped successfully.",
    }

    status = _wait_for_status(STOPPED)
    assert status["status_message"] == "Stopped"


def test_stop_production_reports_no_running_production():
    result = stop_prod(timeout=10, force=False)

    assert result == {
        "ok": False,
        "message": (
            "There is no production running in the current namespace. Use "
            "--start flag to start a production."
        ),
    }


def test_restart_production_reports_no_running_production():
    result = restart_prod(timeout=10, force=False)

    assert result == {
        "ok": False,
        "message": (
            "There is no production running to restart in the current namespace. "
            "Use --start flag to start a named production."
        ),
    }