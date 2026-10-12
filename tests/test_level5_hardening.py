import unittest
from unittest.mock import Mock, patch

from evaluator import MAX_HTTP_REQUEST_BYTES, MAX_HTTP_RESPONSE_BYTES, capture


def program(body):
    return "jancuk\n" + body + "\nselesai jancuk\n"


class FakeResponse:
    def __init__(self, body, final_url="https://example.com"):
        self.body = body
        self.final_url = final_url
        self.headers = Mock()
        self.headers.get_content_charset.return_value = "utf-8"
        self.read_sizes = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return self.final_url

    def read(self, size=-1):
        self.read_sizes.append(size)
        return self.body[:size]


class Level5HardeningTests(unittest.TestCase):
    def test_get_rejects_non_http_schemes_without_network(self):
        for url in ("file:///etc/passwd", "ftp://example.com/a", "gopher://example.com"):
            with self.subTest(url=url), patch("evaluator.urlopen") as open_url:
                self.assertEqual(capture(program(f'hedeh kepo_internet("{url}")')), "tidak\n")
                open_url.assert_not_called()

    def test_post_rejects_non_http_schemes_without_network(self):
        for url in ("file:///tmp/pusingcuk", "ftp://example.com/upload"):
            with self.subTest(url=url), patch("evaluator.urlopen") as open_url:
                self.assertEqual(capture(program(f'hedeh kirim_api("{url}", "data")')), "tidak\n")
                open_url.assert_not_called()

    def test_redirect_to_localhost_blocked(self):
        response = FakeResponse(b"secret", final_url="http://127.0.0.1/admin")
        with patch("evaluator.urlopen", return_value=response) as open_url:
            output = capture(program('hedeh kepo_internet("https://example.com/redirect")'))
        self.assertEqual(output, "tidak\n")
        open_url.assert_called_once()

    def test_get_reads_only_response_limit_plus_one(self):
        response = FakeResponse(b"x" * (MAX_HTTP_RESPONSE_BYTES + 1))
        with patch("evaluator.urlopen", return_value=response):
            self.assertEqual(capture(program('hedeh kepo_internet("https://example.com")')), "tidak\n")
        self.assertEqual(response.read_sizes, [MAX_HTTP_RESPONSE_BYTES + 1])

    def test_post_rejects_oversized_text_before_network(self):
        oversized = "x" * (MAX_HTTP_REQUEST_BYTES + 1)
        source = 'hedeh kirim_api("https://example.com", "' + oversized + '")'
        with patch("evaluator.urlopen") as open_url:
            self.assertEqual(capture(program(source)), "tidak\n")
            open_url.assert_not_called()

    def test_post_rejects_non_dict_non_text_payload(self):
        with patch("evaluator.urlopen") as open_url:
            self.assertEqual(capture(program('hedeh kirim_api("https://example.com", benar)')), "tidak\n")
            open_url.assert_not_called()

    def test_post_serializes_dictionary_as_json(self):
        response = FakeResponse(b'{"ok":true}')
        with patch("evaluator.urlopen", return_value=response) as open_url:
            output = capture(program('hedeh kirim_api("https://example.com", { "ok": benar })'))
        self.assertEqual(output, '{"ok":true}\n')
        request = open_url.call_args.args[0]
        self.assertEqual(request.data, b'{"ok": true}')
        self.assertEqual(open_url.call_args.kwargs["timeout"], 10)

    def test_warna_uses_actual_escape_byte(self):
        output = capture(program('hedeh warna("merah", "merah")'))
        self.assertEqual(output.encode("utf-8"), b"\x1b[31mmerah\x1b[0m\n")

    def test_return_inside_coba_is_not_caught(self):
        source = program(
            'fungsi ambil()\n'
            'coba\n'
            'balek 42\n'
            'ketangkep err\n'
            'balek 0\n'
            'gitu coba\n'
            'selesai fungsi\n'
            'hedeh ambil()'
        )
        self.assertEqual(capture(source), "42\n")

    def test_valid_json_false_is_distinct_from_parse_failure(self):
        self.assertEqual(capture(program('hedeh jadi_json("false")')), "tidak\n")
        self.assertEqual(capture(program('hedeh jadi_json("not json")')), "None\n")

    def test_jadi_teks_serializes_boolean_and_null_as_json(self):
        self.assertEqual(
            capture(program('hedeh jadi_teks(benar)\nhedeh jadi_teks(jadi_json("null"))')),
            "true\nnull\n",
        )


if __name__ == "__main__":
    unittest.main()
