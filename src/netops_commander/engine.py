from __future__ import annotations

from dataclasses import asdict

from .schema import NetOpsResponse, validate_response

DESTRUCTIVE_PATTERNS = (
    "shutdown",
    "erase startup-config",
    "write erase",
    "format",
    "reload",
    "delete flash:",
)


class NetOpsCommanderEngine:
    """Policy-first execution planner to pair with local LLM inference runtimes."""

    policy_version = "2.1.0-alpha"

    def run(
        self,
        *,
        request_id: str,
        action: str,
        vendor: str,
        device: str,
        query: str,
        actor: str = "netops_user",
        confirmed: bool = False,
    ) -> dict:
        candidate_commands = self._generate_candidate_commands(action=action, vendor=vendor, query=query)
        blocked_reasons = self._detect_destructive(candidate_commands)

        requires_confirm = bool(blocked_reasons)
        risk_level = self._risk_level_from_signals(blocked_reasons, action)

        commands = candidate_commands
        if requires_confirm and not confirmed:
            commands = []
            blocked_reasons.append("Execution blocked until multi-stage confirmation is provided")

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
            "confidence": self._confidence_score(action=action, syntax_validated=syntax_validated, blocked=requires_confirm),
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
                    "area 0 authentication message-digest",
                    "network 10.0.0.0 0.255.255.255 area 0",
                ]
            if vendor == "juniper_junos":
                return [
                    "set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 authentication md5 1 key NETOPS",
                ]

        if action == "generate_config" and "shutdown" in text:
            return ["interface GigabitEthernet0/1", "shutdown"]

        if action == "troubleshoot" and "bgp" in text:
            return ["show ip bgp summary", "show ip bgp neighbors"]

        if action == "rca" and ("flap" in text or "unstable" in text):
            return [
                "show logging | include LINK-3-UPDOWN",
                "show interfaces counters errors",
                "show spanning-tree detail | include occurr",
            ]

        if action == "validate_syntax":
            return ["! syntax validation requested"]

        return [f"! unsupported query template for vendor={vendor} action={action}"]

    def _detect_destructive(self, commands: list[str]) -> list[str]:
        reasons: list[str] = []
        for command in commands:
            lowered = command.lower()
            for pattern in DESTRUCTIVE_PATTERNS:
                if pattern in lowered:
                    reasons.append(f"Blocked destructive pattern: {pattern}")
        return reasons

    def _risk_level_from_signals(self, blocked_reasons: list[str], action: str) -> str:
        if blocked_reasons:
            return "CRITICAL"
        if action in {"generate_config", "rca"}:
            return "MEDIUM"
        return "LOW"

    def _confidence_score(self, *, action: str, syntax_validated: bool, blocked: bool) -> float:
        if blocked:
            return 0.75
        if not syntax_validated:
            return 0.4
        if action == "generate_config":
            return 0.98
        return 0.95

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
            elif stripped.startswith("show") or stripped.startswith("!"):
                rollback.append("! no rollback")
            elif stripped.startswith("set "):
                rollback.append(stripped.replace("set ", "delete ", 1))
            else:
                rollback.append(f"no {stripped}")
        return rollback
