from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ExecutionTicket:
    value: str


class BrowserExecutor:
    def __init__(self, driver: Any):
        self.driver = driver

    def execute(self, action: Dict[str, Any], ticket: ExecutionTicket) -> Dict[str, Any]:
        if not isinstance(ticket, ExecutionTicket):
            raise RuntimeError("Bypass detected: execution requires gateway-issued ticket")

        action_type = action["action_type"]
        if action_type == "NAVIGATE":
            return self.driver.navigate(action["url"])
        if action_type == "CLICK":
            return self.driver.click(action["target"]) 
        if action_type == "TYPE":
            return self.driver.type(action["target"], action.get("metadata", {}).get("text", ""))
        if action_type == "SUBMIT":
            return self.driver.submit(action["target"])
        if action_type == "DOWNLOAD":
            return self.driver.download(action["url"])
        raise ValueError(f"Unsupported action type: {action_type}")
