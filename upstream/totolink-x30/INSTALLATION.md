# X30 installation and recovery notes

## UART location and wiring

The UART connector is the populated four-pin **J500** header, component side
of the PCB, above the heatsink near the antenna-side edge. With the Ethernet
sockets on the left, number the pins from the Ethernet end toward the opposite
end of the header. The owner's labelled photograph and confirmation give:

```text
                J500, component side
Ethernet end    [3.3V] [ TX ] [ RX ] [GND]    opposite end
                   1     2      3      4
                     heatsink below
```

| Router pin | Connect to USB-TTL adapter |
| --- | --- |
| 1: 3.3 V | Leave disconnected |
| 2: TX | RX |
| 3: RX | TX |
| 4: GND | GND |

Use **3.3 V TTL signalling**, **115200 baud, 8 data bits, no parity, one stop
bit, no flow control**. Power the router with its normal supply. Do not feed
adapter VCC, 3.3 V or 5 V into the header. Header identification is specific to
the photographed X30 PCB; verify markings before using another revision.

## Owner-reported initial installation

Sami's [published installation report](https://www.reddit.com/r/Saudi_Homelab/comments/1vb1m8f/)
documents a successful UART installation on the STC-branded X30, independently
supporting the method in the original contributor's commit. This report used
an earlier X30 bootloader/image, not the newly revised U-Boot 2026.07 binary.

The reported sequence is:

1. Open the enclosure from the underside after removing its rubber covers
   and screws. Connect J500 as above, retaining normal router power.
2. Connect the computer directly to a LAN port. Isolate other network cables
   and use TFTP server address `192.168.1.254/24`; router address is
   `192.168.1.1`. A gateway is unnecessary on this isolated direct subnet.
3. Serve the exact X30 FIP and squashfs sysupgrade images from the selected
   build, verifying their checksums before use. Do not substitute another
   device's image or mix bootloader and board revisions.
4. Interrupt the original boot menu through UART with an arrow key. The
   reported menu entry is `Upgrade ATF FIP`, using the X30 `bl31-uboot.fip`.
5. Reboot into the OpenWrt U-Boot menu. Select
   `Load production system via TFTP then write to NAND`, using the X30
   `squashfs-sysupgrade.bin`. Wait for writing to complete before restarting.

The report's filenames contain `totolink_X30`. This revision's generated
names contain `totolink_x30`. Serve the filename requested by the bootloader;
a legacy fixed filename may be a byte-identical alias of the verified image.
Do not change the image contents to address a filename mismatch.

This is an attributed installation record, not a claim that we repeated a
stock-to-OpenWrt installation or installed the revised FIP. Confirm the exact
OEM bootloader/menu on another unit before using these steps. No tested
revert-to-stock procedure is available. The owner's report says the vendor's
reset/recovery page did not accept the OpenWrt sysupgrade image; do not treat
that page as an OpenWrt factory-image installer.

## Existing compatible OpenWrt installations

Routine upgrades use only the matching X30 **squashfs sysupgrade** image,
never the preloader or FIP. Verify the exact board and FIT layout first.
The image supports `totolink,x30` and legacy `totolink,X30` identifiers.

Create a private configuration backup and package inventory, copy them off
the router, read/checksum the archive, verify the firmware checksum and device
metadata, and run `sysupgrade -T IMAGE` before a settings-preserving upgrade.
Never force a failed compatibility check. An archive preserves configuration,
not the installed package binaries: use a build that contains the packages
you need. The minimal development CI image is for validation and omits the
stable builder's optional user packages.

## Recovery policy and migration

With **this replacement bootloader and its new default environment**, reset
is checked during preboot. A pressed reset button enters a retrying TFTP
**RAM** boot using `openwrt-mediatek-filogic-totolink_x30-initramfs-recovery.bin`,
with the router/server addresses above. Release reset after recovery starts.
The retry path neither writes a recovery volume nor removes `rootfs_data`;
it ignores stale `replacevol`/`noboot` controls. Explicit UART write menu items
remain intentional installation actions.

This behavior is source- and hosted-test-validated; **RST-at-power-on has not
been tested with the replacement bootloader on hardware**. Saved legacy UBI
environments do not gain new defaults merely by compiling or replacing FIP,
and normal firmware sysupgrade does not migrate this boot policy. Any required
environment initialization belongs to a separately reviewed UART installation,
with verified backups; no automatic migration is supplied here.

The live RAM tests used a self-restoring menu entry staged through working SSH
on an already converted router. They prove that RAM image boot path and return
to stable firmware, not OEM reset recovery or the new bootloader's startup.
