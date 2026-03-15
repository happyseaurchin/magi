#!/usr/bin/env python3
"""MAGI kernel — the heartbeat. Load, send, parse, save, sleep."""

import json
import os
import sys
import time
import argparse
import requests

API_URL = "https://lm.hermitcrab.uk/v1/chat/completions"
API_KEY = "sk-lm-bCXVCVv7:xEp0aFlihvp6LSxX6Jll"
MODEL = "mistralai/devstral-small-2-2512"

SHELL_PATH = "shell.json"
SEED_PATH = "seed.json"


def load_block():
    if not os.path.exists(SHELL_PATH):
        with open(SEED_PATH, "r") as f:
            seed = json.load(f)
        with open(SHELL_PATH, "w") as f:
            json.dump(seed, f, indent=2)
        log("Initialised shell.json from seed.json")
        return seed
    with open(SHELL_PATH, "r") as f:
        return json.load(f)


def send_block(block, max_tokens=2000, temperature=0.7):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": json.dumps(block)}],
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


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def cycle():
    block = load_block()
    try:
        raw = send_block(block)
    except Exception as e:
        log(f"Network error: {e}")
        return

    updated = extract_json(raw)
    if updated is None:
        log(f"No valid JSON: {raw[:200]}")
        return

    with open(SHELL_PATH, "w") as f:
        json.dump(updated, f, indent=2)

    concern = str(updated.get("3", ""))[:120]
    log(f"Concern: {concern}")


def main():
    parser = argparse.ArgumentParser(description="MAGI kernel — B-loop heartbeat")
    parser.add_argument("--interval", type=int, default=30, help="Sleep seconds between cycles")
    args = parser.parse_args()

    interval = int(os.environ.get("MAGI_INTERVAL", args.interval))
    log(f"Kernel starting. Interval: {interval}s")

    while True:
        cycle()
        time.sleep(interval)


if __name__ == "__main__":
    main()
