from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Any


class ProviderAdapterBlocked(RuntimeError):
    """Raised when a provider adapter is intentionally blocked before live submission."""


@dataclass(frozen=True)
class ProviderAdapterStatus:
    provider: str
    submitter_import_path: str
    sdk_modules: dict[str, bool]
    required_env: tuple[str, ...]
    required_env_present: dict[str, bool]
    live_submission_implemented: bool
    no_hardware_submission: bool

    @property
    def ready(self) -> bool:
        return (
            all(self.sdk_modules.values())
            and all(self.required_env_present.values())
            and self.live_submission_implemented
            and not self.no_hardware_submission
        )

    @property
    def blockers(self) -> list[str]:
        blockers = []
        if not all(self.sdk_modules.values()):
            blockers.append("provider_sdk_missing")
        missing_env = [name for name, present in self.required_env_present.items() if not present]
        if missing_env:
            blockers.extend(f"env_missing:{name}" for name in missing_env)
        if not self.live_submission_implemented:
            blockers.append("live_submission_not_implemented")
        if self.no_hardware_submission:
            blockers.append("adapter_no_submit_guard_active")
        return blockers

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "submitter_import_path": self.submitter_import_path,
            "sdk_modules": self.sdk_modules,
            "required_env": list(self.required_env),
            "required_env_present": self.required_env_present,
            "live_submission_implemented": self.live_submission_implemented,
            "no_hardware_submission": self.no_hardware_submission,
            "ready": self.ready,
            "blockers": self.blockers,
        }


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def env_present(required_env: tuple[str, ...]) -> dict[str, bool]:
    presence = {}
    for name in required_env:
        alternatives = [part.strip() for part in name.split(" or ")]
        presence[name] = any(bool(os.environ.get(part)) for part in alternatives)
    return presence


def canonicalize_counts(raw_counts: Any) -> dict[str, int]:
    if not isinstance(raw_counts, dict) or not raw_counts:
        raise ProviderAdapterBlocked("raw provider counts missing or empty")
    normalized: dict[str, int] = {}
    for key, value in raw_counts.items():
        bitstring = str(key).replace(" ", "")
        if bitstring.startswith("0b"):
            bitstring = bitstring[2:]
        if not bitstring or any(char not in "01" for char in bitstring):
            raise ProviderAdapterBlocked(f"non-bitstring count key: {key!r}")
        try:
            count = int(value)
        except (TypeError, ValueError) as exc:
            raise ProviderAdapterBlocked(f"non-integer count value for {key!r}") from exc
        if count < 0:
            raise ProviderAdapterBlocked(f"negative count value for {key!r}")
        normalized[bitstring] = normalized.get(bitstring, 0) + count
    if sum(normalized.values()) <= 0:
        raise ProviderAdapterBlocked("canonical counts sum to zero")
    return dict(sorted(normalized.items()))
