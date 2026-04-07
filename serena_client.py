import subprocess
import json
import os
import threading
import time
import uuid
import shutil
import sys

# -------------------------
# Serena command resolver
# -------------------------
def get_serena_command():
    serena_cmd = os.environ.get("SERENA_FZF_SERENA_CMD", "serena")

    if shutil.which(serena_cmd):
        return [serena_cmd, "start-mcp-server"]

    print("⚠ Serena não encontrada, tentando via uvx...\n")

    if not shutil.which("uvx"):
        print("❌ 'uvx' não encontrado.")
        print("👉 Instale o uv: https://github.com/astral-sh/uv")
        sys.exit(1)

    return [
        "uvx",
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server"
    ]

# -------------------------
# MCP Client
# -------------------------
class MCPClient:
    def __init__(self, command):
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.responses = {}
        self._start_reader()

    def _start_reader(self):
        def read():
            for line in self.proc.stdout:
                try:
                    msg = json.loads(line.strip())
                    if "id" in msg:
                        self.responses[msg["id"]] = msg
                except:
                    pass
        threading.Thread(target=read, daemon=True).start()

    def notify(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def call(self, method, params=None, timeout=None):
        req_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }

        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

        if timeout is None:
            timeout = int(os.environ.get("SERENA_FZF_RPC_TIMEOUT", "5"))

        deadline = time.monotonic() + timeout if timeout else None

        while req_id not in self.responses:
            if deadline and time.monotonic() > deadline:
                raise TimeoutError(f"RPC call '{method}' timed out after {timeout}s")
            time.sleep(0.01)

        return self.responses.pop(req_id)