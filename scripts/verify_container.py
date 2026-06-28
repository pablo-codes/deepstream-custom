#!/usr/bin/env python3
"""
Post-build verification script for the DeepStream custom container.
Runs inside the built image to confirm all required packages are present
and functional before the image is pushed to GHCR.

Exit code 0 = all checks passed, non-zero = at least one check failed.
"""

import sys
import importlib
import os

PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"

failures = []

# ──────────────────────────────────────────────────────────
# 1. Python package import checks
# ──────────────────────────────────────────────────────────
REQUIRED_PACKAGES = {
    "yaml":       "PyYAML",       # pyservicemaker depends on this
    "cv2":        "opencv-python-headless",
    "numpy":      "numpy",
    "torch":      "torch",
}

# These are from the DeepStream base image — nice to verify but
# they will fail on a non-GPU CI runner, so we treat them as warnings.
OPTIONAL_PACKAGES = {
    "pyservicemaker": "pyservicemaker (DeepStream 9.0 SDK)",
}

print("=" * 60)
print("  POST-BUILD VERIFICATION")
print("=" * 60)
print()

print("── Required Python Packages ──")
for import_name, display_name in REQUIRED_PACKAGES.items():
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")
        print(f"  {PASS}  {display_name:<30} (import {import_name}, v{version})")
    except Exception as e:
        print(f"  {FAIL}  {display_name:<30} (import {import_name}: {e})")
        failures.append(display_name)

print()
print("── Optional Python Packages (warnings only) ──")
for import_name, display_name in OPTIONAL_PACKAGES.items():
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")
        print(f"  {PASS}  {display_name:<30} (v{version})")
    except Exception as e:
        print(f"  ⚠️  WARN  {display_name:<30} ({e})")

# ──────────────────────────────────────────────────────────
# 2. DeepStream filesystem checks
# ──────────────────────────────────────────────────────────
print()
print("── DeepStream Filesystem ──")

DS_BASE = "/opt/nvidia/deepstream/deepstream"
REQUIRED_PATHS = [
    (f"{DS_BASE}/version",                                       "DS version file"),
    (f"{DS_BASE}/samples/streams/sample_720p.mp4",               "Sample video"),
    (f"{DS_BASE}/samples/configs/deepstream-app",                "App configs dir"),
    (f"{DS_BASE}/lib",                                           "DS libraries dir"),
]

for path, label in REQUIRED_PATHS:
    exists = os.path.exists(path)
    status = PASS if exists else FAIL
    print(f"  {status}  {label:<40} ({path})")
    if not exists:
        failures.append(f"Missing path: {path}")

# ──────────────────────────────────────────────────────────
# 3. GStreamer check
# ──────────────────────────────────────────────────────────
print()
print("── GStreamer ──")
gst_result = os.popen("gst-inspect-1.0 --version 2>/dev/null").read().strip()
if gst_result:
    print(f"  {PASS}  {gst_result.splitlines()[0]}")
else:
    print(f"  {FAIL}  gst-inspect-1.0 not found")
    failures.append("GStreamer not found")

# ──────────────────────────────────────────────────────────
# 4. pip metadata integrity check
# ──────────────────────────────────────────────────────────
print()
print("── pip Metadata Integrity ──")
pip_check = os.popen("pip3 check 2>&1").read().strip()
if "No broken requirements found" in pip_check:
    print(f"  {PASS}  No broken requirements")
else:
    # Warn but don't fail — the base image has known numpy metadata issues
    for line in pip_check.splitlines()[:5]:
        print(f"  ⚠️  WARN  {line}")

# ──────────────────────────────────────────────────────────
# Result
# ──────────────────────────────────────────────────────────
print()
print("=" * 60)
if failures:
    print(f"  ❌ VERIFICATION FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"     • {f}")
    print("=" * 60)
    sys.exit(1)
else:
    print("  ✅ ALL CHECKS PASSED — image is ready to push")
    print("=" * 60)
    sys.exit(0)
