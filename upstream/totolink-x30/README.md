# TOTOLINK X30 upstream contribution draft

This directory contains an unsigned draft replacement for the device support
proposed in [OpenWrt PR #21061](https://github.com/openwrt/openwrt/pull/21061).
It is separate from the existing stable firmware build. It has not been
submitted upstream, and the corrected sources have not been flashed.

Original implementation: **sing <wx9745@gmail.com>**, commit
`1e4bed859aeb3c7047ee602866d833efed853e2d`.

Revision preparer and hardware tester: **Sami Ibrahim <sami.j20@gmail.com>**.
Code preparation and investigation assisted by **OpenAI Codex**. Preserve the
original author's authorship and existing sign-off when preparing the series;
Sami's sign-off remains pending his review and DCO certification of the final
changes. Supplying identity details alone is not that certification.

## Source baseline

The draft targets OpenWrt main at
`a25fb079b1463cd5d7d69c6d9a1c28d873291ebb` (2026-10-22), with Linux 6.18.55 and
U-Boot 2026.07. The running router uses the previously verified custom 25.12.6
release. Its successful upgrade does not validate a new main-branch image.

## Corrections being validated

- Normalize device/profile/bootloader/artifact paths to lowercase `x30`.
- Keep `totolink,X30` and `totolink,x30` supported-device metadata and FIT
  upgrade handling, including propagation of image validation failures.
- Use explicit LED bindings and modern color/function properties. Physical
  isolated tests confirmed GPIO 34 = 2.4G and GPIO 35 = 5G.
- Remove the nonexistent USB indicator and enabled USB controllers. Photos
  and [the official specifications](https://www.totolink.net/products/x30)
  show no external USB port.
- Let mt76 obtain each radio's permanent MAC from its EEPROM, instead of
  assigning the same MAC to both radio nodes. On the tested unit the EEPROM
  contains valid primary and secondary addresses at offsets 0x4 and 0xa;
  the latter is base + 4. Do not substitute an invented increment.
- Keep LAN = factory base + 3 and WAN = factory base + 1. Set the label MAC
  from factory offset 0x4, which matches the printed label on the tested unit.
- Define the WAN PHY LED pin locally for the current kernel, whose parent
  device tree no longer defines `gbe_led0_pins`.
- Remove the undeclared `factory.bin` image. Retain the existing FIT layout,
  partition boundaries and configuration-preserving sysupgrade behavior.
- Refresh the embedded bootloader patch using OpenWrt's quilt workflow and
  the next unused patch number, 505.

## Hardware evidence

Observed by software: MT7981B, 256 MiB RAM, 128 MiB Winbond SPI NAND with
128 KiB erase blocks and 2 KiB pages, MT7531 switch, four LAN interfaces and
one WAN interface. The exact flash and RAM chip markings have not been read.
The original contributor identifies the radio front end as MT7976C.

Photos confirm front labels MESH, 2.4G, 5G, CPU and PWR; four numbered LAN
ports, WAN, DC input, power button and RST pinhole; model X30 and 12 V / 1 A.
The MESH button is mapped to the standard WPS key code in the original
implementation; OEM mesh pairing is not an OpenWrt button action.

The original contributor reports installation through UART and an FIP
replacement followed by TFTP installation of the production FIT image.
The internal UART header/pinout, OEM bootloader menu and reverting to stock
have **not** been independently verified. These details must be resolved or
clearly accepted by the upstream reviewer before publishing installation
instructions. No bootloader write is part of this validation work.

Photos, serial numbers, full device MAC addresses, configuration archives,
passwords and router state files stay outside the contribution.

## Validation status

The isolated working tree is `.verification/upstream-x30` (ignored by Git).
Run `sh tests/test-x30-upstream.sh OPENWRT_TREE` for FIT dispatch and network
default checks. These use stubs and cannot flash or reconfigure a router.

Completed locally against the pinned current sources:

- The device tree compiles after the complete OpenWrt kernel patch series.
  Compiled properties confirm both Wi-Fi indicator pins and the absence of
  per-radio MAC overrides. The shared parent still produces its existing
  duplicate USB efuse unit-address warning; the X30 file has no DTC warnings.
- U-Boot 2026.07 accepts the X30 defconfig. Its embedded board patch was
  regenerated using `make package/uboot-mediatek/refresh` and applies at the
  end of the current patch series.
- FIT dispatch, image rejection propagation and network defaults pass the
  isolated tests in `tests/test-x30-upstream.sh`.
- The draft validation workflow passes actionlint 1.7.12.

The `Validate X30 upstream contribution draft` GitHub workflow builds the
complete minimal base firmware and bootloader artifacts from the pinned
core tree, without optional feeds. It records checksums, source provenance
and both compatible device identifiers. It has read-only permissions and
does not publish a release or deploy firmware. This validates device
support separately from the existing stable image's optional user packages.

Full firmware and bootloader compilation and runtime validation of the
corrected image remain required until that workflow and device testing pass.
The physical reset and MESH buttons have not been tested; a short reset
press currently reboots OpenWrt, so any live test needs a reversible handler
interception before the user presses it.
