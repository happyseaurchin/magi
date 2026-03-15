#!/usr/bin/env python3
"""MAGI B-loop test — run 5 cycles, log everything."""

import json
import os
import time
import copy
from kernel import send_block, extract_json, SEED_PATH

CYCLES = 5
LOG_DIR = "."


def run_test():
    ts = time.strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(LOG_DIR, f"bloop-test-{ts}.log")

    with open(SEED_PATH, "r") as f:
        seed = json.load(f)

    block = copy.deepcopy(seed)
    results = []

    for i in range(1, CYCLES + 1):
        print(f"Cycle {i}/{CYCLES}...", flush=True)
        prev_block = copy.deepcopy(block)

        try:
            raw = send_block(block)
        except Exception as e:
            results.append({
                "cycle": i,
                "error": str(e),
                "valid_json": False,
            })
            print(f"  Network error: {e}")
            continue

        updated = extract_json(raw)
        valid = updated is not None

        result = {
            "cycle": i,
            "valid_json": valid,
            "raw_response": raw,
        }

        if valid:
            # Structure preserved? Check _, 1, 2 against seed
            preserved = {}
            for key in ("_", "1", "2"):
                preserved[key] = updated.get(key) == seed.get(key)
            result["structure_preserved"] = preserved

            # Concern delta
            prev_concern = str(prev_block.get("3", ""))
            new_concern = str(updated.get("3", ""))
            result["prev_concern"] = prev_concern
            result["new_concern"] = new_concern
            result["concern_changed"] = prev_concern != new_concern

            # Growth — key 4 or new keys
            growth = {}
            key4 = updated.get("4", "")
            if key4 and key4 != seed.get("4", ""):
                growth["4"] = key4
            for k in updated:
                if k not in seed:
                    growth[k] = updated[k]
            result["growth"] = growth if growth else None

            # Use updated block for next cycle
            block = updated
        else:
            result["structure_preserved"] = None
            result["concern_changed"] = None
            result["growth"] = None

        results.append(result)
        status = "valid" if valid else "INVALID"
        print(f"  {status}", flush=True)

    # Write log
    with open(log_path, "w") as f:
        f.write(f"MAGI B-loop test — {ts}\n")
        f.write(f"Seed: {SEED_PATH}\n")
        f.write(f"Cycles: {CYCLES}\n")
        f.write("=" * 60 + "\n\n")

        valid_count = sum(1 for r in results if r.get("valid_json"))
        f.write(f"Summary: {valid_count}/{CYCLES} valid JSON responses\n\n")

        for r in results:
            f.write(f"--- Cycle {r['cycle']} ---\n")

            if "error" in r:
                f.write(f"ERROR: {r['error']}\n\n")
                continue

            f.write(f"Valid JSON: {r['valid_json']}\n")

            if r["structure_preserved"] is not None:
                for key, ok in r["structure_preserved"].items():
                    status = "preserved" if ok else "CHANGED"
                    f.write(f"  Key '{key}': {status}\n")

            if r["concern_changed"] is not None:
                f.write(f"Concern changed: {r['concern_changed']}\n")
                f.write(f"  Previous: {r['prev_concern'][:200]}\n")
                f.write(f"  Current:  {r['new_concern'][:200]}\n")

            if r["growth"]:
                f.write(f"Growth: {json.dumps(r['growth'], indent=2)}\n")
            else:
                f.write("Growth: none\n")

            f.write(f"\nRaw response:\n{r['raw_response']}\n\n")

        # Final assessment
        f.write("=" * 60 + "\n")
        f.write("Assessment:\n")

        if valid_count >= 4:
            f.write(f"  JSON validity: PASS ({valid_count}/{CYCLES})\n")
        else:
            f.write(f"  JSON validity: FAIL ({valid_count}/{CYCLES})\n")

        concerns = [r.get("new_concern", "") for r in results if r.get("valid_json")]
        if len(concerns) >= 2 and concerns[0] != concerns[1]:
            f.write("  Concern evolution: PASS (changed between cycle 1 and 2)\n")
        else:
            f.write("  Concern evolution: FAIL (flatlined or insufficient data)\n")

        all_preserved = all(
            r.get("structure_preserved", {}).get(k, False)
            for r in results if r.get("valid_json")
            for k in ("_", "1", "2")
        )
        if all_preserved:
            f.write("  Structure stability: PASS (keys _, 1, 2 unchanged)\n")
        else:
            f.write("  Structure stability: FAIL (stable keys were modified)\n")

    print(f"\nLog written to {log_path}")
    print(f"Result: {valid_count}/{CYCLES} valid, structure {'stable' if all_preserved else 'UNSTABLE'}")


if __name__ == "__main__":
    run_test()
