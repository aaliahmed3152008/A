from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

ALLOWED_ACTIONS = {"generate_config", "troubleshoot", "rca", "validate_syntax"}
ALLOWED_RISK = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


@dataclass
class RollbackPackage:
    strategy: str
    commands: list[str] = field(default_factory=list)


@dataclass
class Audit:
    timestamp_utc: str
    actor: str
    policy_version: str


@dataclass
class NetOpsResponse:
    request_id: str
    action: str
    vendor: str
    device: str
    risk_level: str
    requires_confirm: bool
    commands: list[str]
    syntax_validated: bool
    confidence: float
    blocked_reasons: list[str]
    rollback_package: RollbackPackage
    audit: Audit

    @staticmethod
    def now_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()


class SchemaValidationError(ValueError):
    pass


def validate_response(payload: dict[str, Any]) -> NetOpsResponse:
    missing = {
        "request_id",
        "action",
        "vendor",
        "device",
        "risk_level",
        "requires_confirm",
        "commands",
        "syntax_validated",
        "confidence",
        "blocked_reasons",
        "rollback_package",
        "audit",
    } - payload.keys()
    if missing:
        raise SchemaValidationError(f"Missing required fields: {sorted(missing)}")

    if payload["action"] not in ALLOWED_ACTIONS:
        raise SchemaValidationError("Invalid action")
    if payload["risk_level"] not in ALLOWED_RISK:
        raise SchemaValidationError("Invalid risk level")
    if not isinstance(payload["requires_confirm"], bool):
        raise SchemaValidationError("requires_confirm must be boolean")
    if not isinstance(payload["commands"], list) or not all(isinstance(x, str) for x in payload["commands"]):
        raise SchemaValidationError("commands must be list[str]")
    if not isinstance(payload["syntax_validated"], bool):
        raise SchemaValidationError("syntax_validated must be boolean")
    if not isinstance(payload["confidence"], (int, float)) or not 0 <= payload["confidence"] <= 1:
        raise SchemaValidationError("confidence must be 0..1")
    if not isinstance(payload["blocked_reasons"], list) or not all(isinstance(x, str) for x in payload["blocked_reasons"]):
        raise SchemaValidationError("blocked_reasons must be list[str]")

    rollback = payload["rollback_package"]
    if not isinstance(rollback, dict):
        raise SchemaValidationError("rollback_package must be object")
    if "strategy" not in rollback or "commands" not in rollback:
        raise SchemaValidationError("rollback_package requires strategy and commands")

    audit = payload["audit"]
    if not isinstance(audit, dict):
        raise SchemaValidationError("audit must be object")
    for key in ("timestamp_utc", "actor", "policy_version"):
        if key not in audit:
            raise SchemaValidationError(f"audit missing {key}")

    return NetOpsResponse(
        request_id=str(payload["request_id"]),
        action=payload["action"],
        vendor=str(payload["vendor"]),
        device=str(payload["device"]),
        risk_level=payload["risk_level"],
        requires_confirm=payload["requires_confirm"],
        commands=payload["commands"],
        syntax_validated=payload["syntax_validated"],
        confidence=float(payload["confidence"]),
        blocked_reasons=payload["blocked_reasons"],
        rollback_package=RollbackPackage(
            strategy=str(rollback["strategy"]),
            commands=list(rollback["commands"]),
        ),
        audit=Audit(
            timestamp_utc=str(audit["timestamp_utc"]),
            actor=str(audit["actor"]),
            policy_version=str(audit["policy_version"]),
        ),
    )
