from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


@dataclass(frozen=True)
class NxosSettings:
    host: str
    username: str
    password: str
    port: int = 22


def load_settings() -> NxosSettings:
    return NxosSettings(
        host=os.getenv("NXOS_HOST", ""),
        username=os.getenv("NXOS_USERNAME", ""),
        password=os.getenv("NXOS_PASSWORD", ""),
        port=int(os.getenv("NXOS_PORT", "22")),
    )
