from __future__ import annotations

from dataclasses import asdict

from .schema import NetOpsResponse, validate_response

DESTRUCTIVE_PATTERNS = (
    "shutdown",
    "erase startup-config",
    "write erase",
    "reload",
    "no router",
)


class NetOpsCommanderEngine:
    """Deterministic policy engine scaffold to pair with a local LLM runtime."""

    policy_version = "2.0.0-alpha"

    def run(
        self,
        *,
        request_id: str,
        action: str,
        vendor: str,
        device: str,
        query: str,
        actor: str = "netops_user",
    ) -> dict:
        commands = self._generate_candidate_commands(action=action, vendor=vendor, query=query)
        blocked_reasons = self._detect_destructive(commands)
        requires_confirm = bool(blocked_reasons)
        risk_level = "HIGH" if requires_confirm else "LOW"
        syntax_validated = self._basic_syntax_validator(commands)

        payload = {
            "request_id": request_id,
            "action": action,
            "vendor": vendor,
            "device": device,
            "risk_level": risk_level,
            "requires_confirm": requires_confirm,
            "commands": commands,
            "syntax_validated": syntax_validated,
            "confidence": 0.99 if syntax_validated else 0.5,
            "blocked_reasons": blocked_reasons,
            "rollback_package": {
                "strategy": "inverse_commands",
                "commands": self._build_rollback(commands),
            },
            "audit": {
                "timestamp_utc": NetOpsResponse.now_timestamp(),
                "actor": actor,
                "policy_version": self.policy_version,
            },
        }
        response = validate_response(payload)
        return asdict(response)

    def _generate_candidate_commands(self, *, action: str, vendor: str, query: str) -> list[str]:
        text = query.lower()
        if action == "generate_config" and "ospf" in text:
            if vendor == "cisco_ios_xe":
                return [
                    "router ospf 1",
                    " area 0 authentication message-digest",
                    " network 10.0.0.0 0.255.255.255 area 0",
                ]
            return ["set protocols ospf area 0.0.0.0"]

        if action == "troubleshoot" and "bgp" in text:
            return ["show ip bgp summary", "show ip bgp neighbors"]

        if action == "validate_syntax":
            return ["! syntax validation requested"]

        return [f"! unsupported query template for vendor={vendor}"]

    def _detect_destructive(self, commands: list[str]) -> list[str]:
        reasons: list[str] = []
        for command in commands:
            lowered = command.lower()
            for pattern in DESTRUCTIVE_PATTERNS:
                if pattern in lowered:
                    reasons.append(f"Blocked destructive pattern: {pattern}")
        return reasons

    def _basic_syntax_validator(self, commands: list[str]) -> bool:
        if not commands:
            return False
        return all(command.strip() != "" for command in commands)

    def _build_rollback(self, commands: list[str]) -> list[str]:
        rollback: list[str] = []
        for command in commands:
            stripped = command.strip()
            if stripped.startswith("no "):
                rollback.append(stripped.removeprefix("no "))
            elif stripped.startswith("show"):
                rollback.append("! show command rollback not required")
            elif stripped.startswith("!"):
                rollback.append("! no rollback")
            else:
                rollback.append(f"no {stripped}")
        return rollback
