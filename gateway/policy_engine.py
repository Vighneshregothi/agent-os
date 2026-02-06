from __future__ import annotations

import fnmatch
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Decision:
    decision: str
    policy_id: str
    reason: str


class PolicyEngine:
    def __init__(self, policy_path: str):
        self.policy_path = Path(policy_path)
        self._policy_doc = self._load_policy_file(self.policy_path)
        self.policy_hash = self._hash_file(self.policy_path)

    @staticmethod
    def _hash_file(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _load_policy_file(path: Path) -> Dict[str, Any]:
        raw = path.read_text(encoding="utf-8")
        try:
            import yaml  # type: ignore

            doc = yaml.safe_load(raw)
        except ModuleNotFoundError:
            # YAML is a superset of JSON; this keeps v0 dependency-free.
            doc = json.loads(raw)
        if not isinstance(doc, dict):
            raise ValueError("policy file root must be an object")
        doc.setdefault("version", 1)
        doc.setdefault("rules", [])
        if not isinstance(doc["rules"], list):
            raise ValueError("policy.rules must be a list")
        return doc

    def evaluate(self, action: Dict[str, Any]) -> Decision:
        for rule in self._policy_doc["rules"]:
            if self._matches(rule, action):
                return Decision(
                    decision=rule["effect"],
                    policy_id=rule.get("policy_id", "unnamed_rule"),
                    reason=rule.get("reason", "Policy decision"),
                )

        return Decision(
            decision="DENY",
            policy_id="default_deny",
            reason="No policy rule matched",
        )

    @staticmethod
    def _matches(rule: Dict[str, Any], action: Dict[str, Any]) -> bool:
        rule_action_type = rule.get("action_type", "*")
        if rule_action_type != "*" and rule_action_type != action.get("action_type"):
            return False

        url_pattern = rule.get("url_pattern", "*")
        return fnmatch.fnmatch(action.get("url", ""), url_pattern)
