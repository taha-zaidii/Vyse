"""Phase-0 DoD: `import vyse` succeeds."""

from __future__ import annotations


def test_package_imports():
    import vyse

    assert vyse.__version__ == "0.1.0"


def test_agents_importable():
    from vyse.agents.alert_agent import AlertAgent  # noqa: F401
    from vyse.agents.analytics_agent import AnalyticsAgent  # noqa: F401
    from vyse.agents.risk_agent import RiskAgent  # noqa: F401
    from vyse.agents.vision_agent import VisionAgent  # noqa: F401
