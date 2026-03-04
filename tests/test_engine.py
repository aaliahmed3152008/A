from src.netops_commander.engine import NetOpsCommanderEngine


def test_generate_config_ospf_cisco() -> None:
    engine = NetOpsCommanderEngine()
    output = engine.run(
        request_id="CFG-1",
        action="generate_config",
        vendor="cisco_ios_xe",
        device="R1",
        query="configure ospf area 0 auth",
    )
    assert output["syntax_validated"] is True
    assert output["risk_level"] == "MEDIUM"
    assert output["requires_confirm"] is False
    assert output["commands"][0] == "router ospf 1"


def test_destructive_is_flagged_and_blocked_without_confirmation() -> None:
    engine = NetOpsCommanderEngine()
    output = engine.run(
        request_id="CFG-2",
        action="generate_config",
        vendor="cisco_ios_xe",
        device="R2",
        query="shutdown interface g0/1",
    )
    assert output["requires_confirm"] is True
    assert output["risk_level"] == "CRITICAL"
    assert output["commands"] == []
    assert output["syntax_validated"] is False
    assert any("multi-stage confirmation" in reason for reason in output["blocked_reasons"])


def test_destructive_can_proceed_when_confirmed() -> None:
    engine = NetOpsCommanderEngine()
    output = engine.run(
        request_id="CFG-3",
        action="generate_config",
        vendor="cisco_ios_xe",
        device="R3",
        query="shutdown interface g0/1",
        confirmed=True,
    )
    assert output["requires_confirm"] is True
    assert output["commands"] == ["interface GigabitEthernet0/1", "shutdown"]
    assert output["syntax_validated"] is True


def test_juniper_rollback_uses_delete() -> None:
    engine = NetOpsCommanderEngine()
    output = engine.run(
        request_id="CFG-4",
        action="generate_config",
        vendor="juniper_junos",
        device="J1",
        query="configure ospf md5",
    )
    assert output["commands"][0].startswith("set protocols ospf")
    assert output["rollback_package"]["commands"][0].startswith("delete protocols ospf")
