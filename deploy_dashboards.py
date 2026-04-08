#!/usr/bin/env python3
"""Wrap and deploy all 3 network security dashboards to the current dtctl context.
Usage: python3 deploy_dashboards.py
"""
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))

DASHBOARDS = [
    {
        "source": os.path.join(BASE, "network-security/palo-alto/dashboards/palo_alto_firewall_logs_dashboard.json"),
        "name": "Palo Alto Firewall Traffic Analysis",
        "id": "ea77fbd7-b7b4-4ae0-afd8-412376926153",
    },
    {
        "source": os.path.join(BASE, "network-security/cisco/dashboards/cisco_asa_firewall_logs_dashboard.json"),
        "name": "Cisco ASA Firewall Dashboard",
        "id": "b85d6021-13c0-4acf-8d33-92179edd1543",
    },
    {
        "source": os.path.join(BASE, "network-security/fortinet/dashboards/fortinet_fortigate_logs_dashboard.json"),
        "name": "Fortinet FortiGate Logs Dashboard",
        "id": "ef373dd0-c745-4ef0-8168-480dfef37c99",
    },
]


def deploy():
    for d in DASHBOARDS:
        with open(d["source"]) as f:
            content = json.load(f)

        wrapped = {
            "id": d["id"],
            "name": d["name"],
            "type": "dashboard",
            "content": content,
        }

        # Write wrapped file next to source
        wrapped_path = d["source"].replace(".json", "_wrapped.json")
        with open(wrapped_path, "w", newline="\n") as f:
            json.dump(wrapped, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print(f"Wrapped: {os.path.basename(wrapped_path)}")

        # Deploy via dtctl
        result = subprocess.run(
            ["dtctl", "apply", "-f", wrapped_path, "--plain"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"  Applied: {result.stdout.strip()}")
        else:
            print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
            print(f"  stdout: {result.stdout.strip()}", file=sys.stderr)


if __name__ == "__main__":
    deploy()
