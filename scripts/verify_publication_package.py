from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_TEXT_FILES = [
    Path("README.md"),
    Path("PATENTS.md"),
    Path("NOTICE"),
    Path("CITATION.cff"),
    Path(".zenodo.json"),
    Path("docs/publication/quickstart-results-summary-v1.md"),
    Path("docs/publication/replication-ledger-v1.md"),
    Path("docs/publication/external-release-plan-v1.md"),
    Path("docs/publication/external-review-response-v1.md"),
    Path("docs/publication/manuscript-to-provisional-support-audit-v1.md"),
    Path("docs/publication/open-source-release-checklist-v1.md"),
    Path("docs/roadmap.md"),
    Path("docs/index.md"),
    Path("docs/api/scoring.md"),
    Path("docs/reproducible-environment.md"),
    Path("docs/research/q-rope-standard-benchmark-protocol-v1.md"),
    Path("docs/research/q-rope-hardware-specific-claim-test-v1.md"),
    Path("docs/research/q-rope-stage219-rope-substitution-gate-v1.md"),
    Path("docs/publication/figures/README.md"),
    Path("requirements-review.txt"),
]

REQUIRED_FILES = [
    *PUBLIC_TEXT_FILES,
    Path("scripts/generate_publication_figures.py"),
    Path("scripts/run_stage216_full_replacement_merged_result_counts.py"),
    Path("scripts/run_stage217_full_replacement_calibration_validation.py"),
    Path("scripts/run_stage218_full_replacement_hardware_metric_interpreter.py"),
    Path("scripts/run_stage219_rope_substitution_gate.py"),
    Path("src/qrope/scoring.py"),
    Path("src/qrope/stage219_rope_substitution_gate.py"),
    Path("tests/test_scoring_api.py"),
    Path("tests/test_stage216_218_full_replacement_interpretation.py"),
    Path("tests/test_stage219_rope_substitution_gate.py"),
    Path("docs/publication/figures/qrope-full-replacement-metrics-v1.png"),
    Path("docs/publication/figures/qrope-replication-status-v1.png"),
    Path("logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/manifest.json"),
    Path("logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/manifest.json"),
    Path("logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/manifest.json"),
    Path("logs/automated_stage_gates/stage219_rope_substitution_gate/manifest.json"),
    Path("logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/results.json"),
    Path("logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/results.json"),
    Path("logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/results.json"),
    Path("logs/automated_stage_gates/stage219_rope_substitution_gate/results.json"),
]

FORBIDDEN_PUBLIC_PATTERNS = [
    "crn:v1",
    "862cce8c",
    "6f260c59",
    "485386182336",
    "c08a112cd874462398a7f69d5757f7e0",
    "76347440",
    "76619690",
    "4085",
]

REQUIRED_PUBLIC_STRINGS = [
    "FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE",
    "qrope-full-replacement-metrics-v1.png",
    "production transformer superiority",
    "RoPE replacement",
    "quantum advantage",
    "broad cross-backend robustness",
    "Why Quantum Hardware?",
    "does not need a quantum computer",
    "Stage 5 is a motivation constraint",
    "from qrope import phase_margins, phase_residual, phasewrap_features, phasewrap_score",
    "qrope.scoring",
    "Reproducible Review Environment",
    "SQR = m8 * m12",
    "Standard Benchmark Protocol",
    "Hardware-Specific Claim Test",
    "PhaseWrap-RoPE Documentation",
    "Publication Figures",
    "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION",
    "bounded RoPE-substitution",
]


def _read(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(_read(path))


def _check_required_files(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not (ROOT / path).exists():
            errors.append(f"missing required file: {path.as_posix()}")


def _check_stage_manifests(errors: list[str]) -> None:
    stage216 = _load_json(Path("logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/manifest.json"))
    stage217 = _load_json(Path("logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/manifest.json"))
    stage218 = _load_json(Path("logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/manifest.json"))

    expected = {
        "stage216": (stage216.get("decision"), "FULL_REPLACEMENT_ALL_RESULT_COUNTS_MERGED_READY_FOR_CALIBRATION"),
        "stage217": (stage217.get("decision"), "FULL_REPLACEMENT_CALIBRATION_VALIDATED_READY_FOR_METRICS"),
        "stage218": (stage218.get("decision"), "FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"),
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            errors.append(f"{label} decision mismatch: {actual!r} != {wanted!r}")
    if stage216.get("merged_template_count") != 21 or stage216.get("expected_template_count") != 21:
        errors.append("stage216 merged template count is not 21/21")
    if stage217.get("inferred_bitstring_order") != "q1q0":
        errors.append("stage217 inferred bitstring order is not q1q0")
    if stage218.get("packet_template_count") != 20:
        errors.append("stage218 packet template count is not 20")
    if stage218.get("comparison_group_count") != 4:
        errors.append("stage218 comparison group count is not 4")
    if stage218.get("full_replacement_positive_seed_pair_count") != 2:
        errors.append("stage218 positive seed pair count is not 2")
    for label, manifest in (("stage216", stage216), ("stage217", stage217), ("stage218", stage218)):
        if manifest.get("blockers"):
            errors.append(f"{label} has blockers: {manifest.get('blockers')}")
        if manifest.get("secret_values_recorded") is not False:
            errors.append(f"{label} secret_values_recorded is not false")
    stage219 = _load_json(Path("logs/automated_stage_gates/stage219_rope_substitution_gate/manifest.json"))
    if stage219.get("decision") != "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION":
        errors.append("stage219 bounded substitution decision mismatch")
    if stage219.get("blockers"):
        errors.append(f"stage219 has blockers: {stage219.get('blockers')}")
    if stage219.get("primary_stage") != "stage30_matched_retrieval_bridge":
        errors.append("stage219 primary stage is not stage30")
    if stage219.get("secondary_stage") != "stage32_full_context_feature_bridge":
        errors.append("stage219 secondary stage is not stage32")


def _check_public_text(errors: list[str]) -> None:
    combined = "\n".join(_read(path) for path in PUBLIC_TEXT_FILES if (ROOT / path).exists())
    lower = combined.lower()
    for pattern in FORBIDDEN_PUBLIC_PATTERNS:
        if pattern.lower() in lower:
            errors.append(f"forbidden public pattern found: {pattern}")
    for required in REQUIRED_PUBLIC_STRINGS:
        if required.lower() not in lower:
            errors.append(f"required public string missing: {required}")


def _check_markdown_links(errors: list[str]) -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)#][^)]+)\)")
    for path in PUBLIC_TEXT_FILES:
        if not path.suffix == ".md" and path.name != "README.md":
            continue
        if not (ROOT / path).exists():
            continue
        text = _read(path)
        for match in link_re.finditer(text):
            target = match.group(1).split("#", 1)[0].strip()
            if not target or re.match(r"^(https?:|mailto:)", target):
                continue
            resolved = (ROOT / path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"link escapes repo in {path.as_posix()}: {target}")
                continue
            if not resolved.exists():
                errors.append(f"missing local link in {path.as_posix()}: {target}")


def verify_publication_package() -> list[str]:
    errors: list[str] = []
    _check_required_files(errors)
    if errors:
        return errors
    _check_stage_manifests(errors)
    _check_public_text(errors)
    _check_markdown_links(errors)
    return errors


def main() -> int:
    errors = verify_publication_package()
    if errors:
        print("PUBLICATION_PACKAGE_VERIFY_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PUBLICATION_PACKAGE_VERIFY_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
