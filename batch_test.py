"""Batch runner: executes every demo scene and records results."""
import os
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT)

# Get the scene list from run.py without executing it
import importlib.util
spec = importlib.util.spec_from_file_location("run_mod", os.path.join(PROJECT, "run.py"))
run_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_mod)
SCENES = run_mod.SCENES

results = []
for num, desc, cls in SCENES:
    label = f"{num:>3}. {desc}"
    start = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "run.py", num],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PYTHONPATH": ""},  # avoid hermes venv shadowing
        )
        elapsed = time.time() - start
        if proc.returncode == 0 and "Saved:" in proc.stdout:
            results.append((num, desc, "OK", elapsed, ""))
            print(f"[OK]   {label} ({elapsed:.1f}s)")
        else:
            err = (proc.stderr or proc.stdout)[-300:].replace("\n", " | ")
            results.append((num, desc, "FAIL", elapsed, err))
            print(f"[FAIL] {label} ({elapsed:.1f}s): {err}")
    except subprocess.TimeoutExpired:
        results.append((num, desc, "TIMEOUT", 120, "timeout"))
        print(f"[TIME] {label}")
    except Exception as e:
        results.append((num, desc, "ERROR", 0, str(e)))
        print(f"[ERR]  {label}: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
ok = [r for r in results if r[2] == "OK"]
fail = [r for r in results if r[2] != "OK"]
print(f"Total: {len(results)}  OK: {len(ok)}  Failed: {len(fail)}")
if fail:
    print("\nFailures:")
    for num, desc, status, elapsed, err in fail:
        print(f"  {num:>3}. {desc}: {status} — {err}")
print("\nVideos saved to downloaded_videos/")
