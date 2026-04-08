#!/usr/bin/env python3
"""Enhance all 3 network security dashboards with KPI tiles, defaultTimeframe,
and davis config. Operates on the source JSON files in the repo."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Per-vendor configuration ─────────────────────────────────────────────────
VENDORS = {
    "palo-alto": {
        "path": os.path.join(BASE, "network-security/palo-alto/dashboards/palo_alto_firewall_logs_dashboard.json"),
        "log_source": "palo-alto-firewall",
        "action_field": "paloalto.action",
        "block_filter": 'paloalto.action != "allow"',
        "src_field": "paloalto.src",
        "rule_field": "paloalto.rule",
        "rule_label": "Deny Rules Hit",
    },
    "cisco": {
        "path": os.path.join(BASE, "network-security/cisco/dashboards/cisco_asa_firewall_logs_dashboard.json"),
        "log_source": "cisco-asa",
        "action_field": "cisco.action",
        "block_filter": 'in(cisco.action, "deny", "auth-failed")',
        "src_field": "cisco.src_ip",
        "rule_field": "cisco.message_id",
        "rule_label": "Message IDs",
    },
    "fortinet": {
        "path": os.path.join(BASE, "network-security/fortinet/dashboards/fortinet_fortigate_logs_dashboard.json"),
        "log_source": "fortinet-fortigate",
        "action_field": "fortinet.action",
        "block_filter": 'fortinet.action != "accept"',
        "src_field": "fortinet.srcip",
        "rule_field": "fortinet.policyname",
        "rule_label": "Policies Hit",
    },
}

KPI_ROW_HEIGHT = 4
KPI_TILE_WIDTH = 6  # 4 tiles × 6 = 24 (full width)


def build_kpi_tiles(v):
    """Return 4 KPI tiles + their layouts for a given vendor config."""
    ls = v["log_source"]

    tiles = {
        "kpi_total": {
            "type": "data",
            "title": "Total Events",
            "query": f'fetch logs\n| filter log.source == "{ls}"\n| summarize total = count()',
            "visualization": "singleValue",
            "visualizationSettings": {
                "thresholds": [],
                "chartSettings": {},
                "singleValue": {
                    "showLabel": True,
                    "label": "Total Events",
                    "autoscale": True,
                },
                "table": {"enableLineWrap": True, "hiddenColumns": [], "lineWrapIds": []},
            },
            "davis": {"enabled": False, "davisVisualization": {"isAvailable": True}},
        },
        "kpi_block_rate": {
            "type": "data",
            "title": "Block Rate %",
            "query": (
                f'fetch logs\n| filter log.source == "{ls}"\n'
                f"| fieldsAdd is_blocked = {v['block_filter']}\n"
                "| summarize block_rate = round(toDouble(countIf(is_blocked)) / toDouble(count()) * 100, decimals: 1)"
            ),
            "visualization": "singleValue",
            "visualizationSettings": {
                "thresholds": [
                    {"field": "block_rate", "title": "Block Rate", "isEnabled": True,
                     "rules": [
                         {"value": 0,  "color": {"Default": "#4fd5a6"}},
                         {"value": 30, "color": {"Default": "#f5d30f"}},
                         {"value": 50, "color": {"Default": "#dc3545"}},
                     ]},
                ],
                "chartSettings": {},
                "singleValue": {
                    "showLabel": True,
                    "label": "Block Rate %",
                    "autoscale": True,
                },
                "table": {"enableLineWrap": True, "hiddenColumns": [], "lineWrapIds": []},
            },
            "davis": {"enabled": False, "davisVisualization": {"isAvailable": True}},
        },
        "kpi_unique_src": {
            "type": "data",
            "title": "Unique Sources",
            "query": (
                f'fetch logs\n| filter log.source == "{ls}"\n'
                f"| summarize unique_sources = countDistinct({v['src_field']})"
            ),
            "visualization": "singleValue",
            "visualizationSettings": {
                "thresholds": [],
                "chartSettings": {},
                "singleValue": {
                    "showLabel": True,
                    "label": "Unique Sources",
                    "autoscale": True,
                },
                "table": {"enableLineWrap": True, "hiddenColumns": [], "lineWrapIds": []},
            },
            "davis": {"enabled": False, "davisVisualization": {"isAvailable": True}},
        },
        "kpi_unique_rules": {
            "type": "data",
            "title": v["rule_label"],
            "query": (
                f'fetch logs\n| filter log.source == "{ls}"\n'
                f"| filter {v['block_filter']}\n"
                f"| summarize unique_rules = countDistinct({v['rule_field']})"
            ),
            "visualization": "singleValue",
            "visualizationSettings": {
                "thresholds": [],
                "chartSettings": {},
                "singleValue": {
                    "showLabel": True,
                    "label": v["rule_label"],
                    "autoscale": True,
                },
                "table": {"enableLineWrap": True, "hiddenColumns": [], "lineWrapIds": []},
            },
            "davis": {"enabled": False, "davisVisualization": {"isAvailable": True}},
        },
    }

    layouts = {
        "kpi_total":       {"x": 0,  "y": 0, "w": KPI_TILE_WIDTH, "h": KPI_ROW_HEIGHT},
        "kpi_block_rate":  {"x": 6,  "y": 0, "w": KPI_TILE_WIDTH, "h": KPI_ROW_HEIGHT},
        "kpi_unique_src":  {"x": 12, "y": 0, "w": KPI_TILE_WIDTH, "h": KPI_ROW_HEIGHT},
        "kpi_unique_rules":{"x": 18, "y": 0, "w": KPI_TILE_WIDTH, "h": KPI_ROW_HEIGHT},
    }

    return tiles, layouts


def enhance_dashboard(vendor_key, v):
    path = v["path"]
    with open(path, "r") as f:
        dash = json.load(f)

    # ── 1. Build new KPI tiles ───────────────────────────────────────────
    kpi_tiles, kpi_layouts = build_kpi_tiles(v)

    # ── 2. Renumber existing tiles to make room for KPIs ─────────────────
    old_keys = sorted(dash["tiles"].keys(), key=lambda k: int(k))
    new_tiles = {}
    new_layouts = {}

    # KPI tiles get slots 0-3
    kpi_names = ["kpi_total", "kpi_block_rate", "kpi_unique_src", "kpi_unique_rules"]
    for i, name in enumerate(kpi_names):
        new_tiles[str(i)] = kpi_tiles[name]
        new_layouts[str(i)] = kpi_layouts[name]

    offset = len(kpi_names)  # 4

    for old_key in old_keys:
        old_idx = int(old_key)
        new_idx = old_idx + offset
        new_key = str(new_idx)

        tile = dash["tiles"][old_key]

        # Keep markdown header at y=0 but push it down by KPI_ROW_HEIGHT
        old_layout = dash["layouts"].get(old_key, {})
        new_layout = dict(old_layout)
        # Shift the markdown header down too — KPIs are at top
        if old_key == "0":
            new_layout["y"] = KPI_ROW_HEIGHT
        else:
            new_layout["y"] = old_layout.get("y", 0) + KPI_ROW_HEIGHT

        # ── 3. Add davis config to all data tiles ────────────────────────
        if tile.get("type") == "data" and "davis" not in tile:
            tile["davis"] = {"enabled": False, "davisVisualization": {"isAvailable": True}}

        new_tiles[new_key] = tile
        new_layouts[new_key] = new_layout

    dash["tiles"] = new_tiles
    dash["layouts"] = new_layouts

    # ── 4. Add defaultTimeframe ──────────────────────────────────────────
    if "settings" not in dash:
        dash["settings"] = {}
    dash["settings"]["defaultTimeframe"] = {
        "enabled": True,
        "value": "now()-2h"
    }

    # Write back
    with open(path, "w", newline="\n") as f:
        json.dump(dash, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[{vendor_key}] Enhanced dashboard: {path}")
    print(f"  - Added 4 KPI singleValue tiles")
    print(f"  - Shifted {len(old_keys)} existing tiles down by {KPI_ROW_HEIGHT}")
    print(f"  - Added davis config to data tiles")
    print(f"  - Set defaultTimeframe to 2h")


if __name__ == "__main__":
    for vendor_key, v in VENDORS.items():
        enhance_dashboard(vendor_key, v)
    print("\nDone. Review changes with `git diff`.")
