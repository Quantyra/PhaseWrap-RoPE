from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    token = os.environ.get("QUANDELA_CLOUD_TOKEN", "").strip()
    if not token:
        print("QUANDELA_CLOUD_TOKEN is missing.")
        return 1

    try:
        from perceval.providers import QuandelaSession
    except Exception as exc:
        print(f"Failed to import QuandelaSession: {exc}")
        return 1

    platform_name = (
        os.environ.get("QROPE_QUANDELA_BACKEND", "").strip()
        or os.environ.get("QUANDELA_PLATFORM", "").strip()
        or "sim:slos"
    )

    try:
        session = QuandelaSession(platform_name=platform_name, token=token)
        processor = session.build_remote_processor()
        specs = processor.specs
    except Exception as exc:
        print(f"Failed to connect to Quandela Cloud: {exc}")
        return 2

    print("Quandela Cloud connection initialized.")
    print(f"Platform: {platform_name}")
    try:
        print(f"Processor name: {processor.name}")
    except Exception:
        pass
    try:
        print(f"Processor status: {processor.status}")
    except Exception:
        pass
    try:
        commands = getattr(processor, "available_commands", [])
        if commands:
            print(f"Available commands: {', '.join(commands)}")
    except Exception:
        pass
    try:
        if isinstance(specs, dict):
            print("Specs keys:")
            for key in sorted(specs.keys())[:10]:
                print(f"spec: {key}")
        else:
            print(f"Specs type: {type(specs).__name__}")
    except Exception as exc:
        print(f"Connected, but failed to summarize specs: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
