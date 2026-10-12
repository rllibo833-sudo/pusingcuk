"""Offline blockchain contract: deterministic mock and loopback-only JSON-RPC."""
from __future__ import annotations

import ipaddress
import json
from urllib.error import URLError, HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler


class Web3AdapterError(RuntimeError):
    """Blockchain adapter policy or protocol failure."""


class MockBlockchain:
    """In-memory test double; it does not create keys or submit real transactions."""

    def __init__(self, *, chain_id=31337, initial_balances=None):
        if not isinstance(chain_id, int) or isinstance(chain_id, bool) or chain_id <= 0:
            raise Web3AdapterError("chain_id harus bilangan bulat positif")
        self.chain_id = chain_id
        self.balances = {}
        for address, amount in (initial_balances or {}).items():
            self._check_address(address)
            self._check_amount(amount, allow_zero=True)
            self.balances[address] = amount
        self.transactions = {}

    @staticmethod
    def _check_address(address):
        if not isinstance(address, str) or not address or len(address) > 128:
            raise Web3AdapterError("alamat mock tidak valid")

    @staticmethod
    def _check_amount(amount, *, allow_zero=False):
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise Web3AdapterError("jumlah harus bilangan bulat")
        if amount < 0 or (amount == 0 and not allow_zero):
            raise Web3AdapterError("jumlah harus positif")

    def balance(self, address):
        self._check_address(address)
        return self.balances.get(address, 0)

    def transfer(self, sender, recipient, amount, *, tx_id=None):
        self._check_address(sender)
        self._check_address(recipient)
        self._check_amount(amount)
        if sender == recipient:
            raise Web3AdapterError("pengirim dan penerima harus berbeda")
        fingerprint = (sender, recipient, amount)
        if tx_id is not None:
            if not isinstance(tx_id, str) or not tx_id or len(tx_id) > 128:
                raise Web3AdapterError("tx_id tidak valid")
            if tx_id in self.transactions:
                prior = self.transactions[tx_id]
                if prior["fingerprint"] != fingerprint:
                    raise Web3AdapterError("tx_id sudah dipakai untuk transfer berbeda")
                return dict(prior["result"])
        if self.balance(sender) < amount:
            raise Web3AdapterError("saldo tidak cukup")
        self.balances[sender] = self.balance(sender) - amount
        self.balances[recipient] = self.balance(recipient) + amount
        result = {"chain_id": self.chain_id, "from": sender, "to": recipient, "amount": amount}
        if tx_id is not None:
            self.transactions[tx_id] = {"fingerprint": fingerprint, "result": dict(result)}
        return result


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class LocalDevJsonRpc:
    """Small JSON-RPC client restricted to a literal loopback HTTP endpoint."""

    def __init__(self, endpoint="http://127.0.0.1:8545", *, timeout=2.0,
                 max_response_bytes=1_048_576):
        parsed = urlsplit(endpoint)
        if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
            raise Web3AdapterError("endpoint harus HTTP loopback tanpa kredensial")
        try:
            if not ipaddress.ip_address(parsed.hostname).is_loopback:
                raise Web3AdapterError("RPC hanya boleh menuju IP loopback")
        except ValueError as exc:
            raise Web3AdapterError("RPC harus memakai IP loopback literal") from exc
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 10:
            raise Web3AdapterError("timeout harus di atas 0 hingga 10 detik")
        if not isinstance(max_response_bytes, int) or not 1 <= max_response_bytes <= 8_388_608:
            raise Web3AdapterError("batas respons harus antara 1 byte dan 8 MiB")
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes
        self._next_id = 1
        # Ignore proxy environment variables and refuse redirects to external hosts.
        self._opener = build_opener(ProxyHandler({}), _NoRedirect)

    def request(self, method, params=None):
        if not isinstance(method, str) or not method or len(method) > 128:
            raise Web3AdapterError("nama metode RPC tidak valid")
        if params is None:
            params = []
        if not isinstance(params, (list, dict)):
            raise Web3AdapterError("params RPC harus berupa list atau object")
        request_id = self._next_id
        self._next_id += 1
        payload = json.dumps({
            "jsonrpc": "2.0", "id": request_id, "method": method, "params": params,
        }, allow_nan=False).encode("utf-8")
        request = Request(self.endpoint, data=payload, headers={
            "Content-Type": "application/json", "Accept": "application/json",
        }, method="POST")
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                raw = response.read(self.max_response_bytes + 1)
            if len(raw) > self.max_response_bytes:
                raise Web3AdapterError("respons RPC melewati batas ukuran")
            document = json.loads(raw.decode("utf-8"))
        except Web3AdapterError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError,
                json.JSONDecodeError, ValueError) as exc:
            raise Web3AdapterError(f"RPC pengembangan lokal gagal: {type(exc).__name__}") from exc
        if not isinstance(document, dict) or document.get("jsonrpc") != "2.0":
            raise Web3AdapterError("respons JSON-RPC tidak valid")
        if document.get("id") != request_id:
            raise Web3AdapterError("ID respons JSON-RPC tidak cocok")
        if "error" in document:
            raise Web3AdapterError("node RPC mengembalikan error")
        if "result" not in document:
            raise Web3AdapterError("respons JSON-RPC tidak memiliki result")
        return document["result"]
