from __future__ import annotations

from typing import Any, Dict


class MoltPlanner:
    """Produces ActionRequest objects only; it does not execute browser actions."""

    def plan(self, action_type: str, target: str, url: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {
            "action_type": action_type,
            "target": target,
            "url": url,
            "metadata": metadata or {},
        }
