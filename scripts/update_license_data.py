"""Vendor an SPDX license-list-data snapshot into a single bundle (JSON).

First-class air-gap requirement: bundle the full text of every license/exception so it works
completely without network access. Run on each release to refresh
`src/onot/license/data/licenses.json`.

Usage: python scripts/update_license_data.py
"""

from __future__ import annotations

import concurrent.futures as cf
import json
from pathlib import Path

import httpx

BASE = "https://spdx.org/licenses"
OUT = Path(__file__).resolve().parents[1] / "src" / "onot" / "license" / "data" / "licenses.json"


def _fetch_json(client: httpx.Client, url: str) -> dict:
    resp = client.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _detail_url(entry: dict, id_key: str) -> str:
    return entry.get("detailsUrl") or f"{BASE}/{entry[id_key]}.json"


def main() -> None:
    client = httpx.Client(follow_redirects=True, timeout=30, trust_env=True)
    idx = _fetch_json(client, f"{BASE}/licenses.json")
    exc_idx = _fetch_json(client, f"{BASE}/exceptions.json")
    version = idx["licenseListVersion"]

    def lic_task(entry: dict) -> tuple[str, dict]:
        detail = _fetch_json(client, _detail_url(entry, "licenseId"))
        return entry["licenseId"], {
            "name": entry.get("name", ""),
            "deprecated": bool(entry.get("isDeprecatedLicenseId", False)),
            "reference": entry.get("reference"),
            "text": detail.get("licenseText", ""),
        }

    def exc_task(entry: dict) -> tuple[str, dict]:
        detail = _fetch_json(client, _detail_url(entry, "licenseExceptionId"))
        return entry["licenseExceptionId"], {
            "name": entry.get("name", ""),
            "deprecated": bool(entry.get("isDeprecatedLicenseId", False)),
            "reference": entry.get("reference"),
            "text": detail.get("licenseExceptionText", ""),
        }

    licenses: dict[str, dict] = {}
    exceptions: dict[str, dict] = {}
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for lid, val in pool.map(lic_task, idx["licenses"]):
            licenses[lid] = val
        for eid, val in pool.map(exc_task, exc_idx["exceptions"]):
            exceptions[eid] = val

    data = {
        "licenseListVersion": version,
        "licenses": licenses,
        "exceptions": exceptions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    print(
        f"wrote {OUT}: {len(licenses)} licenses, {len(exceptions)} exceptions, "
        f"v{version}, {OUT.stat().st_size} bytes"
    )


if __name__ == "__main__":
    main()
