# Strict JSON Output Schema

```json
{
  "request_id": "string",
  "action": "generate_config | troubleshoot | rca | validate_syntax",
  "vendor": "string",
  "device": "string",
  "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
  "requires_confirm": "boolean",
  "commands": ["string"],
  "syntax_validated": "boolean",
  "confidence": "number (0.0 - 1.0)",
  "blocked_reasons": ["string"],
  "rollback_package": {
    "strategy": "string",
    "commands": ["string"]
  },
  "audit": {
    "timestamp_utc": "ISO-8601 string",
    "actor": "string",
    "policy_version": "string"
  }
}
```

## Contract Rules

1. No free text outside JSON.
2. `commands` must be explicit, executable CLI lines.
3. If destructive commands are detected:
   - set `requires_confirm=true`
   - set `risk_level` to at least `HIGH`
   - list reasons in `blocked_reasons`
4. `syntax_validated=true` only when all commands pass syntax checks.
5. `rollback_package.commands` must be present when `commands` is non-empty.
