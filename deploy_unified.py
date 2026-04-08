#!/usr/bin/env python3
"""Deploy unified network security dashboard and notebook to oqr staging."""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

ASSETS = [
    {
        "source": os.path.join(BASE, "network-security/unified/dashboards/network_security_overview_dashboard.json"),
        "name": "Network Security Overview",
        "type": "dashboard",
        "id": "1b48f4c3-f3b5-4ded-bd73-0661ce96e711",
    },
    {
        "source": os.path.join(BASE, "network-security/unified/notebooks/network_security_overview_notebook.json"),
        "name": "Network Security Overview — Cross-Vendor Analysis",
        "type": "notebook",
        "id": "9afdd1e3-d230-41af-98c6-08773e7fe369",
    },
]


def deploy():
    for asset in ASSETS:
        with open(asset["source"]) as f:
            content = json.load(f)

        wrapped = {
            "name": asset["name"],
            "type": asset["type"],
            "content": content,
        }
        if "id" in asset:
            wrapped["id"] = asset["id"]

        wrapped_path = asset["source"].replace(".json", "_wrapped.json")
        with open(wrapped_path, "w", newline="\n") as f:
            json.dump(wrapped, f, indent=2, ensure_ascii=False)
            f.write("\n")

        result = subprocess.run(
            ["dtctl", "apply", "-f", wrapped_path, "--plain"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"[{asset['type']}] {asset['name']}: {result.stdout.strip()}")
        else:
            print(f"[{asset['type']}] {asset['name']}: ERROR", file=sys.stderr)
            print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
            print(f"  stdout: {result.stdout.strip()}", file=sys.stderr)


if __name__ == "__main__":
    deploy()
