"""Email delivery service supporting Resend and SMTP."""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_summary_email(recipient: str, summary: str) -> None:
    """Send the executive summary to the recipient email."""
    settings = get_settings()

    if settings.EMAIL_PROVIDER == "resend":
        await _send_via_resend(recipient, summary)
    elif settings.EMAIL_PROVIDER == "smtp":
        await asyncio.to_thread(_send_via_smtp, recipient, summary)
    else:
        raise ValueError(f"Unsupported email provider: {settings.EMAIL_PROVIDER}")

    logger.info("Email sent to %s via %s", recipient, settings.EMAIL_PROVIDER)


async def _send_via_resend(recipient: str, summary: str) -> None:
    """Send email via Resend API."""
    settings = get_settings()

    if not settings.RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY is not configured.")

    html_body = _markdown_to_html(summary)

    payload = {
        "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
        "to": [recipient],
        "subject": "Your AI-Generated Sales Executive Summary",
        "html": html_body,
        "text": summary,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.status_code >= 400:
            logger.error(
                "Resend API error %d: %s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

    logger.info("Resend API response: %s", response.json())


def _send_via_smtp(recipient: str, summary: str) -> None:
    """Send email via SMTP."""
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AI-Generated Sales Executive Summary"
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    msg["To"] = recipient

    msg.attach(MIMEText(summary, "plain"))
    msg.attach(MIMEText(_markdown_to_html(summary), "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [recipient], msg.as_string())


def _markdown_to_html(text: str) -> str:
    """Simple markdown-like text to HTML conversion for email."""
    import re

    lines = text.split("\n")
    html_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_lines.append("<br>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{_escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{_escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{_escape(stripped[2:])}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_lines.append(f"<li>{_escape(stripped[2:])}</li>")
        else:
            html_lines.append(f"<p>{_escape(stripped)}</p>")

    body = "\n".join(html_lines)
    # Bold: **text**
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)

    return f"""<!DOCTYPE html>
<html>
<head><style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; padding: 24px; line-height: 1.6; }}
  h1, h2, h3 {{ color: #16213e; }}
  li {{ margin-bottom: 4px; }}
</style></head>
<body>{body}</body>
</html>"""


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
