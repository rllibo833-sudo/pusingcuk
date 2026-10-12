"""DNS-resolution and IPv6 SSRF regression tests."""
import socket
import unittest
from unittest.mock import patch

from evaluator import _is_blocked_hostname, _valid_http_url


def addrinfo(address):
    family = socket.AF_INET6 if ":" in address else socket.AF_INET
    return [(family, socket.SOCK_STREAM, 6, "", (address, 0, 0, 0) if family == socket.AF_INET6 else (address, 0))]


class DnsRebindingTests(unittest.TestCase):
    def test_hostname_resolving_to_private_ipv4_is_blocked(self):
        with patch("evaluator.socket.gethostbyname", return_value="192.168.1.20"), \
             patch("evaluator.socket.getaddrinfo", return_value=addrinfo("192.168.1.20")):
            self.assertFalse(_valid_http_url("https://attacker.example/data"))

    def test_hostname_resolving_to_loopback_is_blocked(self):
        with patch("evaluator.socket.gethostbyname", return_value="127.0.0.1"), \
             patch("evaluator.socket.getaddrinfo", return_value=addrinfo("127.0.0.1")):
            self.assertTrue(_is_blocked_hostname("rebind.example"))

    def test_hostname_resolving_to_ipv6_ula_is_blocked(self):
        with patch("evaluator.socket.gethostbyname", return_value="93.184.216.34"), \
             patch("evaluator.socket.getaddrinfo", return_value=addrinfo("fd12:3456::1")):
            self.assertFalse(_valid_http_url("https://attacker.example/data"))

    def test_literal_ipv6_ula_and_link_local_are_blocked(self):
        for host in ("fc00::1", "fd12:3456::1", "fe80::1"):
            with self.subTest(host=host):
                self.assertTrue(_is_blocked_hostname(host))

    def test_dns_failure_fails_closed(self):
        with patch("evaluator.socket.gethostbyname", side_effect=socket.gaierror), \
             patch("evaluator.socket.getaddrinfo", side_effect=socket.gaierror):
            self.assertTrue(_is_blocked_hostname("unresolvable.example"))

    def test_public_dns_answers_are_allowed(self):
        with patch("evaluator.socket.gethostbyname", return_value="93.184.216.34"), \
             patch("evaluator.socket.getaddrinfo", return_value=addrinfo("93.184.216.34")):
            self.assertFalse(_is_blocked_hostname("public.example"))


if __name__ == "__main__":
    unittest.main()
