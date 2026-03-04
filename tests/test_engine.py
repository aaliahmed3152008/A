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
    assert output["risk_level"] == "LOW"
    assert output["requires_confirm"] is False
    assert output["commands"][0] == "router ospf 1"


def test_destructive_is_flagged() -> None:
    engine = NetOpsCommanderEngine()
    blocked = engine._detect_destructive(["shutdown", "interface Gi0/1"])
    assert blocked
