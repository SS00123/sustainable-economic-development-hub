"""Backward-compatible shim.

The canonical module is now `analytics_hub_platform.domain.kpis.indicators`.
This file remains to avoid breaking older imports.
"""

from __future__ import annotations

from analytics_hub_platform.domain.kpis.indicators import *  # noqa: F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]  # type: ignore
