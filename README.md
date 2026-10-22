# UniXNU-gts9uwifi

UniXNU device repository for the **Samsung Galaxy Tab S9 Ultra (Wi-Fi)** — SM-X910, codename
`gts9uwifi`, SM8550-AC "kalama".

**State: skeleton / porting baseline.** The UEFI layer builds
(`uefi-sheng/Platforms/Samsung/gts9uwifiPkg`, derived from the working `gts9wifiPkg` of the
Tab S9 on the same SoC) and the Android boot image packs. Nothing here has booted on the tablet
yet, and the macOS/iOS side has not been exercised at all — the kernel step needs macOS + Xcode.

## What this repository is

The device layer of the UniXNU stack:

| File | Role |
|---|---|
| `board.toml` | board description: IPSW identity, userdata geometry, kernel defconfig and archive list, firmware (Mu-Silicium) description, payload and ADT parameters |
| `configs/gts9uwifi_defconfig` | kernel configuration, `CONFIG_XNU_*` |
| `scripts/make-gts9uwifi-adt.py` | generates the Apple-format hardware DT the kernel consumes |
| `scripts/check-gts9uwifi.py` | firmware preflight: the DSC/FDF/config/vendor set must agree |
| `scripts/read-userdata-lba.sh` | reads the real `userdata` GPT geometry off the tablet |

The generic half — build driver, UEFI boot manager, DarwinBoot, XNU patches, the 4 KiB page
work — comes from `UniXNU` and is not copied here.

## Prerequisites

* Linux with the UniXNU toolchain (see the parent project); **`build kernel` and
  `build userdata` require macOS + Xcode**, so use a Mac or the `macOS build` GitHub Action.
* `uefi-sheng` cloned next to this repository (`--uefi ../uefi-sheng`).
* An iPadOS/macOS restore image; `[ipsw]` in `board.toml` is the first target.
* The tablet with an unlocked bootloader.

## Progress

| Layer | State |
|---|---|
| Mu-Silicium UEFI (`gts9uwifiPkg`) | builds, `SILICIUM_UEFI.fd` 3 MB |
| Boot image packing (BootShim + FD + SM-X910 DTB) | builds, `ANDROID!` v4 |
| UEFI on the tablet | **not verified** |
| XNU kernel (prelink) | not started — needs macOS |
| Userdata / Apple userland | not started |

## Device facts already established

Read off the physical SM-X910, not assumed:

* SoC SM8550-AC, msm-id `0x218 0x20000 / 0x207 0x20000 / 0x207 0x10000 / 0x218 0x10000`
* board-id `0x10008 0x03` (the Tab S9 11" is `0x04` — the boards are not interchangeable)
* stock DTB from `/sys/firmware/fdt`: model `Samsung GTS9UWIFI PROJECT (board-id,03)`
* `reserved-memory/splash_region` = `0xb8000000` + `0x2b00000`, same window as the Tab S9
* panel 2960×1848 (landscape), vs 2560×1600 on the Tab S9
* partitions: `boot` 96 MiB, `abl` 4 MiB, `dtbo` 16 MiB, `uefi` 5 MiB, plus `init_boot`, `vendor_boot`
* no fastboot: `adb reboot bootloader` lands in Samsung Download mode (Odin protocol only)

## Open items

1. **Vendor DXE set** — `uefi-sheng/Binaries/gts9uwifi` is currently a copy of the Tab S9 set.
   Replace it with drivers extracted from this tablet's own `abl`/`uefi` partitions and re-test.
2. **userdata geometry** — run `scripts/read-userdata-lba.sh`; the LBA values in `board.toml` are
   sheng's until then, and building the userdata image against them writes outside the partition.
3. **SMEM RAM table** — confirm `owned_memory_size` and `dram_size`.
4. **Kernel enablement** — `CONFIG_XNU_SHENG_PMGR`, Adreno and the mobile display provider are off
   on purpose; each needs evidence on this board before it goes back on.
5. **macOS step** — the kernel prelink and userdata image need macOS + Xcode.

## Typical commands

```bash
./unixnu defconfig gts9uwifi_defconfig -D ../UniXNU-gts9uwifi
./unixnu fetch
./unixnu build package
./unixnu build firmware --uefi ../uefi-sheng
./unixnu bootimg --uefi ../uefi-sheng --dtb ../uefi-sheng/Resources/DTBs/gts9uwifi.dtb
# macOS only:
./unixnu ipsw fetch
./unixnu build kernel
./unixnu build payload --unique-chip-id <hex> --trust-cache <bundle> --data-ramdisk <seed>
```

## Licensing

Same terms as the upstream repositories this derives from: the files here are offered under the
BSD-2-Clause-Patent licence of UniXNU; the SM-X910 DTB and the vendor DXE binaries are Samsung's
and Qualcomm's and are not covered by it.
