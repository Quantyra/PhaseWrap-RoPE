from __future__ import annotations

import importlib
import json
import pkgutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import qrope  # noqa: E402

OPTIONAL_DEPENDENCY_ROOTS = {
    "amazon",
    "braket",
    "matplotlib",
    "pennylane",
    "perceval",
    "qiskit",
    "qiskit_aer",
    "qiskit_ibm_runtime",
}
REQUIRED_ARTIFACTS = (
    "logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/manifest.json",
    "logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/manifest.json",
    "logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/manifest.json",
    "logs/automated_stage_gates/stage219_rope_substitution_gate/manifest.json",
)


def _module_names() -> list[str]:
    return sorted(module.name for module in pkgutil.iter_modules(qrope.__path__, prefix="qrope."))


def _import_modules() -> list[str]:
    skipped: list[str] = []
    failures: list[str] = []
    for module_name in _module_names():
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            missing_root = str(exc.name).split(".", 1)[0]
            if missing_root in OPTIONAL_DEPENDENCY_ROOTS:
                skipped.append(f"{module_name} (missing optional dependency {exc.name})")
                continue
            failures.append(f"{module_name}: {exc}")
        except Exception as exc:  # pragma: no cover - diagnostic output is the point.
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")
    if failures:
        raise RuntimeError("Module import smoke failures:\n" + "\n".join(failures))
    return skipped


def _check_artifacts() -> None:
    failures: list[str] = []
    for artifact in REQUIRED_ARTIFACTS:
        path = REPO_ROOT / artifact
        if not path.exists():
            failures.append(f"missing artifact: {artifact}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid JSON artifact {artifact}: {exc}")
    if failures:
        raise RuntimeError("Artifact integrity failures:\n" + "\n".join(failures))


def _run_script_help() -> None:
    scripts = [
        "scripts/run_stage11_phasewrap_theory.py",
        "scripts/run_stage218_full_replacement_hardware_metric_interpreter.py",
        "scripts/run_stage219_rope_substitution_gate.py",
    ]
    failures: list[str] = []
    for script in scripts:
        completed = subprocess.run(
            [sys.executable, script, "--help"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        output = f"{completed.stdout}\n{completed.stderr}".lower()
        if completed.returncode not in {0, 2} or ("usage" not in output and "publication" not in output):
            failures.append(f"{script}: exit={completed.returncode}")
    if failures:
        raise RuntimeError("Script help smoke failures:\n" + "\n".join(failures))


def main() -> int:
    skipped = _import_modules()
    _check_artifacts()
    _run_script_help()
    print("Public surface smoke passed.")
    if skipped:
        print("Optional-dependency module skips:")
        for item in skipped:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
