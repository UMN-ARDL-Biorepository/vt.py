"""
vt package initialization.

This module applies a minimal, safe shim to avoid runtime DeprecationWarnings
from third-party libraries that call `asyncio.iscoroutinefunction` (deprecated
in Python 3.14). We forward that name to `inspect.iscoroutinefunction` so
upstream packages keep working without warnings.

The shim is conservative and only replaces the attribute if it exists and
differs from `inspect.iscoroutinefunction`.
"""

import asyncio
import inspect

try:
    if (
        hasattr(asyncio, "iscoroutinefunction")
        and asyncio.iscoroutinefunction is not inspect.iscoroutinefunction
    ):
        asyncio.iscoroutinefunction = inspect.iscoroutinefunction
except Exception:
    # If anything goes wrong, don't prevent package import.
    pass

__all__ = []
