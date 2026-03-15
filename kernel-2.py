#!/usr/bin/env python3
"""MAGI kernel-2 — B-loop heartbeat + tool executor + HTTP server."""

import json
import os
import sys
import time
import threading
import argparse
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import posixpath

API_URL = "https://lm.hermitcrab.uk/v1/chat/completions"
API_KEY = "sk-lm-bCXVCVv7:xEp0aFlihvp6LSxX6Jll"
MODEL = "mistralai/devstral-small-2-2512"

SHELL_PATH = "shell-2.json"
SEED_PATH = "seed-2.json"
SERVE_DIR = "./serve"
HTTP_PORT = 8080

# File lock for shell-2.json access
_shell_lock = threading.Lock()
_log_file = None


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if _log_file:
        _log_file.write(line + "\n")
        _log_file.flush()


# --- Block I/O ---

def load_block():
    with _shell_lock:
        if not os.path.exists(SHELL_PATH):
            with open(SEED_PATH, "r") as f:
                seed = json.load(f)
            with open(SHELL_PATH, "w") as f:
                json.dump(seed, f, indent=2)
            log(f"Initialised {SHELL_PATH} from {SEED_PATH}")
            return seed
        with open(SHELL_PATH, "r") as f:
            return json.load(f)


def save_block(block):
    with _shell_lock:
        with open(SHELL_PATH, "w") as f:
            json.dump(block, f, indent=2)


def send_block(block, max_tokens=2000, temperature=0.7):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a JSON processor. You receive a JSON object. You return it updated. Return ONLY the JSON object. No markdown, no explanation, no code fences."},
            {"role": "user", "content": json.dumps(block)},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _all_keys(obj):
    """Collect all keys recursively."""
    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(k)
            keys.extend(_all_keys(v))
    return keys


def is_pscale_valid(obj):
    """Recursively check that all keys are _ or digits 1-9."""
    if not isinstance(obj, dict):
        return True
    valid_keys = {"_", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    for key, val in obj.items():
        if key not in valid_keys:
            return False
        if not is_pscale_valid(val):
            return False
    return True


# --- Tool executor ---

def safe_path(filename):
    """Resolve filename within SERVE_DIR. Reject escapes."""
    clean = posixpath.normpath("/" + filename).lstrip("/")
    if not clean or ".." in clean.split("/"):
        return None
    return os.path.join(SERVE_DIR, clean)


def execute_tool(name, args_str):
    """Execute a single tool. Returns (status, result)."""
    try:
        args = json.loads(args_str) if args_str else {}
    except json.JSONDecodeError:
        return "error", f"Invalid JSON args: {args_str}"

    if name == "write_file":
        path = safe_path(args.get("path", ""))
        if path is None:
            return "error", "Invalid path"
        os.makedirs(os.path.dirname(path) or SERVE_DIR, exist_ok=True)
        with open(path, "w") as f:
            f.write(args.get("content", ""))
        return "done", f"written to {path}"

    elif name == "read_file":
        path = safe_path(args.get("path", ""))
        if path is None:
            return "error", "Invalid path"
        if not os.path.exists(path):
            return "error", f"File not found: {path}"
        with open(path, "r") as f:
            content = f.read(2000)
        return "done", content

    elif name == "list_files":
        if not os.path.exists(SERVE_DIR):
            return "done", ""
        files = os.listdir(SERVE_DIR)
        return "done", ", ".join(sorted(files))

    else:
        return "error", f"Unknown tool: {name}"


def execute_pending_tools(block):
    """Scan key 8 for pending tool requests and execute them."""
    tools = block.get("8")
    if not isinstance(tools, dict):
        return

    for key, req in tools.items():
        if key == "_":
            continue
        if not isinstance(req, dict):
            continue
        if req.get("3") != "pending":
            continue

        name = req.get("1", "")
        args_str = req.get("2", "")
        log(f"Tool: {name}({args_str[:80]})")

        try:
            status, result = execute_tool(name, args_str)
        except Exception as e:
            status, result = "error", str(e)

        req["3"] = status
        req["4"] = result
        log(f"  -> {status}: {result[:120]}")


# --- HTTP server ---

class MAGIHandler(SimpleHTTPRequestHandler):
    """Serves ./serve/ as static files, /state as shell-2.json, /input as POST endpoint."""

    def do_GET(self):
        if self.path == "/state":
            self._serve_state()
        else:
            self._serve_static()

    def do_POST(self):
        if self.path == "/input":
            self._handle_input()
        else:
            self.send_error(404)

    def _serve_state(self):
        with _shell_lock:
            if os.path.exists(SHELL_PATH):
                with open(SHELL_PATH, "r") as f:
                    data = f.read()
            else:
                data = "{}"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data.encode())

    def _serve_static(self):
        path = self.path.split("?")[0].split("#")[0]
        if path == "/":
            path = "/index.html"
        filepath = safe_path(path.lstrip("/"))
        if filepath is None or not os.path.isfile(filepath):
            self.send_error(404)
            return
        self.send_response(200)
        if filepath.endswith(".html"):
            ct = "text/html"
        elif filepath.endswith(".css"):
            ct = "text/css"
        elif filepath.endswith(".js"):
            ct = "application/javascript"
        elif filepath.endswith(".json"):
            ct = "application/json"
        else:
            ct = "application/octet-stream"
        self.send_header("Content-Type", ct)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def _handle_input(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            text = data.get("text", "")
        except (json.JSONDecodeError, AttributeError):
            text = body.decode("utf-8", errors="replace")

        # Write user input to key 6 in shell
        with _shell_lock:
            if os.path.exists(SHELL_PATH):
                with open(SHELL_PATH, "r") as f:
                    block = json.load(f)
                block["6"] = text
                with open(SHELL_PATH, "w") as f:
                    json.dump(block, f, indent=2)
                log(f"User input: {text[:120]}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logging


def start_http_server():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), MAGIHandler)
    log(f"HTTP server on port {HTTP_PORT}")
    server.serve_forever()


# --- B-loop ---

def cycle():
    block = load_block()
    try:
        raw = send_block(block)
    except Exception as e:
        log(f"Network error: {e}")
        return

    log(f"Raw ({len(raw)} chars): {raw[:300]}")

    updated = extract_json(raw)
    if updated is None:
        log(f"REJECT: no valid JSON")
        return

    if not is_pscale_valid(updated):
        bad_keys = [k for k in _all_keys(updated) if k not in {"_","1","2","3","4","5","6","7","8","9"}]
        log(f"REJECT: non-pscale keys: {bad_keys[:10]}")
        return

    # Execute any pending tool requests
    execute_pending_tools(updated)

    save_block(updated)

    concern = updated.get("3", "")
    if isinstance(concern, dict):
        summary = concern.get("1", str(concern))[:120]
    else:
        summary = str(concern)[:120]
    log(f"Concern: {summary}")
    log(f"Shell: {json.dumps(updated, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="MAGI kernel-2 — B-loop + tools + HTTP")
    parser.add_argument("--interval", type=int, default=30, help="Sleep seconds between cycles")
    parser.add_argument("--cycles", type=int, default=0, help="Max cycles (0 = unlimited, Ctrl+C to stop)")
    args = parser.parse_args()

    interval = int(os.environ.get("MAGI_INTERVAL", args.interval))
    max_cycles = args.cycles

    # Ensure serve directory exists
    os.makedirs(SERVE_DIR, exist_ok=True)

    # Start HTTP server in background thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    global _log_file
    log_name = f"kernel2-{time.strftime('%Y%m%d-%H%M%S')}.log"
    _log_file = open(log_name, "w")
    log(f"Kernel-2 starting. Interval: {interval}s. Cycles: {max_cycles or 'unlimited'}. Log: {log_name}")

    n = 0
    while max_cycles == 0 or n < max_cycles:
        n += 1
        log(f"--- Cycle {n}{f'/{max_cycles}' if max_cycles else ''} ---")
        cycle()
        if max_cycles and n >= max_cycles:
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
