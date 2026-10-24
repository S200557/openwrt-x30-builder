# Stable X30 hardware corrections

This change carries the physically verified hardware corrections from the
upstream contribution draft onto the existing stable X30 profile. The initial
test image targets official OpenWrt **v25.12.6**, kernel **6.12.112**.

The new third patch fixes the 2.4 GHz/5 GHz indicator GPIOs, removes the
duplicate per-radio MAC overrides so mt76 reads its factory EEPROM addresses,
corrects the printed-label MAC source and removes nonexistent USB hardware.
The undefined `factory.bin` image is removed from the profile. Existing
stable LED names, profile names, supported-device identifiers, flash
partitions, FIT upgrade handling and WAN pin configuration are retained.
The original bootloader source and installed bootloader are unaffected.

The build also includes `ip-bridge` and `iperf3` (and their dependencies),
which were already manually installed on the test router. User configuration
and custom software still require a verified configuration/overlay backup.

## Validation gates

- Apply the complete patch series against both v25.12.5 and v25.12.6 using
  the same three-way application as the build workflow.
- Run FIT dispatch/image rejection and network-default regression tests.
- Build the full stable firmware, then check the actual compiled device tree
  against the observed GPIO assignments, EEPROM references and flash layout.
- Verify the image's compatible device metadata, manifest, checksums and
  build provenance against the reviewed PR head and official source commit.
- Before installation, confirm the exact router model/board, current stable
  kernel, unchanged SSH host key and working authentication.
- Save a fresh sysupgrade configuration/overlay backup and package inventory
  to a private folder outside the repository. Read every archive member and
  verify the off-router SHA256. Keep credentials and device identifiers private.
- Transfer the verified squashfs sysupgrade image and pass the router's image
  compatibility test. Preserve settings and record the upgrade as issued
  before invoking it, so a reconnect cannot cause a second flash.
- After reboot, verify the release/kernel, config hashes, LAN/WAN, DNS,
  enabled Wi-Fi radios, permanent radio MAC uniqueness, LEDs and key services.
  Button testing must first intercept the normal reset/WPS actions safely.

## Relationship to the upstream contribution

The development-branch draft remains separate in PR #10 and uses Linux 6.18.55.
Its firmware and bootloader build has passed. Stable runtime results can
support the shared hardware findings, but do not establish runtime support
for a different kernel. The development image needs its own controlled
runtime test; it is not part of this stable installation.

Original support and installation report: sing <wx9745@gmail.com>,
[OpenWrt PR #21061](https://github.com/openwrt/openwrt/pull/21061).
Revision preparation/hardware observations: Sami Ibrahim <sami.j20@gmail.com>.
Preparation assisted by OpenAI Codex. The final upstream DCO certification
remains pending human review. UART header/pinout and stock-recovery details
still need independent confirmation before claiming those paths are tested.

## Current status

Patch application and network regression checks have passed locally. Full
candidate build, fresh backup and device runtime validation are pending.
