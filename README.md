# demoability_logs_generators

Dynatrace Workflow-based log generators for simulating realistic enterprise log sources in demo environments.

Each generator is a Dynatrace Workflow (JS action) that generates structured log entries and ingests them via the **Log Ingest API v2** into Grail. No real infrastructure needed.

## Structure

```
network-security/
  palo-alto/         ← Palo Alto PAN-OS logs (traffic, threat, system, config)
  fortinet/          ← FortiGate logs (traffic, utm/ips, utm/virus, utm/webfilter, vpn, system)
  cisco/             ← Cisco ASA/FTD logs (connection, ACL, IPS, VPN, platform/system)
  unified/           ← Cross-vendor normalized dashboard + notebook
api-gateway/
  kong/              ← Kong access + policy logs (planned)
  mulesoft/          ← MuleSoft API gateway logs (planned)
idp/
  okta/              ← Okta System Log (planned)
  entra-id/          ← Entra ID sign-in + audit logs (planned)
```

Each vendor folder contains:
- `workflows/` — workflow YAML (source of truth for PA) and JSON (API deploy)
- `queries/` — DQL queries for the Logs app, Notebooks, Dashboards
- `notebooks/` — Dynatrace Notebook JSON
- `dashboards/` — Dynatrace Dashboard JSON

## Target Environments

All generators are developed and validated on **oqr staging** before promotion to Playground.

## Deploy with dtctl

```bash
# Switch to staging context
dtctl config use-context staging

# Deploy workflow (in-place update if ID matches)
dtctl apply -f network-security/palo-alto/workflows/palo_alto_log_generator_api.json --plain

# Deploy dashboard / notebook (use deploy scripts)
python3 deploy_dashboards.py
python3 deploy_unified.py

# Execute manually
dtctl exec workflow <workflow-id> --plain

# Verify logs
dtctl query "fetch logs | filter log.source == \"palo-alto-firewall\" | summarize count()" --plain
```

## Deployment Status

| Vendor | Category | Deployed (staging) |
|--------|----------|-------------------|
| Palo Alto | Network Security | ✅ |
| Fortinet FortiGate | Network Security | ✅ |
| Cisco ASA/FTD | Network Security | ✅ |
| Kong | API Gateway | ❌ |
| MuleSoft | API Gateway | ❌ |
| Okta | IdP | ❌ |
| Entra ID | IdP | ❌ |

---

## Log Coverage — Network Security

### Palo Alto Networks (PAN-OS 10.x)

`log.source = "palo-alto-firewall"` | Device: `PA-5260-LAB` | Format: PAN-OS CSV syslog

| Log Family | Subtype / Event | Format | Key Attributes |
|---|---|---|---|
| **TRAFFIC** | `end` — allow, deny, drop, reset-both | PAN-OS 10.x CSV (~103 fields) | `paloalto.action`, `paloalto.rule`, `paloalto.app`, `paloalto.src`, `paloalto.dst`, `paloalto.dport`, `paloalto.from_zone`, `paloalto.to_zone`, `paloalto.bytes_sent`, `paloalto.session_end_reason` |
| **THREAT** | `vulnerability` — MS SMBv1 EternalBlue, Log4Shell, BlueKeep, PHP RFI, SQL Injection | PAN-OS 10.x CSV | `paloalto.subtype`, `paloalto.threat_id`, `paloalto.threat_name`, `paloalto.threat_category`, `paloalto.severity`, `paloalto.action` (block-ip / drop / reset-both / alert) |
| **THREAT** | `spyware` — Cobalt Strike C2, DNS C2 Beacon | PAN-OS 10.x CSV | same as above |
| **THREAT** | `wildfire-virus` — WildFire Malware Detected | PAN-OS 10.x CSV | same as above |
| **THREAT** | `url` — Phishing URL Detected | PAN-OS 10.x CSV | same as above |
| **THREAT** | `file` — Suspicious PE File Transferred | PAN-OS 10.x CSV | same as above |
| **SYSTEM** | `ha` — HA state change, peer heartbeat failure | PAN-OS 10.x CSV | `paloalto.subtype`, `paloalto.event_id`, `paloalto.description`, `paloalto.severity` |
| **SYSTEM** | `interface` — ethernet up/down | PAN-OS 10.x CSV | same as above |
| **SYSTEM** | `general` — config commit (success/fail), cert expiry | PAN-OS 10.x CSV | same as above |
| **SYSTEM** | `globalprotect` — GP tunnel connected, GP auth failure | PAN-OS 10.x CSV | same as above |
| **SYSTEM** | `login` — admin login success/fail | PAN-OS 10.x CSV | same as above |
| **SYSTEM** | `routing` — BGP peer down | PAN-OS 10.x CSV | same as above |
| **CONFIG** | `set` / `delete` / `commit` — admin change audit | PAN-OS 10.x CSV | `paloalto.config_cmd`, `paloalto.config_path`, `paloalto.admin`, `paloalto.client`, `paloalto.result` |

**Distribution per run (50 entries):** ~60% TRAFFIC · ~20% THREAT · ~12% SYSTEM · ~8% CONFIG

---

### Fortinet FortiGate (FortiOS 7.x)

`log.source = "fortinet-fortigate"` | Device: `FGT-600F-PROD` | Format: FortiOS key=value syslog

| Log Family | type/subtype | Key Attributes |
|---|---|---|
| **traffic/forward** | Accept (60%) + deny/server-rst/client-rst (40%) | `fortinet.action`, `fortinet.policyname`, `fortinet.srcip`, `fortinet.dstip`, `fortinet.dstport`, `fortinet.service`, `fortinet.app`, `fortinet.appcat`, `fortinet.srccountry`, `fortinet.sentbyte`, `fortinet.rcvdbyte`, `fortinet.duration` |
| **utm/ips** | 7 signatures: MS17-010/EternalBlue, Cobalt Strike, Log4j, SSH Brute Force, BlueKeep, SQL Injection, FTP Bounce | `fortinet.attack`, `fortinet.severity`, `fortinet.attackid`, `fortinet.cve` (where applicable) |
| **utm/virus** (AV) | 8 signatures: Kryptik Trojan, CoinMiner, MSIL Ransomware, Mirai Botnet, HTML Phishing, CobaltStrike Backdoor, Log4j Exploit, Generic Virus | `fortinet.virus`, `fortinet.category`, `fortinet.severity`, `fortinet.filename`, `fortinet.quarantined` |
| **utm/webfilter** | 8 URL categories: Malicious Websites, Phishing, Gambling, Social Networking, Streaming Media, Command and Control, Hacking, News | `fortinet.url`, `fortinet.hostname`, `fortinet.cat`, `fortinet.catdesc`, `fortinet.user`, `fortinet.action` (block / passthrough) |
| **event/vpn** | SSL VPN login success (80%) + login failed (20%) | `fortinet.user`, `fortinet.tunneltype`, `fortinet.reason`, `fortinet.remip` |
| **event/system** | Admin login/logout, config-change, HA switch-over, interface-down | `fortinet.action`, `fortinet.level` (information / warning / critical) |

**Distribution per run (50 entries):** ~50% traffic · ~14% utm/ips · ~10% utm/virus · ~10% utm/webfilter · ~10% event/vpn · ~6% event/system

---

### Cisco ASA / Firepower FTD

`log.source = "cisco-asa"` | Devices: `ASA-EDGE-01`, `FTD-EDGE-01` | Format: `%ASA-<sev>-<msgid>:` / `%FTD-<sev>-<msgid>:`

| Log Family | Message IDs | Description | Key Attributes |
|---|---|---|---|
| **Connection events** | `302013` / `302014` | TCP connection built / teardown | `cisco.action` (built/teardown), `cisco.src_ip`, `cisco.dst_ip`, `cisco.src_port`, `cisco.dst_port`, `cisco.protocol`, `cisco.connection_id`, `cisco.bytes` |
| **Connection events** | `302015` / `302016` | UDP connection built / teardown | same as above |
| **Syslog security — ACL deny** | `106023` | Explicit deny by access-group | `cisco.action` (deny), `cisco.acl_name`, `cisco.src_ip`, `cisco.dst_ip`, `cisco.protocol` |
| **Syslog security — ACL permit** | `106100` | Access-list permit with hit count | `cisco.action` (permit), `cisco.acl_name` |
| **Syslog security — port block** | `710003` | TCP access denied to ASA interface | `cisco.action` (deny), `cisco.src_ip`, `cisco.dst_ip`, `cisco.dst_port` |
| **VPN — AnyConnect** | `113039` | VPN session started | `cisco.action` (vpn-start), `cisco.user`, `cisco.group`, `cisco.src_ip` |
| **VPN — AnyConnect** | `113019` | VPN session disconnected | `cisco.action` (vpn-disconnect), `cisco.user`, `cisco.group`, `cisco.session_type`, `cisco.bytes_sent`, `cisco.bytes_received`, `cisco.reason` |
| **VPN — AAA** | `113005` | AAA user authentication rejected | `cisco.action` (auth-failed), `cisco.user`, `cisco.aaa_server` |
| **IPS / Intrusion** | `733100` (`%ASA`) | Snort IDS/IPS drop — 10 signatures (EternalBlue, Log4Shell, BlueKeep, Cobalt Strike, SQL Injection, etc.) | `cisco.action` (ips-drop), `cisco.ips_sid`, `cisco.ips_msg`, `cisco.ips_priority`, `cisco.cve` |
| **IPS / Intrusion** | `430003` (`%FTD`) | Firepower AC intrusion event | same as above |
| **Platform / System** | `104001` / `104002` | HA primary down / standby recovered | `cisco.action` (system), `cisco.message_id`, `cisco.severity_level` |
| **Platform / System** | `105003` | HA heartbeat missing | same as above |
| **Platform / System** | `111008` / `111010` | Admin CLI command executed | same as above |
| **Platform / System** | `111009` | Admin reload command | same as above |
| **Platform / System** | `199002` | Startup completed | same as above |
| **Platform / System** | `321001` | SSH process failure | same as above |
| **Platform / System** | `413172` / `501102` | NAT detection / interface config | same as above |

**Distribution per run (50 entries):** ~20% 302013 · ~12% 302014 · ~10% 302015 · ~5% 302016 · ~13% 106023 · ~10% 106100 · ~7% 710003 · ~5% 113039 · ~5% 113019 · ~3% 113005 · ~6% IPS · ~4% system

---

## Credits

Palo Alto generator originally by [@rstojan](https://github.com/rstojan/firewall_project).
