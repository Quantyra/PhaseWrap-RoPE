from __future__ import annotations

from scripts import verify_publication_package as verifier


def test_publication_package_verifier_passes_current_package() -> None:
    assert verifier.verify_publication_package() == []


def test_publication_package_verifier_catches_stage218_decision_regression(monkeypatch) -> None:
    original_load_json = verifier._load_json

    def fake_load_json(path):
        payload = original_load_json(path)
        if path.as_posix().endswith("stage218_full_replacement_hardware_metric_interpreter_250usd/manifest.json"):
            payload = dict(payload)
            payload["decision"] = "REGRESSED"
        return payload

    monkeypatch.setattr(verifier, "_load_json", fake_load_json)

    errors = verifier.verify_publication_package()

    assert any("stage218 decision mismatch" in error for error in errors)


def test_publication_package_verifier_catches_forbidden_public_pattern(monkeypatch) -> None:
    original_read = verifier._read

    def fake_read(path):
        text = original_read(path)
        if path.as_posix() == "README.md":
            return f"{text}\n76347440\n"
        return text

    monkeypatch.setattr(verifier, "_read", fake_read)

    errors = verifier.verify_publication_package()

    assert any("forbidden public pattern" in error for error in errors)
