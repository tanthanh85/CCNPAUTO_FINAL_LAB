from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests
from urllib3.exceptions import InsecureRequestWarning

from src.settings import load_settings


# TODO: Use Cisco Yangsuite to locate the correct Cisco IOS XE RESTCONF paths.
# Place only the RESTCONF data path beginning with "/".
CPU_URI = ""
MEMORY_URI = ""
INTERFACE_GIG1_URI = ""


class RestconfMonitorError(RuntimeError):
    pass


def restconf_get(path: str) -> dict[str, Any]:
    if not path:
        raise RestconfMonitorError("RESTCONF URI has not been completed")
    if not path.startswith("/"):
        raise RestconfMonitorError("RESTCONF URI must begin with '/'")

    settings = load_settings()
    if not settings.verify_tls:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    response = requests.get(
        f"{settings.restconf_base_url}{path}",
        auth=(settings.username, settings.password),
        headers={"Accept": "application/yang-data+json"},
        timeout=10,
        verify=settings.verify_tls,
    )
    response.raise_for_status()
    return response.json() if response.text else {}


def numeric_value(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return float(value) if "." in value else int(value)
        except ValueError:
            return None
    return None


def find_numeric_leaf(value: Any, leaf_name: str) -> int | float | None:
    """Find a numeric JSON leaf without depending on its module prefix."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.split(":")[-1] == leaf_name:
                found = numeric_value(child)
                if found is not None:
                    return found
            found = find_numeric_leaf(child, leaf_name)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_numeric_leaf(item, leaf_name)
            if found is not None:
                return found
    return None


def get_monitoring_snapshot() -> dict[str, Any]:
    cpu_data = restconf_get(CPU_URI)
    memory_data = restconf_get(MEMORY_URI)
    interface_data = restconf_get(INTERFACE_GIG1_URI)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": {
            "uri": CPU_URI,
            "value": find_numeric_leaf(cpu_data, "five-seconds"),
            "unit": "percent",
        },
        "memory": {
            "uri": MEMORY_URI,
            "value": find_numeric_leaf(memory_data, "used-memory"),
            "unit": "bytes",
        },
        "gigabit_ethernet_1": {
            "uri": INTERFACE_GIG1_URI,
            "input_rate": find_numeric_leaf(interface_data, "rx-pps"),
            "output_rate": find_numeric_leaf(interface_data, "tx-pps"),
            "unit": "packets_per_second",
        },
    }
