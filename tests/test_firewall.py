import json
import tempfile
import unittest
from pathlib import Path

from audit.logger import AuditLogger
from gateway.action_gateway import ActionGateway, AuditWriteError, GatewayError
from gateway.executor import BrowserExecutor
from gateway.policy_engine import PolicyEngine


class FakeDriver:
    def __init__(self):
        self.calls = []

    def navigate(self, url):
        self.calls.append(("navigate", url))
        return {"status": "OK", "op": "navigate", "url": url}

    def click(self, target):
        self.calls.append(("click", target))
        return {"status": "OK", "op": "click", "target": target}

    def type(self, target, text):
        self.calls.append(("type", target, text))
        return {"status": "OK", "op": "type"}

    def submit(self, target):
        self.calls.append(("submit", target))
        return {"status": "OK", "op": "submit"}

    def download(self, url):
        self.calls.append(("download", url))
        return {"status": "OK", "op": "download"}


class FailingAuditLogger:
    def append(self, event):
        raise OSError("disk full")


class FirewallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.schema = Path("schemas/action.schema.json")

        self.policy_path = self.tmp_path / "policy.yaml"
        self.policy_path.write_text(Path("policies/default.yaml").read_text(encoding="utf-8"), encoding="utf-8")

        self.log_path = self.tmp_path / "audit.jsonl"

        self.driver = FakeDriver()
        self.gateway = ActionGateway(
            policy_engine=PolicyEngine(str(self.policy_path)),
            executor=BrowserExecutor(self.driver),
            audit_logger=AuditLogger(str(self.log_path)),
            schema_path=str(self.schema),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_login_submit_is_blocked(self):
        result = self.gateway.handle(
            agent_id="molt-001",
            action={"action_type": "SUBMIT", "target": "#login", "url": "https://site.com/login"},
        )
        self.assertEqual("DENIED", result["status"])
        self.assertEqual([], self.driver.calls)

    def test_unknown_action_type_is_rejected(self):
        with self.assertRaises(GatewayError):
            self.gateway.handle(
                agent_id="molt-001",
                action={"action_type": "HACK", "target": "#x", "url": "https://site.com"},
            )

    def test_bypass_gateway_crashes(self):
        executor = BrowserExecutor(self.driver)
        with self.assertRaises(RuntimeError):
            executor.execute(
                {"action_type": "CLICK", "target": "#btn", "url": "https://site.com"},
                ticket="not-a-ticket",
            )

    def test_policy_hash_changes_on_file_modification(self):
        first = PolicyEngine(str(self.policy_path)).policy_hash
        changed = json.loads(self.policy_path.read_text(encoding="utf-8"))
        changed["rules"][0]["reason"] = "Changed reason"
        self.policy_path.write_text(json.dumps(changed, indent=2), encoding="utf-8")
        second = PolicyEngine(str(self.policy_path)).policy_hash
        self.assertNotEqual(first, second)

    def test_audit_write_failure_denies_action(self):
        failing_gateway = ActionGateway(
            policy_engine=PolicyEngine(str(self.policy_path)),
            executor=BrowserExecutor(self.driver),
            audit_logger=FailingAuditLogger(),
            schema_path=str(self.schema),
        )
        with self.assertRaises(AuditWriteError):
            failing_gateway.handle(
                agent_id="molt-001",
                action={"action_type": "CLICK", "target": "#ok", "url": "https://site.com"},
            )


if __name__ == "__main__":
    unittest.main()
