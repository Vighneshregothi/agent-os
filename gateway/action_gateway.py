from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse, urlunparse

from audit.logger import AuditLogger
from gateway.executor import BrowserExecutor, ExecutionTicket
from gateway.policy_engine import PolicyEngine


class GatewayError(Exception):
    pass


class AuditWriteError(GatewayError):
    pass


class ActionGateway:
    def __init__(
        self,
        policy_engine: PolicyEngine,
        executor: BrowserExecutor,
        audit_logger: AuditLogger,
        schema_path: str,
    ):
        self.policy_engine = policy_engine
        self.executor = executor
        self.audit_logger = audit_logger
        self.schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))

    def handle(self, agent_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_action(action)
        action = dict(action)
        action["url"] = self._normalize_url(action["url"])

        decision = self.policy_engine.evaluate(action)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "agent_id": agent_id,
            "action": action,
            "decision": {
                "decision": decision.decision,
                "policy_id": decision.policy_id,
                "reason": decision.reason,
            },
            "execution_result": None,
            "policy_hash": self.policy_engine.policy_hash,
        }

        if decision.decision == "ALLOW":
            ticket = ExecutionTicket(secrets.token_hex(16))
            try:
                event["execution_result"] = self.executor.execute(action, ticket)
            except Exception as exc:  # execution errors are auditable failures
                event["execution_result"] = {"status": "ERROR", "error": str(exc)}

        try:
            self.audit_logger.append(event)
        except Exception as exc:
            raise AuditWriteError("Audit write failed; action must fail") from exc

        if decision.decision == "DENY":
            return {"status": "DENIED", "decision": event["decision"]}

        result = event["execution_result"]
        if isinstance(result, dict) and result.get("status") == "ERROR":
            return {"status": "ERROR", "decision": event["decision"], "result": result}

        return {"status": "OK", "decision": event["decision"], "result": result}

    def _validate_action(self, action: Dict[str, Any]) -> None:
        required = self.schema.get("required", [])
        for field in required:
            if field not in action:
                raise GatewayError(f"Malformed action: missing field '{field}'")

        allowed_types = self.schema["properties"]["action_type"]["enum"]
        if action["action_type"] not in allowed_types:
            raise GatewayError(f"Unknown action type: {action['action_type']}")

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise GatewayError("Malformed action: url must use http/https")
        if not parsed.netloc:
            raise GatewayError("Malformed action: url missing host")
        normalized = parsed._replace(fragment="")
        return urlunparse(normalized)
