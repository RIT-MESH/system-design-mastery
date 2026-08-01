# Configuration Management and Change Automation

> **Prev:** Syslog, SNMP, NetFlow and Monitoring | **Next:** Network Security and Segmentation

## Learning objectives

After this chapter you can explain network configuration management, change automation, drift detection, intent-based networking, and infrastructure-as-code for network devices.

## Overview

Network automation manages device configurations programmatically: versioned configs, templated deployments, drift detection against baselines, and orchestrated change rollout. Intent-based networking translates business intent (policies, SLAs) into device configurations. Infrastructure-as-code applies the GitOps model to network devices: declare desired state in Git, reconcile automatically.

## How it works

Configs are stored in a versioned repository. A change is authored as a template or diff, reviewed, approved, and deployed via an automation engine (NETCONF, RESTCONF, CLI scraping). Drift detection compares live configs to the repo baseline. Intent-based networking adds a translation layer: intent (connectivity policy) to config (ACLs, routes). GitOps for network: Git is the source of truth; an agent reconciles devices to the declared state.

## Architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Git[Git: desired config] --> Engine[Automation engine]
  Engine --> Dev[Devices: deploy]
  Dev --> Drift[Drift detector]
  Drift -.divergence.-> Alert[Alert and ticket]
  Intent[Intent policy] --> Translate[Intent-to-config translation]
  Translate --> Git
```

## Trade-offs

GitOps (auditable, declarative) vs imperative scripts (fast, less safe). Templated (consistent) vs per-device (flexible). Drift detection (safe) vs trust (simple). Intent-based (high-level) vs direct config (granular).

## When NOT to use this

See trade-offs above; do not apply a pattern where a simpler approach suffices.

## Common mistakes

No rollback for failed changes; drift detected but not remediated; Git as source of truth but devices manually edited (divergence); CLI scraping (fragile) vs NETCONF (structured).

## Failure modes

Automation engine deploys wrong config to wrong devices; drift detector down (silent divergence); Git state and device state permanently out of sync; intent translation produces invalid config.

## Review questions

1. What is the GitOps model for network devices? 2. How does drift detection work? 3. What is intent-based networking? 4. Why is CLI scraping fragile? 5. What happens when Git and device state diverge?

## Further reading

NETCONF RFC 6241; RESTCONF RFC 8040; intent-based networking references; Level 9 GitOps; configuration drift case study.

---
Prev: Syslog, SNMP, NetFlow and Monitoring | Next: Network Security and Segmentation
