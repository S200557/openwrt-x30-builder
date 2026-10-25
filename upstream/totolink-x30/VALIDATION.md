# Validation evidence

## Exact tested sources

- OpenWrt: `a25fb079b1463cd5d7d69c6d9a1c28d873291ebb`.
- Builder head used for the real development RAM test:
  `435456d3ca47f94db04d956ddf8a088279f95e3b`.
- Development image: Linux 6.18.55, SNAPSHOT, `mediatek/filogic`, X30.
- RAM image SHA256:
  `18d6568c536767bea51e46de701c5cd9e0c3514d40e2b3e2bf7ffcaa8babe6d6`.
- [Development full build](https://github.com/S200557/openwrt-x30-builder/actions/runs/40133262529),
  [stable full build](https://github.com/S200557/openwrt-x30-builder/actions/runs/40133262539),
  and [25.12.5/25.12.6 patch checks](https://github.com/S200557/openwrt-x30-builder/actions/runs/40133262553)
  all passed for that builder head. The PR publisher was intentionally skipped.

Artifact archive/file hashes, generated configuration, patch hash, source
provenance, FIT component hashes and embedded DTBs were independently checked.
The subsequent source revision changes only the embedded U-Boot recovery
policy; Linux board support remains identical to the RAM-tested draft. Its
new bootloader/CI results must be recorded separately.

## Physical and runtime findings, 25 October 2026

| Area | Result and scope |
| --- | --- |
| Identity | Same physical X30, factory identity, 256 MiB RAM and 128 MiB Winbond SPI NAND verified |
| Root filesystem | Development system ran in RAM; production FIT checksum stayed unchanged |
| Ethernet | LAN2 linked at 1 Gbps and carried management traffic; other ports not individually cable-tested |
| Radio MACs | 2.4 GHz used factory EEPROM offset 0x4; 5 GHz used offset 0xa; both were valid and distinct |
| LAN/WAN/label MACs | LAN = factory base + 3, WAN = base + 1, label = base, checked at runtime |
| Wi-Fi clients | Secured 2.4 GHz and 5 GHz APs passed authentication, DHCP, bidirectional traffic and ping |
| Indicators | Running FDT and sysfs triggers matched GPIO 34/2.4 GHz and GPIO 35/5 GHz; physical pin mapping was observed in isolated stable tests |
| Buttons | Front MESH emitted WPS and rear RST emitted reset while normal actions were intercepted; original handlers restored |
| Kernel health | No panic, Oops, BUG or call trace observed in retained final kernel log |
| Return to stable | Original 25.12.6 / Linux 6.12.112, configuration hashes, all 192 packages and both original boot environments verified |
| Services/network | All 13 expected stable services, LAN/WAN state, internet/DNS, firewall and Tailscale verified after return |
| Laptop cleanup | Temporary addresses, host routes, firewall rule, TFTP service and Wi-Fi profiles removed; original Wi-Fi and Ethernet DHCP restored |

Two WPS press/release pairs were captured during the requested MESH tap
sequence. One reset pair was captured, all releases were short and no button
remained held. The extra WPS pair is an observation; its cause was not established.

The original stable configuration had one secured AP enabled and its other AP
disabled. Testing used two temporary secured RAM profiles, then verified exact
restoration of the saved configuration. We do not equate a radio being detected
with a successful client traffic test.

## Bootloader recovery revision

The original generated target configuration had `CONFIG_USE_PREBOOT` disabled.
Its normal saved menu entry selected production directly, bypassing `boot_first`.
The revision enables preboot and gives reset a RAM-only retry path. A hosted
U-Boot 2026.07 test executes the actual environment's Hush control flow with
hardware doubles and fails closed on UBI, MTD or environment-save commands.

Cases cover normal boot handoff, pressed-reset RAM boot, stale NAND-write
control variables, transfer failures and rejected images. The target defconfig
is also checked for preboot enablement, and CI builds the actual target binary.
Hosted command-flow tests are not physical bootloader tests.

The exported patch also applies cleanly to current official main
`a27b155e89c3470d92077b8fc7992c18732332e9`, checked on 25 October 2026.
This is an application check, not a new firmware build/runtime claim for that
upstream revision.

No BL2/FIP binary was written during the stable or development RAM tests.
The installed U-Boot 2025.10 remains in place. The replacement U-Boot 2026.07,
power-on reset recovery, OEM revert and stock-to-OpenWrt install have not been
independently exercised during this validation session. The owner's earlier
successful UART installation is separately cited in INSTALLATION.md.

Private backups, raw photographs, client identifiers, raw router logs and keys
are retained locally, not in this repository.
