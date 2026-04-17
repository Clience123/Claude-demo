import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import error, request


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-1")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class ClaudeOpusHandler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/claude/opus/chat":
            self._send_json(404, {"error": "not_found"})
            return

        if not API_KEY:
            self._send_json(500, {"error": "ANTHROPIC_API_KEY is required"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            self._send_json(400, {"error": "request body is required"})
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
            messages = payload["messages"]
            max_tokens = int(payload.get("max_tokens", 1024))
            temperature = float(payload.get("temperature", 0.7))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid request payload"})
            return

        upstream_payload = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        upstream_body = json.dumps(upstream_payload).encode("utf-8")
        upstream_request = request.Request(
            ANTHROPIC_URL,
            data=upstream_body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        try:
            with request.urlopen(upstream_request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                self._send_json(200, result)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self._send_json(exc.code, {"error": "upstream_http_error", "detail": detail})
        except error.URLError as exc:
            self._send_json(502, {"error": "upstream_connection_error", "detail": str(exc.reason)})


def main() -> None:
    server = HTTPServer((HOST, PORT), ClaudeOpusHandler)
    print(f"Claude Opus service running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
