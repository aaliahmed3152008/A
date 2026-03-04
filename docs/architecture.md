# NetOps-Commander LLM Architecture (PRD v2.0.0)

## 1) Objective

Build an on-prem, air-gapped, multi-vendor NetOps LLM system that produces machine-consumable JSON outputs for configuration generation, troubleshooting, RCA correlation, and safe execution planning.

## 2) Pipeline

### Input Layer

- User query (Arabic/English)
- Device state snapshots
- `show run` payloads
- Syslog streams
- SNMP metrics

### Reasoning Layer

1. **Context Assembler**
   - Normalizes structured and unstructured network input.
   - Splits long contexts into stable chunks with protocol tags.
2. **Protocol Reasoner**
   - Applies routing/switching/security/QoS/multicast/NAT domain templates.
3. **RCA Correlator**
   - Links events, counters, and topology state to likely root causes.
4. **Multi-Vendor Parser**
   - Converts intent into vendor-specific command blocks.

### Safety Layer

1. **Risk Scorer**
   - Rates operational impact: `LOW | MEDIUM | HIGH | CRITICAL`.
2. **Syntax Validator**
   - Rejects malformed command sequences before output.
3. **Destructive Command Blocker**
   - Blocks high-risk operations unless explicit staged confirmation is required.
4. **Rollback Planner**
   - Creates rollback package for each generated change set.

### Output Layer

- Strict JSON schema only.
- Automation-ready command list.
- Confirm/deny gate for risky changes.
- Audit and rollback metadata.

## 3) Latency and Scale Strategy

- Real-time target: sub-2s for normal inference paths.
- Horizontal scaling across inference workers.
- Batch + streaming ingestion for massive telemetry.
- Context window target >= 32k tokens for large configs and logs.

## 4) Security and Governance

- AES-256 at rest and TLS 1.3 in transit.
- RBAC and MFA enforcement for privileged actions.
- Immutable audit log entries for every request/response.
- Strict no-egress posture for on-prem deployment.

## 5) Model Runtime Profile

- Base model choices:
  - Llama-3-70B
  - Mixtral-8x7B
- Quantization:
  - 4-bit AWQ/GGUF for high-throughput local inference
  - 8-bit GPTQ where required
- Fine-tuning:
  - QLoRA + LoRA adapters on network-specific datasets.

## 6) KPI Alignment

- Syntax accuracy: 99%+
- JSON validity: 100%
- Destructive output without confirmation: 0%
- Data egress: 0%
- Response time: <2s target
