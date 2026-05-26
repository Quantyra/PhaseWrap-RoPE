from __future__ import annotations

import os
from pathlib import Path

from qrope.env_utils import load_local_dotenv


def test_load_local_dotenv_uses_allowlist_and_common_syntax(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("IBM_QUANTUM_TOKEN", raising=False)
    monkeypatch.delenv("UNRELATED_SECRET", raising=False)
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "\n".join(
            [
                "export IBM_QUANTUM_TOKEN='ibm-token'",
                'UNRELATED_SECRET="should-not-load"',
            ]
        ),
        encoding="utf-8",
    )

    load_local_dotenv(dotenv)

    assert os.environ["IBM_QUANTUM_TOKEN"] == "ibm-token"
    assert "UNRELATED_SECRET" not in os.environ


def test_load_local_dotenv_preserves_existing_environment(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("IBM_QUANTUM_TOKEN", "existing")
    dotenv = tmp_path / ".env"
    dotenv.write_text("IBM_QUANTUM_TOKEN=new\n", encoding="utf-8")

    load_local_dotenv(dotenv)

    assert os.environ["IBM_QUANTUM_TOKEN"] == "existing"
