"""Recipient list loading for email subscription.

Sources (priority: file overrides env when both exist):
1. EMAIL_RECIPIENTS env var — comma-separated emails (simple case)
2. EMAIL_RECIPIENTS_FILE JSON file — list of objects with per-recipient overrides

JSON file format (default path: .claude/recipients.json):
[
  {"email": "alice@example.com", "name": "Alice", "lang": "zh", "min_score": 6, "active": true},
  {"email": "bob@example.com"}
]

Fields beyond `email` are optional and fall back to global EMAIL_* config.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Recipient:
    """A single email recipient with optional per-recipient overrides."""
    email: str
    name: str = ""
    lang: Optional[str] = None  # zh | en | ja, None = use global EMAIL_LANG
    min_score: Optional[float] = None  # None = use global EMAIL_MIN_SCORE
    active: bool = True

    def display(self) -> str:
        """Return RFC 5322 display form: 'Name <email>' or just 'email'."""
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email

    def to_dict(self) -> Dict[str, Any]:
        d = {"email": self.email, "active": self.active}
        if self.name:
            d["name"] = self.name
        if self.lang:
            d["lang"] = self.lang
        if self.min_score is not None:
            d["min_score"] = self.min_score
        return d


def _is_valid_email(addr: str) -> bool:
    return bool(EMAIL_RE.match(addr.strip()))


def _parse_env_list(raw: str) -> List[Recipient]:
    """Parse comma-separated email list. Skips invalid entries silently."""
    out = []
    for part in raw.split(","):
        addr = part.strip()
        if addr and _is_valid_email(addr):
            out.append(Recipient(email=addr))
    return out


def _parse_json_file(path: Path) -> List[Recipient]:
    """Parse JSON file. Returns empty list if file missing or malformed."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        email = str(entry.get("email", "")).strip()
        if not email or not _is_valid_email(email):
            continue
        out.append(Recipient(
            email=email,
            name=str(entry.get("name", "")),
            lang=entry.get("lang"),
            min_score=entry.get("min_score"),
            active=bool(entry.get("active", True)),
        ))
    return out


def load_recipients(config: Dict[str, Any]) -> List[Recipient]:
    """Load recipient list from config.

    Resolution order:
    - If EMAIL_RECIPIENTS_FILE points to an existing JSON file, use it (overrides env).
    - Otherwise fall back to EMAIL_RECIPIENTS env list.
    - Returns only `active=True` recipients. Duplicate emails are de-duped (first wins).
    """
    file_path = config.get("EMAIL_RECIPIENTS_FILE", ".claude/recipients.json")
    file_recipients = _parse_json_file(Path(file_path)) if file_path else []

    if file_recipients:
        recipients = file_recipients
    else:
        recipients = _parse_env_list(config.get("EMAIL_RECIPIENTS", ""))

    # Filter inactive + dedupe by email (case-insensitive)
    seen = set()
    out = []
    for r in recipients:
        if not r.active:
            continue
        key = r.email.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
