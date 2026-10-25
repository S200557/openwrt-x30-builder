# Unsigned commit-message draft

The text below preserves the original author and sign-off. Sami's additional
sign-off is intentionally absent until his review and DCO certification.
Keep this notice out of the final commit message.

```text
From: sing <wx9745@gmail.com>
Subject: mediatek: add support for TOTOLINK X30

Add support for the TOTOLINK X30, including the STC-branded unit.

Hardware specification:
  SoC: MediaTek MT7981B, dual-core Cortex-A53
  RAM: 256 MiB; chip marking not inspected
  Flash: 128 MiB Winbond SPI NAND, 128 KiB blocks, 2 KiB pages
  Wi-Fi: dual-band 2x2; MT7976C reported by the original contributor
  Ethernet: four gigabit LAN ports and one gigabit WAN, MT7531 switch
  LEDs: fixed PWR, blue CPU/2.4G/5G, blue/red MESH; no USB port
  Buttons: reset, front MESH exposed as WPS, physical power switch
  UART: J500 above the heatsink, antenna-side PCB edge, 115200 8N1
  Power: 12 V DC, 1 A

Flash instructions:
  Use a 3.3 V TTL adapter with no flow control. With Ethernet sockets
  on the left, J500 pins from the Ethernet end are 3.3V, TX, RX, GND.
  Leave 3.3V disconnected; cross TX/RX and connect common GND.
  Isolate Ethernet, serve the matching X30 images by TFTP from
  192.168.1.254/24, and use router address 192.168.1.1.
  Interrupt the original UART boot menu with an arrow key, select
  "Upgrade ATF FIP" and supply the X30 bl31-uboot.fip. Restart into
  OpenWrt U-Boot, select "Load production system via TFTP then write
  to NAND" and supply the X30 squashfs-sysupgrade.bin. Wait until
  writing completes. This is the owner's reported earlier install;
  the revised U-Boot binary has not been installed in this session.
  Use exactly the filename requested by the bootloader: legacy
  images use totolink_X30; this revision uses totolink_x30.
  No tested revert-to-stock procedure is available. The OEM recovery
  web page is not a demonstrated OpenWrt sysupgrade installer.

MAC address layout (base = factory partition offset 0x4):
  LAN: base + 3
  WAN: base + 1
  2.4 GHz: radio EEPROM primary address at factory offset 0x4
  5 GHz: radio EEPROM secondary address at factory offset 0xa
  Label: base at factory offset 0x4
  The tested EEPROM secondary is base + 4; retain EEPROM sourcing
  rather than inventing a per-band increment. Unit bytes: xx:xx:xx.

Keep legacy compatible IDs and FIT image validation. Enable preboot
reset checking with RAM-only TFTP recovery, independent of stale
NAND-write controls. Saved legacy environments require separate
review; a routine firmware upgrade does not migrate boot policy.

Linux 6.18.55 RAM tests covered LAN2, both secured Wi-Fi bands with
client DHCP/traffic/ping, radio and Ethernet MACs, LED mapping and
physical MESH/reset events. Hosted U-Boot tests cover recovery flow;
they do not establish physical reset recovery with the new binary.

Signed-off-by: sing <wx9745@gmail.com>
[Sami Ibrahim: refresh current sources, correct hardware mappings,
 add FIT compatibility, validate RAM operation and recovery logic;
 preparation assisted by OpenAI Codex]
```

Pending: Sami Ibrahim <sami.j20@gmail.com> must review this final scope and
certify the DCO before his sign-off is added. Final submission must link the
original PR and the owner's installation report in its description.
