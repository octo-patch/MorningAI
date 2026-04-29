import sys
from typing import Optional


def log(tag: str, msg: str, *, tty_only: bool = False) -> None:
    if tty_only and not sys.stderr.isatty():
        return
    sys.stderr.write(f"[{tag}] {msg}\n")
    sys.stderr.flush()


def parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if len(date_str) >= 10:
        return date_str[:10]
    return None
