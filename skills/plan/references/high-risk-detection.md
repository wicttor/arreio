---
title: High-Risk Area Detection
description: "Scan the task description and scoped context for high-risk keywords across six areas: Security, Payments, APIs, Migrations, Complex Logic, and Infrastructure."
type: reference
version: 1.2
timestamp: "2026-10-23"
---

# High-Risk Area Detection

This file documents how the research phase identifies high-risk areas. Keywords only **nominate candidates**; the agent then **confirms or dismisses each candidate by the real consequence of failure**. Only confirmed areas count toward the risk level. A keyword match alone never sets a risk level.

## Step A: Nominate candidates (keywords)

Scan the task description and scoped context for these keywords. Each hit nominates an area; it does not confirm it:

| Area           | Keywords                                                                                               | Risk Category |
| -------------- | ------------------------------------------------------------------------------------------------------ | ------------- |
| Security       | auth, jwt, oauth, session, encryption, ssl, tls, certificate, permission, rbac, acl, audit, credential | CRITICAL      |
| Payments       | payment, billing, stripe, checkout, invoice, refund, transaction, subscription, pci, card              | CRITICAL      |
| APIs           | api, rest, graphql, endpoint, integration, webhook, rate-limit, versioning                             | HIGH          |
| Migrations     | migration, upgrade, data, schema, version, backward-compat, deprecation                                | HIGH          |
| Complex Logic  | algorithm, analysis, processing, computation, ml, analytics, optimization                              | HIGH          |
| Infrastructure | deploy, kubernetes, docker, scaling, network, cdn, load-balance, failover, disaster-recovery           | HIGH          |

## Step B: Confirm or dismiss each candidate

For every nominated area, decide `confirmed` or `dismissed` and write one line of evidence. Judge the consequence of failure in this project, not the word.

| Area | Confirm only when the work really involves | Typical dismissals (keyword used in a general sense) |
| ---- | ------------------------------------------ | ---------------------------------------------------- |
| Security | Authentication, authorization, secrets, or protecting data from other people | "session" = a game or editor session; "audit" = a code review; "permission" = a file mode |
| Payments | Real money, a payment provider, billing, or financial records | "transaction" = an in-process state change or a database transaction; "card" = a UI card; "subscription" = an event subscription |
| APIs | A public or third-party interface other systems call | "api" = an internal engine/library call; "integration" = wiring two local modules |
| Migrations | Changing data or schemas that already exist in use and must keep working | "schema"/"version"/"data" for a new local format with no existing data to migrate |
| Complex Logic | Algorithms where a subtle bug is costly and hard to detect | "processing"/"analysis" as plain data handling |
| Infrastructure | Deployment, networks, or operational environments the change alters | "network" for an in-game concept; "deploy" for a local build step |

Rules:

- **Confirmed** needs evidence you can cite: a file, a requirement quote, or a named external system. "The word appears" is not evidence.
- **Critical** (Security, Payments) additionally needs the cited evidence to show the real consequence (money moves, access control changes, secrets are handled). Without it, dismiss or downgrade to the next area it honestly fits.
- A source of truth that already specifies the behavior, its tests, and its failure handling lowers uncertainty but does not by itself dismiss an area; judge the consequence.
- Record every candidate, confirmed or dismissed, with its reason in the Research Findings (`High-Risk Detection`). A dismissal is cheap; an unexplained Critical is not allowed.

## Area Definitions

### Security (CRITICAL)

Involves authentication, authorization, session management, encryption, or credential handling.

- **Examples:** JWT implementation, OAuth integration, session cookies, SSL certificates, password hashing
- **Why critical:** Security breaches can compromise the entire system
- **Escalation:** Recommend external research unless extensive local patterns exist (see the matrix below)

### Payments (CRITICAL)

Involves payment processing, billing, invoicing, or financial transactions.

- **Examples:** Stripe integration, checkout flow, refund logic, subscription management
- **Why critical:** Payment systems have strict compliance requirements (PCI DSS); errors cause financial loss
- **Escalation:** Recommend external research unless extensive local patterns exist; verify compliance requirements

### APIs (HIGH)

Involves REST, GraphQL, or other API design and integration.

- **Examples:** RESTful endpoint design, GraphQL schema, third-party API integration, versioning
- **Why high:** Poor API design can create compatibility issues; integration errors block downstream work
- **Escalation:** Recommend external research if designing new APIs or integrating unfamiliar third-party services

### Migrations (HIGH)

Involves schema changes, version upgrades, or data migration with impact on production.

- **Examples:** Database schema migration, framework upgrade, data format change, breaking API changes
- **Why high:** Migrations can cause data loss or downtime if not carefully planned
- **Escalation:** Recommend external research for migrations without local patterns

### Complex Logic (HIGH)

Involves algorithms, machine learning, complex computations, or analysis.

- **Examples:** Sorting/searching algorithms, ML model selection, financial calculations, performance-critical code
- **Why high:** Bugs in complex logic can cascade; optimization mistakes are hard to reverse
- **Escalation:** Recommend external research if no local examples exist

### Infrastructure (HIGH)

Involves deployment, container orchestration, scaling, or network architecture.

- **Examples:** Kubernetes deployment, Docker setup, load balancing, CDN configuration, disaster recovery
- **Why high:** Infrastructure mistakes can cause downtime or security vulnerabilities
- **Escalation:** Recommend external research for infrastructure patterns not yet documented

## Risk Level Determination

After Step B, assign a risk level from the **confirmed** areas only:

```
risk_level = determine_risk(areas_confirmed, high_risk_count)

if any_confirmed_area_is_security_or_payments:
  risk_level = CRITICAL
  reason = "Critical area confirmed: " + critical_area + " (" + evidence + ")"
elif high_risk_count >= 2:
  risk_level = HIGH
  reason = "Multiple high-risk areas confirmed: " + areas_confirmed.join(", ")
elif any_confirmed_area_is_api_migration_logic_infra:
  risk_level = MEDIUM
  reason = "High-risk area confirmed: " + area_name
else:
  risk_level = LOW
  reason = "No high-risk areas confirmed"
```

## Mapping to Research Decision

> **Authoritative.** The Research phase (Step 3) looks up its external-research decision directly in the matrix below, using the detected **risk level** and the **patterns found count**. Do not apply a separate formula — this matrix is the single source of truth.

Use risk level to determine if external research should be recommended:

| Risk Level | Patterns Found | Decision           | Notes                                        |
| ---------- | -------------- | ------------------ | -------------------------------------------- |
| CRITICAL   | 0-2            | Recommend external | Insufficient local patterns; must research   |
| CRITICAL   | 3+             | Optional external  | Strong local patterns; external optional     |
| HIGH       | 0-2            | Recommend external | Insufficient local patterns; must research   |
| HIGH       | 3+             | Skip external      | Strong local patterns; local code is enough  |
| MEDIUM     | 0-1            | Recommend external | Limited local examples; external recommended |
| MEDIUM     | 2+             | Optional external  | Adequate local patterns; external optional   |
| LOW        | any            | Skip external      | Low risk; no external research needed        |

External research informs the plan; it never overrides the source of truth. When research disagrees with an accepted source document, record the difference in `Open Decisions` instead of changing the source or adding units.
