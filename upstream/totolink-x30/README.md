# TOTOLINK X30 upstream contribution draft

This is an unsigned revision of the device support proposed in
[OpenWrt PR #21061](https://github.com/openwrt/openwrt/pull/21061), kept separate
from this repository's stable firmware builder. It has not been submitted
upstream. The corrected Linux support passed a real RAM boot and client tests;
the revised bootloader recovery policy still needs its new CI result and has
not been installed on hardware.

Original implementation and author: **sing <wx9745@gmail.com>**, commit
`1e4bed859aeb3c7047ee602866d833efed853e2d`.
Revisions and hardware observations: **Sami Ibrahim <sami.j20@gmail.com>**.
Preparation and investigation were assisted by **OpenAI Codex**. Preserve the
original author and existing sign-off. Sami's DCO certification remains pending
his review of the final changes; identity details alone are not a sign-off.

## Review documents

- [Installation and UART](INSTALLATION.md): J500 pin order, the owner's
  documented initial installation, compatible FIT upgrades and recovery limits.
- [Validation](VALIDATION.md): exact source/CI evidence and hardware-test scope.
- [Review checklist](REVIEW.md): existing upstream comments and remaining gates.
- [Commit message draft](COMMIT_MESSAGE.md): hardware, installation and MAC
  layout sections, with Sami's sign-off deliberately pending.

## Source baseline

OpenWrt main is pinned to `a25fb079b1463cd5d7d69c6d9a1c28d873291ebb`, with
Linux 6.18.55 and U-Boot 2026.07. The router remains on the independently
verified stable 25.12.6 / Linux 6.12.112 installation after the RAM tests.
Do not describe the development snapshot as an official stable release.

The patch normalizes the profile and artifact names to lowercase `x30`, keeps
both legacy compatible IDs and FIT upgrade validation, corrects the Wi-Fi LED
pins and label MAC source, and uses the radio EEPROM addresses. It removes
nonexistent USB hardware and the undefined factory image, defines the WAN PHY
indicator pin required by the current parent DTS, and refreshes the U-Boot board
patch through OpenWrt's quilt workflow.

The recovery revision enables preboot processing and routes a pressed reset
button to a TFTP RAM loop. Failed normal boot also falls back to RAM loading.
Automatic recovery does not call the NAND-writing recovery helper. Explicit
UART installation/write menu entries remain separate. See the migration and
physical-validation limits in [INSTALLATION.md](INSTALLATION.md).

## Reproduce checks

Apply `openwrt-main.patch` to the pinned source tree, then run:

```sh
sh tests/test-x30-upstream.sh OPENWRT_TREE
python3 tests/test-x30-bootloader.py OPENWRT_TREE
```

The second check needs the checksummed U-Boot archive in `OPENWRT_TREE/dl`,
standard native build dependencies and Python development headers. It builds
hosted U-Boot with test-only hardware doubles and fails on storage access.
It does not contact a router or prove the replacement bootloader's physical
reset-to-recovery behavior. CI also builds the real firmware and bootloader
and checks the target's generated preboot configuration.

Raw photos, serial numbers, full unit MAC addresses, backups, credentials and
router state remain outside this contribution.
