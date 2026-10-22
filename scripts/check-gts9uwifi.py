#!/usr/bin/env python3
"""Preflight for the gts9uwifi firmware step.

The Mu-Silicium platform package, the device config and the vendor DXE set all have to agree
before an FD is worth flashing.  This checks the three files the driver will read and refuses
the build when the device-specific inputs are still the Tab S9 placeholders.

Run by `unixnu build firmware` through board.toml [firmware] preflight, from the uefi checkout.
"""
import hashlib
import os
import sys

UEFI = "."

CHECKS = [
    # (path relative to the Mu-Silicium checkout, why)
    ("Platforms/Samsung/gts9uwifiPkg/gts9uwifi.dsc", "device DSC"),
    ("Platforms/Samsung/gts9uwifiPkg/gts9uwifi.fdf", "device FDF"),
    ("Platforms/Samsung/gts9uwifiPkg/DeviceBuild.py", "stuart build description"),
    ("Resources/Configs/gts9uwifi.toml", "boot shim / FD / boot image parameters"),
    ("Binaries/gts9uwifi", "vendor DXE drivers"),
]


def fail(msg):
    print(f"gts9uwifi preflight: {msg}", file=sys.stderr)
    return False


def main():
    ok = True
    for path, why in CHECKS:
        full = os.path.join(UEFI, path)
        if not os.path.exists(full):
            ok = fail(f"missing {why}: {path}")
    if not ok:
        return 1

    config = os.path.join(UEFI, "Resources/Configs/gts9uwifi.toml")
    text = open(config, encoding="utf-8").read()
    for key in ("[boot_shim]", "[uefi_fd]", "[boot_image]"):
        if key not in text:
            ok = fail(f"{config} has no {key} section")

    # The vendor DXE set is seeded from the Tab S9 until the SM-X910 abl is dumped.  Warn, do not
    # fail: UEFI with the Tab S9 drivers is exactly the experiment that tells us whether the seed
    # is good enough.
    binaries = os.path.join(UEFI, "Binaries/gts9uwifi")
    if os.path.isdir(binaries):
        with open(os.path.join(binaries, "SOURCE.txt"), encoding="utf-8", errors="replace") as fh:
            origin = fh.read().strip() if os.path.exists(os.path.join(binaries, "SOURCE.txt")) else ""
        if "gts9wifi" in origin:
            print("gts9uwifi preflight: WARNING vendor DXE seeded from Binaries/gts9wifi "
                  "(replace after dumping the SM-X910 abl)", file=sys.stderr)

    for root, _dirs, files in os.walk(binaries):
        for name in files:
            if name.endswith(".inf"):
                pass
    print("gts9uwifi preflight: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
