# demoability_logs_generators

Dynatrace Workflow-based log generators for simulating realistic enterprise log sources in demo environments.

Each generator is a Dynatrace Workflow (JS action) that generates structured log entries and ingests them via the **Log Ingest API v2** into Grail. No real infrastructure needed.

## Structure

```
network-security/
  palo-alto/         ← Palo Alto PAN-OS traffic logs (done)
  fortinet/          ← FortiGate logs (planned)
  cisco/             ← Cisco ASA/FTD logs (planned)
api-gateway/
  kong/              ← Kong access + policy logs (planned)
  mulesoft/          ← MuleSoft API gateway logs (planned)
idp/
  okta/              ← Okta System Log (planned)
  entra-id/          ← Entra ID sign-in + audit logs (planned)
```

Each vendor folder contains:
- `workflows/` — workflow YAML (UI import) and JSON (API import)
- `queries/` — DQL queries for the Logs app, Notebooks, Dashboards
- `notebooks/` — Dynatrace Notebook JSON
- `dashboards/` — Dynatrace Dashboard JSON

## Target Environments

All generators are developed and validated on **oqr staging** (`oqr47576.sprint.apps.dynatracelabs.com`) before promotion to Playground.

## Deploy with dtctl

```bash
# Switch to staging context
dtctl config use-context staging

# Deploy workflow
dtctl apply -f network-security/palo-alto/workflows/palo_alto_log_generator_api.json --plain

# Deploy notebook (wrap first — see deploy script)
# Deploy dashboard (wrap first — see deploy script)

# Execute manually
dtctl exec workflow <workflow-id> --plain

# Verify logs
dtctl query "fetch logs | filter log.source == \"palo-alto-firewall\" | summarize count()" --plain
```

## Status

| Vendor | Category | Workflow | Queries | Notebook | Dashboard | Deployed (staging) |
|--------|----------|----------|---------|----------|-----------|-------------------|
| Palo Alto | Network Security | ✅ | ✅ 15 queries | ✅ | ✅ | ✅ |
| Fortinet FortiGate | Network Security | ✅ | ✅ 15 queries | ✅ | ✅ | ✅ |
| Cisco ASA/FTD | Network Security | ✅ | ✅ 15 queries | ✅ | ✅ | ✅ |
| Kong | API Gateway | ❌ | ❌ | ❌ | ❌ | ❌ |
| MuleSoft | API Gateway | ❌ | ❌ | ❌ | ❌ | ❌ |
| Okta | IdP | ❌ | ❌ | ❌ | ❌ | ❌ |
| Entra ID | IdP | ❌ | ❌ | ❌ | ❌ | ❌ |

## Credits

Palo Alto generator originally by [@rstojan](https://github.com/rstojan/firewall_project).
