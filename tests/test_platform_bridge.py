import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cuk_platform_bridge", ROOT / "apps/accounting/platform_bridge.py")
BRIDGE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BRIDGE
SPEC.loader.exec_module(BRIDGE)

def request(operation="db.query_accounts", payload=None):
    return {"contract_version": BRIDGE.CONTRACT_VERSION, "request_id": "test-1", "operation": operation, "input": payload or {}}

class PlatformBridgeTests(unittest.TestCase):
    def test_dispatches_registered_capability(self):
        bridge = BRIDGE.PlatformBridge({"db.query_accounts": lambda data: {"accounts": []}})
        response = bridge.dispatch(request())
        self.assertEqual(response["status"], "succeeded")
        self.assertEqual(response["result"], {"accounts": []})

    def test_missing_capability_fails_closed(self):
        response = BRIDGE.PlatformBridge({}).dispatch(request())
        self.assertEqual(response["status"], "denied")
        self.assertEqual(response["diagnostic"]["code"], "CAPABILITY_UNAVAILABLE")

    def test_rejects_unknown_operation_and_contract(self):
        with self.assertRaises(BRIDGE.BridgeError) as caught:
            BRIDGE.validate_envelope(request("db.raw_sql"))
        self.assertEqual(caught.exception.code, "OPERATION_DENIED")
        bad = request(); bad["contract_version"] = "old"
        with self.assertRaises(BRIDGE.BridgeError): BRIDGE.validate_envelope(bad)

    def test_rejects_extra_fields(self):
        bad = request(); bad["sql"] = "DROP TABLE journals"
        with self.assertRaises(BRIDGE.BridgeError): BRIDGE.validate_envelope(bad)

    def test_no_raw_secure_store_key_capability(self):
        self.assertIn("secure_store.get_key_metadata", BRIDGE.ALLOWED_OPERATIONS)
        self.assertNotIn("secure_store.get_key", BRIDGE.ALLOWED_OPERATIONS)

if __name__ == "__main__": unittest.main()
