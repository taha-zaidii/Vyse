"""SMTP email channel — HTML body with severity color, frame snapshot link."""

from __future__ import annotations

from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import structlog

from vyse.core.models import DispatchResult, Incident, Severity

logger = structlog.get_logger(__name__)


class SMTPChannel:
    name = "email"

    def __init__(
        self,
        threshold: Severity = Severity.HIGH,
        host: str = "localhost",
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        sender: str = "vyse@localhost",
        recipients: list[str] | None = None,
        use_tls: bool = True,
    ):
        self.threshold = threshold
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender
        self.recipients = recipients or []
        self.use_tls = use_tls

    def _build_message(self, incident: Incident) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Vyse · {incident.severity.label}] {incident.incident_type}"
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)
        body = (
            f"<p><b>Severity:</b> {incident.severity.label}</p>"
            f"<p><b>Camera:</b> {incident.camera_id} &middot; <b>Zone:</b> {incident.zone}</p>"
            f"<p><b>Rule:</b> {incident.rule_id}</p>"
            f"<p><b>Confidence avg:</b> {incident.confidence_avg:.2f} "
            f"&middot; <b>Triggers:</b> {incident.trigger_event_count}</p>"
            f"<p><a href='{incident.frame_snapshot_path or '#'}'>View snapshot</a></p>"
        )
        msg.attach(MIMEText(body, "html"))
        return msg

    async def dispatch(self, incident: Incident) -> DispatchResult:
        try:
            await aiosmtplib.send(
                self._build_message(incident),
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=self.use_tls,
            )
            status, code, err = "sent", None, None
        except Exception as e:
            status, code, err = "failed", None, str(e)
            logger.exception("smtp_failed", error=err)
        return DispatchResult(
            incident_id=incident.incident_id,
            channel=self.name,
            dispatched_at=datetime.now(UTC),
            status=status,
            response_code=code,
            error_msg=err,
        )

    async def test(self) -> bool:
        try:
            client = aiosmtplib.SMTP(hostname=self.host, port=self.port, use_tls=self.use_tls)
            await client.connect()
            await client.quit()
            return True
        except Exception:
            return False
