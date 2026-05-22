"""Seed the DB with realistic-looking demo incidents.

Run after the backend is up so the dashboard has something to display:
    python scripts/seed_demo.py
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta, timezone

# Allow running from repo root: `python scripts/seed_demo.py`
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from vyse.core.models import Incident, Severity  # noqa: E402
from vyse.db.session import init_db, session_scope  # noqa: E402
from vyse.db.models import IncidentORM  # noqa: E402


TYPES = [
    ("PPE_NO_HELMET_SUSTAINED", Severity.HIGH),
    ("PPE_NO_VEST_SUSTAINED", Severity.MEDIUM),
    ("DROWSY_OPERATOR", Severity.CRITICAL),
    ("PHONE_IN_MACHINERY", Severity.HIGH),
    ("RESTRICTED_ZONE_BREACH", Severity.HIGH),
]
ZONES = ["machinery", "walkway", "restricted_control_room"]
CAMERAS = ["cam-1", "cam-2"]


async def seed(n: int = 80) -> None:
    await init_db()
    async with session_scope() as session:
        now = datetime.now(timezone.utc)
        for i in range(n):
            t, sev = random.choice(TYPES)
            inc = Incident(
                created_at=now - timedelta(minutes=random.randint(0, 60 * 36)),
                camera_id=random.choice(CAMERAS),
                zone=random.choice(ZONES),
                incident_type=t,
                severity=sev,
                rule_id=t,
                confidence_avg=round(random.uniform(0.6, 0.95), 2),
                trigger_event_count=random.randint(8, 30),
                track_id=random.randint(1, 12),
                metadata={"seed": True},
            )
            session.add(IncidentORM.from_dataclass(inc))
        await session.commit()
    print(f"[ok] inserted {n} demo incidents")


if __name__ == "__main__":
    asyncio.run(seed())
