# On-Prem Deployment Reference

## Runtime Targets

- Primary serving engines:
  - vLLM (GPU inference service)
  - llama.cpp (CPU/GPU edge nodes)
  - Ollama (operator-friendly packaging)
- No internet dependency after artifact sync.

## Air-Gap Requirements

1. Mirror model artifacts into internal registry.
2. Disable outbound routes from inference VLAN.
3. Use private package mirrors for Python/system dependencies.
4. Store logs in immutable internal SIEM.

## Suggested Services

- `netops-llm-inference`
- `netops-policy-engine`
- `netops-audit-writer`
- `netops-automation-adapter`

## Security Baseline

- TLS 1.3 mutual auth between services.
- AES-256 encrypted persistent volumes.
- RBAC + MFA in control-plane UI.
- Break-glass workflow for emergency override.
