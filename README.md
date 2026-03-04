# NetOps-Commander LLM (PRD v2.0.0 Blueprint)

This repository converts the provided PRD into an implementation-ready, on-premise project scaffold for a Tier-3-grade NetOps assistant.

## What is implemented

- **Architecture aligned to PRD**:
  - Input ingestion (`user_query`, `show run`, `syslog`, `snmp`, `device_state`)
  - Reasoning pipeline (`context_assembler`, `protocol_reasoner`, `rca_correlator`, `multi_vendor_parser`)
  - Safety pipeline (`risk_scorer`, `syntax_validator`, `destructive_cmd_blocker`, `rollback_planner`)
  - Output as **strict JSON envelope** for direct automation.
- **Protocol domain coverage map** matching routing/switching/security/qos/multicast/auth/nat/monitoring requirements.
- **Deterministic safety guardrails** for destructive command blocking and mandatory confirmation.
- **On-prem deployment assets** for `vLLM`, `llama.cpp`, and `Ollama` compatibility planning.

## Repository layout

- `docs/architecture.md`: detailed design that maps PRD sections to components.
- `docs/json_schema.md`: strict output schema and field semantics.
- `docs/deployment_onprem.md`: air-gapped deployment reference.
- `configs/protocol_coverage.yaml`: protocol/domain taxonomy from PRD.
- `src/netops_commander/engine.py`: orchestration and safety gating logic.
- `src/netops_commander/schema.py`: strict schema validator.
- `src/netops_commander/prompts.py`: system prompt template enforcing JSON-only behavior.
- `src/netops_commander/cli.py`: local CLI entrypoint.
- `tests/test_engine.py`: baseline regression tests.

## Quick start

```bash
python -m src.netops_commander.cli \
  --request-id CFG-2025-0391 \
  --action generate_config \
  --vendor cisco_ios_xe \
  --device R-CORE-01 \
  --query "configure ospf area 0 auth"
```

## Status

- Stage: **ALPHA scaffold**
- Scope: **Design + deterministic policy layer + interface contracts**
- Next: connect to chosen base model (`Llama-3-70B` or `Mixtral-8x7B`) and fine-tuning dataset pipeline.
