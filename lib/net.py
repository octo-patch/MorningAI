"""Network helpers — IPv4-only DNS fallback for broken-IPv6 environments.

Some hosts have a working IPv4 path but resolve AAAA records that route to a
black hole (the kernel reports `OSError(errno=101, ENETUNREACH)` once it tries
to connect). The Python stdlib happily prefers the IPv6 record returned by
`socket.getaddrinfo`, so any blocking I/O fails before we get a chance to fall
back to IPv4.

This module exposes:

- `is_ipv6_unreachable(exc)` — recognise that error class
- `force_ipv4_only()` — context manager that monkey-patches
  `socket.getaddrinfo` to return only AF_INET addresses, restored on exit

Typical usage::

    try:
        do_network_call()
    except OSError as e:
        if not is_ipv6_unreachable(e):
            raise
        with force_ipv4_only():
            do_network_call()
"""

import socket
from contextlib import contextmanager
from typing import Iterator


def is_ipv6_unreachable(exc: BaseException) -> bool:
    """True if exc is an OSError with errno 101 (ENETUNREACH).

    Also unwraps `urllib.error.URLError`, whose `.reason` attribute carries the
    underlying `OSError` for connection failures.
    """
    if isinstance(exc, OSError) and getattr(exc, "errno", None) == 101:
        return True
    reason = getattr(exc, "reason", None)
    if isinstance(reason, OSError) and getattr(reason, "errno", None) == 101:
        return True
    return False


@contextmanager
def force_ipv4_only() -> Iterator[None]:
    """Monkey-patch `socket.getaddrinfo` to return only AF_INET (IPv4) entries.

    Restored on exit. Not thread-safe — but neither is the underlying problem,
    and the collectors that need this are short-lived per-source futures.
    """
    original = socket.getaddrinfo

    def _v4_only(host, port, family=0, *args, **kwargs):
        return original(host, port, socket.AF_INET, *args, **kwargs)

    socket.getaddrinfo = _v4_only
    try:
        yield
    finally:
        socket.getaddrinfo = original
