from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


def get_iosxe_credentials_from_vault() -> dict[str, str]:
    """Retrieve IOS XE credentials from HashiCorp Vault.

    TODO:
    - Import hvac.
    - Create hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN")).
    - Read KV version 2 secret at os.getenv("VAULT_SECRET_PATH").
    - Extract the nested data dictionary without printing the Vault response.
    - Return {"username": username, "password": password}.

    Security requirement: never print the raw Vault response, username,
    password, or token. The dashboard calls this function repeatedly.
    """

    raise NotImplementedError("Complete Vault credential retrieval for the final lab")
