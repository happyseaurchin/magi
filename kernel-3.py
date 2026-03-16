#!/usr/bin/env python3
"""MAGI kernel-3 — B-loop + positional tools + tool hygiene + HTTP server."""

import json
import os
import sys
import time
import threading
import argparse
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import posixpath

# Load .env if present (no external dependency)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"

SHELL_PATH = "shell-3.json"
SEED_PATH = "seed-3.json"
SERVE_DIR = "./serve"
HTTP_PORT = 8080

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


def send_block(block, max_tokens=4000, temperature=0.7):
    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": json.dumps(block)},
        ],
        "system": "You are a JSON processor. You receive a JSON object. You return it updated. Return ONLY the JSON object. No markdown, no explanation, no code fences.",
    }
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


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


# --- Tool executor (positional args) ---

def safe_path(filename):
    """Resolve filename within SERVE_DIR. Reject escapes."""
    clean = posixpath.normpath("/" + filename).lstrip("/")
    if not clean or ".." in clean.split("/"):
        return None
    return os.path.join(SERVE_DIR, clean)


def execute_tool(req):
    """Execute a tool request. req is a dict with positional keys."""
    name = req.get("1", "")
    arg1 = req.get("2", "")
    arg2 = req.get("3", "")

    if name == "write_file":
        path = safe_path(arg1)
        if path is None:
            return "error", "Invalid path"
        os.makedirs(os.path.dirname(path) or SERVE_DIR, exist_ok=True)
        with open(path, "w") as f:
            f.write(arg2)
        return "done", f"written {arg1} ({len(arg2)} chars)"

    elif name == "read_file":
        path = safe_path(arg1)
        if path is None:
            return "error", "Invalid path"
        if not os.path.exists(path):
            return "error", f"not found: {arg1}"
        with open(path, "r") as f:
            content = f.read(2000)
        return "done", content

    elif name == "list_files":
        files = os.listdir(SERVE_DIR) if os.path.exists(SERVE_DIR) else []
        return "done", ", ".join(sorted(files)) or "(empty)"

    else:
        return "error", f"unknown tool: {name}"


def execute_pending_tools(block):
    """Scan key 8 for pending tool requests and execute them.

    Handles two formats:
    - Flat: 8.1 is a string (tool name), 8.2/8.3 are args, 8.4 is status
    - Nested: 8.1 is a dict containing {1: name, 2: arg1, 3: arg2, 4: status}
    """
    tools = block.get("8")
    if not isinstance(tools, dict):
        return

    # Check if flat format: 8.1 is a string (tool name directly)
    first = tools.get("1")
    if isinstance(first, str) and first and tools.get("4") not in ("done", "error"):
        # Flat format — key 8 IS the request
        name = first
        log(f"Tool: {name}(arg1={str(tools.get('2',''))[:80]})")
        try:
            status, result = execute_tool(tools)
        except Exception as e:
            status, result = "error", str(e)
        tools["4"] = status
        tools["5"] = result
        log(f"  -> {status}: {result[:120]}")
        return

    # Nested format — scan sub-keys for dicts
    for key in sorted(tools.keys()):
        if key == "_":
            continue
        req = tools[key]
        if not isinstance(req, dict):
            continue
        if req.get("4") in ("done", "error"):
            continue

        name = req.get("1", "")
        if not name:
            continue

        log(f"Tool: {name}(arg1={str(req.get('2',''))[:80]})")

        try:
            status, result = execute_tool(req)
        except Exception as e:
            status, result = "error", str(e)

        req["4"] = status
        req["5"] = result
        log(f"  -> {status}: {result[:120]}")


def clean_tool_queue(block):
    """Summarise executed tools into 8._, clear requests."""
    tools = block.get("8")
    if not isinstance(tools, dict):
        return

    summaries = []

    # Check flat format: 8.1 is a string and 8.4 is done/error
    first = tools.get("1")
    if isinstance(first, str) and first and tools.get("4") in ("done", "error"):
        name = first
        status = tools.get("4", "?")
        result = str(tools.get("5", ""))[:100]
        summaries.append(f"{name}: {status} — {result}")
    else:
        # Nested format — scan sub-keys for dicts
        for key in sorted(tools.keys()):
            if key == "_":
                continue
            req = tools[key]
            if isinstance(req, dict) and req.get("4") in ("done", "error"):
                name = req.get("1", "?")
                status = req.get("4", "?")
                result = str(req.get("5", ""))[:100]
                summaries.append(f"{name}: {status} — {result}")

    # Clear all requests, write summary to _
    block["8"] = {
        "_": "; ".join(summaries) if summaries else "No tools used last cycle.",
        "1": {"1": "", "2": "", "3": "", "4": "", "5": ""}
    }


def preserve_user_input(updated_block):
    """If user input arrived during LLM processing, preserve it."""
    with _shell_lock:
        if os.path.exists(SHELL_PATH):
            with open(SHELL_PATH, "r") as f:
                current = json.load(f)
            current_input = current.get("6", "")
            if current_input and not updated_block.get("6"):
                updated_block["6"] = current_input
                log(f"Preserved user input: {current_input[:120]}")


# --- HTTP server ---

class MAGIHandler(SimpleHTTPRequestHandler):
    """Serves ./serve/ as static files, /state as shell-3.json, /input as POST endpoint."""

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
        content_type = self.headers.get("Content-Type", "")
        text = ""
        if "application/json" in content_type:
            try:
                data = json.loads(body)
                text = data.get("text", data.get("message", ""))
            except (json.JSONDecodeError, AttributeError):
                text = body.decode("utf-8", errors="replace")
        elif "application/x-www-form-urlencoded" in content_type:
            form = parse_qs(body.decode("utf-8", errors="replace"))
            text = form.get("text", form.get("message", [""]))[0]
        else:
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

        # Redirect form POSTs back to the page; JSON POSTs get JSON response
        if "application/x-www-form-urlencoded" in content_type:
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        else:
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

    # Execute pending tools and clean queue BEFORE sending to LLM
    execute_pending_tools(block)
    clean_tool_queue(block)
    save_block(block)

    # Shell size warning
    shell_size = len(json.dumps(block))
    if shell_size > 6000:  # ~1500 tokens
        log(f"WARNING: shell is {shell_size} chars — content may be embedded instead of filed")

    try:
        raw = send_block(block)
    except Exception as e:
        log(f"Network error: {e}")
        return

    log(f"Raw ({len(raw)} chars): {raw[:300]}")

    updated = extract_json(raw)
    if updated is None:
        log(f"REJECT: no valid JSON. Last 500 chars: ...{raw[-500:]}")
        return

    if not is_pscale_valid(updated):
        bad_keys = [k for k in _all_keys(updated) if k not in {"_","1","2","3","4","5","6","7","8","9"}]
        log(f"REJECT: non-pscale keys: {bad_keys[:10]}")
        return

    # Restore immutable keys (_, 1, 2) from seed — LLM can only modify 3-9
    with open(SEED_PATH, "r") as f:
        seed = json.load(f)
    for key in ("_", "1", "2"):
        if key in seed:
            updated[key] = seed[key]

    # Preserve user input that arrived during LLM call
    preserve_user_input(updated)

    save_block(updated)

    concern = updated.get("3", "")
    if isinstance(concern, dict):
        summary = concern.get("1", str(concern))[:120]
    else:
        summary = str(concern)[:120]
    log(f"Concern: {summary}")
    log(f"Shell: {json.dumps(updated, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="MAGI kernel-3 — B-loop + positional tools + hygiene + HTTP")
    parser.add_argument("--interval", type=int, default=0, help="Sleep seconds between cycles (default: 0, no delay)")
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
    log_name = f"kernel3-{time.strftime('%Y%m%d-%H%M%S')}.log"
    _log_file = open(log_name, "w")
    log(f"Kernel-3 starting. Interval: {interval}s. Cycles: {max_cycles or 'unlimited'}. Log: {log_name}")

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
