#!/usr/bin/env python3
"""Preflight for the gts9uwifi firmware step.

The Mu-Silicium platform package, the device config and the vendor DXE set all have to agree
before an FD is worth flashing.  This checks the files the driver will read and warns when the
vendor DXE set is still the Tab S9 seed.

The UniXNU driver runs preflight scripts from the assembled build tree:
    python3 <tree>/scripts/check-gts9uwifi.py        (cwd = <tree>)
so the Mu-Silicium checkout is located by probing, not by assuming the cwd.
"""
import os
import sys

CHECKS = [
    ("Platforms/Samsung/gts9uwifiPkg/gts9uwifi.dsc", "device DSC"),
    ("Platforms/Samsung/gts9uwifiPkg/gts9uwifi.fdf", "device FDF"),
    ("Platforms/Samsung/gts9uwifiPkg/DeviceBuild.py", "stuart build description"),
    ("Resources/Configs/gts9uwifi.toml", "boot shim / FD / boot image parameters"),
    ("Binaries/gts9uwifi", "vendor DXE drivers"),
]


def find_uefi():
    """Return the Mu-Silicium checkout, or None when it cannot be located."""
    candidates = []
    env = os.environ.get("UNIXNU_UEFI")
    if env:
        candidates.append(env)
    candidates.append(os.getcwd())
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in ("..", "../..", "../../.."):
        candidates.append(os.path.normpath(os.path.join(here, rel)))
    # the tree keeps .cache/firmware pointing at the device repository
    cache = os.path.join(here, "..", ".cache", "firmware")
    if os.path.isdir(cache):
        candidates.append(os.path.normpath(os.path.join(cache, "..", "..")))
    for maybe in candidates:
        if maybe and os.path.isfile(os.path.join(maybe, "Platforms/Samsung/gts9uwifiPkg/gts9uwifi.dsc")):
            return maybe
    return None


def main():
    uefi = find_uefi()
    if uefi is None:
        print("gts9uwifi preflight: skipped, no Mu-Silicium checkout with gts9uwifiPkg found "
              "(pass --uefi / set UNIXNU_UEFI)", file=sys.stderr)
        return 0

    print(f"gts9uwifi preflight: uefi checkout {uefi}")
    ok = True
    for path, why in CHECKS:
        if not os.path.exists(os.path.join(uefi, path)):
            print(f"gts9uwifi preflight: missing {why}: {path}", file=sys.stderr)
            ok = False
    if not ok:
        return 1

    config = os.path.join(uefi, "Resources/Configs/gts9uwifi.toml")
    text = open(config, encoding="utf-8").read()
    for key in ("[boot_shim]", "[uefi_fd]", "[boot_image]"):
        if key not in text:
            print(f"gts9uwifi preflight: {config} has no {key} section", file=sys.stderr)
            ok = False

    dsc = open(os.path.join(uefi, "Platforms/Samsung/gts9uwifiPkg/gts9uwifi.dsc"), encoding="utf-8").read()
    if "UNIXNU_PAYLOAD" not in dsc:
        print("gts9uwifi preflight: warning: DSC has no UNIXNU_PAYLOAD guard, the FD will not "
              "contain UniXNU/DarwinBoot", file=sys.stderr)

    source = os.path.join(uefi, "Binaries/gts9uwifi/SOURCE.txt")
    if os.path.isfile(source) and "gts9wifi" in open(source, encoding="utf-8", errors="replace").read():
        print("gts9uwifi preflight: WARNING vendor DXE seeded from Binaries/gts9wifi "
              "(replace after dumping the SM-X910 abl)", file=sys.stderr)

    if ok:
        print("gts9uwifi preflight: ok")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
