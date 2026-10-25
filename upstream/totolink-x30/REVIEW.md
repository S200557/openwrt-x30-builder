# Upstream review checklist

This packet is a draft. Do not add Sami's sign-off or publish an upstream PR
until he reviews the final changes and explicitly certifies the DCO.

## Existing review comments

The original discussion is [openwrt/openwrt#21061](https://github.com/openwrt/openwrt/pull/21061).

| Review topic | Resolution |
| --- | --- |
| LED binding constants | Include `dt-bindings/leds/common.h`; real DTB compilation passed |
| Uppercase device identifiers | Lowercase profile/DTS/U-Boot paths; retain both legacy image compatible IDs |
| LED syntax and indentation | Modern color/function properties, no deprecated mixed labels in Linux DTS, tabs retained |
| Wi-Fi LED GPIOs | GPIO 34 = 2.4 GHz, GPIO 35 = 5 GHz, physically observed |
| Missing WAN PHY indicator pin | Define `gbe_led0_pins` locally; the current parent does not provide it |
| Duplicate radio MACs | Remove per-band overrides and use the actual EEPROM addresses; the suggested unused +2 offset was not adopted |
| Undefined factory image | Remove `factory.bin`; preserve the FIT squashfs sysupgrade format |
| FIT upgrade dispatch | Both X30 IDs route to FIT validation/upgrade; rejection propagation tested |
| USB mismatch | No external USB port or indicator in the hardware; remove the enabled controllers and phantom indicator |
| U-Boot WPS key typo | Correct `linux,code` binding |
| Embedded patch hygiene | Quilt refresh, unversioned source paths and current next-free device slot 505 |
| Commit-message MAC layout | Add explicit LAN, WAN, 2.4 GHz, 5 GHz and label sources |
| Installation details | Owner's public UART/FIP/TFTP report and labelled J500 photo confirm location, wiring and serial settings |
| Reset recovery | Enable preboot and a RAM-only retry path; hosted tests cover failures and stale write controls |

The original automated review suggested both a guessed radio increment and
dropping the unresolved PHY pin reference. Decisions here use physical EEPROM
evidence and the current compiled parent DTS rather than adopting suggestions
without validation.

## Submission gates

1. Check the new full firmware/bootloader build and all patch checks for the
   final builder head. Earlier CI success is evidence for its recorded SHA.
2. Review the new recovery logic with its hardware/migration limits. Newly
   built U-Boot has not been installed on the test router.
3. The patch applies cleanly to official main at
   `a27b155e89c3470d92077b8fc7992c18732332e9` as checked on 25 October 2026.
   Recheck if main changes before submission. The RAM-test baseline remains
   pinned and must not be relabelled as a test of a different upstream revision.
4. Review COMMIT_MESSAGE.md and preserve original authorship/sign-off.
   Include a concise description of Sami's revisions and disclose assistance.
5. Sami explicitly certifies [DCO 1.1](https://developercertificate.org/) and
   authorizes submission of the final reviewed patch. Only then add his
   `Signed-off-by` trailer and prepare the upstream PR/series.

OpenWrt's [current review rules](https://github.com/openwrt/openwrt/blob/a27b155e89c3470d92077b8fc7992c18732332e9/.github/llm-review-rules.md)
require hardware, flash-instruction and MAC-layout sections for new devices.
Its [formalities configuration](https://github.com/openwrt/openwrt/blob/a27b155e89c3470d92077b8fc7992c18732332e9/.github/formalities.json)
checks sign-offs, noreply email, merge commits, line lengths and CRLF.

## Installation evidence limits

The owner confirmed J500 order as 3.3 V, TX, RX, GND from the Ethernet end,
matching the labelled photograph. Only GND/TX/RX are connected to the adapter.
This closes the location/pin-order gap without claiming a newly repeated stock
installation. Exact OEM versions/menu variations and reverting to stock remain
unverified. Other physical Ethernet ports have not been individually cable-tested.

The original author or maintainers have not been contacted from this workflow.
No upstream submission or human DCO certification is implied by this packet.
