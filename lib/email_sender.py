"""SMTP email sender (Python stdlib only).

Supports STARTTLS / SSL / plaintext transport. Builds RFC 2046 multipart/alternative
(HTML + plain text) with optional file attachments. Adds RFC 2369 / RFC 8058
List-Unsubscribe headers when configured.
"""

import mimetypes
import smtplib
import ssl
from dataclasses import dataclass, field
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SmtpConfig:
    host: str
    port: int = 587
    user: str = ""
    password: str = ""
    tls: str = "starttls"   # starttls | ssl | none
    timeout: int = 30


@dataclass
class SendResult:
    recipient: str
    status: str   # "sent" | "failed" | "skipped"
    error: str = ""
    message_id: str = ""


class SendError(Exception):
    """Raised on SMTP-level failures. Caller catches and records to manifest."""
    def __init__(self, recipient: str, reason: str):
        super().__init__(f"send to {recipient} failed: {reason}")
        self.recipient = recipient
        self.reason = reason


def _build_message(
    from_addr: str,
    to_addr: str,
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: str = "",
    extra_headers: Optional[Dict[str, str]] = None,
    attachments: Optional[List[Path]] = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="morning-ai")
    if reply_to:
        msg["Reply-To"] = reply_to

    for k, v in (extra_headers or {}).items():
        if v:
            msg[k] = v

    # multipart/alternative: text first, then HTML (preferred when both present)
    msg.set_content(text_body, subtype="plain", charset="utf-8")
    msg.add_alternative(html_body, subtype="html")

    for path in attachments or []:
        if not path.exists() or not path.is_file():
            continue
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=path.name)

    return msg


def _open_smtp(cfg: SmtpConfig) -> smtplib.SMTP:
    """Open and authenticate an SMTP connection per cfg.tls mode."""
    tls = (cfg.tls or "starttls").lower()
    context = ssl.create_default_context()

    if tls == "ssl":
        client = smtplib.SMTP_SSL(cfg.host, cfg.port, timeout=cfg.timeout, context=context)
    else:
        client = smtplib.SMTP(cfg.host, cfg.port, timeout=cfg.timeout)
        client.ehlo()
        if tls == "starttls":
            client.starttls(context=context)
            client.ehlo()
        # tls == "none": no encryption negotiated

    if cfg.user and cfg.password:
        client.login(cfg.user, cfg.password)
    return client


def send(
    smtp_config: SmtpConfig,
    from_addr: str,
    to_addr: str,
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: str = "",
    extra_headers: Optional[Dict[str, str]] = None,
    attachments: Optional[List[Path]] = None,
) -> SendResult:
    """Send a single email. Returns SendResult; raises SendError on failure.

    Caller should iterate recipients and rate-limit between sends.
    """
    msg = _build_message(
        from_addr=from_addr,
        to_addr=to_addr,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        reply_to=reply_to,
        extra_headers=extra_headers,
        attachments=attachments,
    )

    try:
        client = _open_smtp(smtp_config)
    except (smtplib.SMTPException, OSError, ssl.SSLError) as e:
        raise SendError(to_addr, f"connection error: {e}")

    try:
        client.send_message(msg)
    except smtplib.SMTPException as e:
        try:
            client.quit()
        except smtplib.SMTPException:
            pass
        raise SendError(to_addr, f"smtp error: {e}")
    finally:
        try:
            client.quit()
        except smtplib.SMTPException:
            pass

    return SendResult(
        recipient=to_addr,
        status="sent",
        message_id=msg["Message-ID"] or "",
    )


def build_unsubscribe_headers(unsubscribe: str) -> Dict[str, str]:
    """Build List-Unsubscribe headers from an unsubscribe target.

    Supports mailto: and https:// targets. RFC 8058 one-click is added when an
    https URL is present (mainstream clients show a one-tap unsubscribe button).
    Returns {} when unsubscribe is empty.
    """
    if not unsubscribe:
        return {}
    target = unsubscribe.strip()
    if not (target.startswith("mailto:") or target.startswith("http://") or target.startswith("https://")):
        # Treat bare "user@host" as mailto:
        target = f"mailto:{target}"
    headers = {"List-Unsubscribe": f"<{target}>"}
    if target.startswith("https://"):
        headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    return headers
