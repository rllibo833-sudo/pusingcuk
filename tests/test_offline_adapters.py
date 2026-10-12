import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from compiler.ir import from_source
from library.module_system import ModuleImportError, expand_file
from library.adapters import (
    DatabaseAdapterError, LocalDatabase, LocalHTTPServer, ServerAdapterError,
    MockBlockchain, LocalDevJsonRpc, Web3AdapterError,
)


class ModuleSystemTests(unittest.TestCase):
    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_explicit_import_compiles_with_namespaced_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "lib/angka.pusingcuk", """jancuk
ekspor fungsi tambah
fungsi tambah(a, b)
    balek a + b
selesai fungsi
selesai jancuk
""")
            entry = self.write(root, "main.pusingcuk", """jancuk
pakai "lib/angka.pusingcuk" sebagai angka
hedeh angka.tambah(20, 22)
selesai jancuk
""")
            expanded = expand_file(entry)
            self.assertIn("_pcmod_", expanded)
            self.assertNotIn("pakai ", expanded)
            from_source(expanded, entry.name)

    def test_non_exported_symbol_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "m.pusingcuk", """jancuk
fungsi rahasia()
    balek 1
selesai fungsi
selesai jancuk
""")
            entry = self.write(root, "main.pusingcuk", """jancuk
pakai "m.pusingcuk" sebagai m
hedeh m.rahasia()
selesai jancuk
""")
            with self.assertRaisesRegex(ModuleImportError, "bukan ekspor"):
                expand_file(entry)

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = self.write(root, "main.pusingcuk", """jancuk
pakai "../secret.pusingcuk" sebagai secret
selesai jancuk
""")
            with self.assertRaisesRegex(ModuleImportError, "tidak aman"):
                expand_file(entry)

    def test_cycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "a.pusingcuk", """jancuk
pakai "b.pusingcuk" sebagai b
ekspor fungsi a
fungsi a()
    balek b.b()
selesai fungsi
selesai jancuk
""")
            self.write(root, "b.pusingcuk", """jancuk
pakai "a.pusingcuk" sebagai a
ekspor fungsi b
fungsi b()
    balek a.a()
selesai fungsi
selesai jancuk
""")
            entry = self.write(root, "main.pusingcuk", """jancuk
pakai "a.pusingcuk" sebagai a
selesai jancuk
""")
            with self.assertRaisesRegex(ModuleImportError, "siklus impor"):
                expand_file(entry)

    def test_only_pusingcuk_extension_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "m.py", "print('no')")
            entry = self.write(root, "main.pusingcuk", """jancuk
pakai "m.py" sebagai m
selesai jancuk
""")
            with self.assertRaisesRegex(ModuleImportError, "ekstensi modul"):
                expand_file(entry)


class LocalDatabaseTests(unittest.TestCase):
    def test_parameterized_queries_and_transaction_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            with LocalDatabase(tmp) as db:
                db.execute("CREATE TABLE users (name TEXT)")
                db.execute("INSERT INTO users(name) VALUES (?)", ("Rani",))
                self.assertEqual(db.query("SELECT name FROM users WHERE name = ?", ("Rani",)),
                                 [("Rani",)])
                with self.assertRaisesRegex(ValueError, "rollback"):
                    with db.transaction():
                        db.execute("INSERT INTO users(name) VALUES (?)", ("Budi",))
                        raise ValueError("rollback")
                self.assertEqual(db.query("SELECT name FROM users"), [("Rani",)])

    def test_attach_and_pragma_are_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with LocalDatabase(tmp) as db:
                with self.assertRaises(DatabaseAdapterError):
                    db.execute("ATTACH DATABASE ? AS other", ("outside.sqlite3",))
                with self.assertRaises(DatabaseAdapterError):
                    db.execute("PRAGMA user_version")

    def test_filename_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DatabaseAdapterError):
                LocalDatabase(tmp, "../outside.sqlite3")


class LocalServerTests(unittest.TestCase):
    def test_json_get_and_post_on_loopback(self):
        def hello(_payload, _headers):
            return {"message": "halo"}

        def echo(payload, _headers):
            return {"received": payload}

        with LocalHTTPServer({("GET", "/hello"): hello, ("POST", "/echo"): echo}) as server:
            host, port = server.address
            with urlopen(f"http://{host}:{port}/hello", timeout=2) as response:
                self.assertEqual(json.loads(response.read()), {"message": "halo"})
            request = Request(
                f"http://{host}:{port}/echo",
                data=json.dumps({"n": 7}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=2) as response:
                self.assertEqual(json.loads(response.read()), {"received": {"n": 7}})

    def test_external_bind_is_rejected(self):
        with self.assertRaises(ServerAdapterError):
            LocalHTTPServer(host="0.0.0.0")

    def test_request_body_limit(self):
        with LocalHTTPServer({("POST", "/"): lambda payload, headers: {"ok": True}},
                              max_body_bytes=8) as server:
            host, port = server.address
            request = Request(f"http://{host}:{port}/", data=b'{"long":1}',
                              headers={"Content-Type": "application/json"}, method="POST")
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=2)
            self.assertEqual(caught.exception.code, 413)


class Web3AdapterTests(unittest.TestCase):
    def test_mock_transfer_and_idempotency(self):
        chain = MockBlockchain(initial_balances={"alice": 100, "bob": 0})
        result = chain.transfer("alice", "bob", 25, tx_id="demo-1")
        self.assertEqual(result["chain_id"], 31337)
        self.assertEqual(chain.balance("alice"), 75)
        self.assertEqual(chain.balance("bob"), 25)
        chain.transfer("alice", "bob", 25, tx_id="demo-1")
        self.assertEqual(chain.balance("bob"), 25)
        with self.assertRaises(Web3AdapterError):
            chain.transfer("alice", "carol", 25, tx_id="demo-1")

    def test_external_rpc_is_rejected(self):
        with self.assertRaises(Web3AdapterError):
            LocalDevJsonRpc("http://example.com:8545")

    def test_local_json_rpc_round_trip(self):
        def rpc(payload, _headers):
            return {"jsonrpc": "2.0", "id": payload["id"], "result": "0x539"}

        with LocalHTTPServer({("POST", "/"): rpc}) as server:
            host, port = server.address
            client = LocalDevJsonRpc(f"http://{host}:{port}/")
            self.assertEqual(client.request("eth_chainId"), "0x539")


if __name__ == "__main__":
    unittest.main()
