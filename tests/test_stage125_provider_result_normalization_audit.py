from __future__ import annotations

import json

import pytest

from qrope.provider_adapters.amazon_braket import normalize_result_counts as normalize_braket
from qrope.provider_adapters.common import ProviderAdapterBlocked, canonicalize_counts
from qrope.provider_adapters.ibm_runtime import normalize_result_counts as normalize_ibm
from qrope.stage125_provider_result_normalization_audit import run_stage125_audit, write_stage125_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_canonicalize_counts_rejects_invalid_keys() -> None:
    with pytest.raises(ProviderAdapterBlocked):
        canonicalize_counts({"not_bits": 10})


def test_provider_normalizers_accept_common_result_shapes() -> None:
    assert normalize_ibm({"counts": {"0b00": 3, "11": 2}}) == {"00": 3, "11": 2}
    assert normalize_ibm({"quasi_dists": [{"00": 0.25, "11": 0.75}], "shots": 1000}) == {"00": 250, "11": 750}
    assert normalize_braket({"measurementCounts": {"01": 4, "10": 6}}) == {"01": 4, "10": 6}
    assert normalize_braket({"counts": {"0b01": 4, "10": 6}}) == {"01": 4, "10": 6}


def test_stage125_reports_normalization_ready(tmp_path) -> None:
    _write_json(tmp_path / "stage124.json", {"decision": "ADAPTER_READINESS_ALIGNED_EXECUTION_BLOCKED"})

    result = run_stage125_audit(stage124_results_path=tmp_path / "stage124.json")

    assert result["decision"] == "PROVIDER_RESULT_NORMALIZATION_READY_EXECUTION_BLOCKED"
    assert result["ready_provider_count"] == 2
    assert all(record["ready_sample_count"] == 2 for record in result["provider_records"])


def test_stage125_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage124.json", {})
    result = run_stage125_audit(stage124_results_path=tmp_path / "stage124.json")

    paths = write_stage125_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_count"] == 2
    assert "ibm_runtime" in summary
