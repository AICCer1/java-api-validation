#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

PORT = int(os.getenv("MOCK_API_PORT", "18080"))
TOKEN = os.getenv("MOCK_API_TOKEN", "demo-token")

USERS = {
    1: {
        "id": 1,
        "name": "Alice Skill Demo",
        "email": "alice.skill.demo@example.com",
        "phone": "+8613800000000"
    }
}
NEXT_ID = 2


def json_bytes(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "JavaApiValidationMock/1.0"

    def log_message(self, fmt, *args):
        return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def _send(self, status, payload, headers=None):
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _is_authorized(self):
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {TOKEN}"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/actuator/health":
            return self._send(200, {"status": "UP"})

        if path == "/api/users":
            if not self._is_authorized():
                return self._send(401, {"error": "unauthorized"})
            query = parse_qs(parsed.query)
            page = query.get("page", ["1"])[0]
            size = query.get("size", ["10"])[0]
            return self._send(200, {
                "page": int(page),
                "size": int(size),
                "total": len(USERS),
                "records": list(USERS.values())
            })

        if path.startswith("/api/users/"):
            if not self._is_authorized():
                return self._send(401, {"error": "unauthorized"})
            try:
                user_id = int(path.rsplit("/", 1)[-1])
            except ValueError:
                return self._send(400, {"error": "invalid user id"})
            user = USERS.get(user_id)
            if not user:
                return self._send(404, {"error": "user not found"})
            return self._send(200, user)

        if path == "/api/admin/users":
            if not self._is_authorized():
                return self._send(403, {"error": "forbidden"})
            return self._send(200, {
                "total": len(USERS),
                "records": list(USERS.values())
            })

        return self._send(404, {"error": "not found"})

    def do_POST(self):
        global NEXT_ID
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/users":
            if not self._is_authorized():
                return self._send(401, {"error": "unauthorized"})
            payload = self._read_json() or {}
            user = {
                "id": NEXT_ID,
                "name": payload.get("name", f"User-{NEXT_ID}"),
                "email": payload.get("email", f"user{NEXT_ID}@example.com"),
                "phone": payload.get("phone", "")
            }
            USERS[NEXT_ID] = user
            NEXT_ID += 1
            return self._send(201, user, headers={"Location": f"/api/users/{user['id']}"})

        return self._send(404, {"error": "not found"})


if __name__ == "__main__":
    print(f"Mock API listening on http://127.0.0.1:{PORT} (token: {TOKEN})")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
