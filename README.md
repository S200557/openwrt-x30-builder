# OpenWrt X30 Builder

Automated OpenWrt builds for the **TOTOLINK X30** router on the MediaTek Filogic target.

This repository builds a custom OpenWrt image for the X30 by combining:

- the latest official OpenWrt stable release tag
- a pinned TOTOLINK X30 board-support patch
- a reproducible GitHub Actions workflow
- a minimal device-specific OpenWrt configuration

The goal is to produce updateable `sysupgrade.bin` images without manually compiling OpenWrt on a local machine.

## Target device

Device:

```text
TOTOLINK X30
```

## Built-in packages

- LuCI
- LuCI HTTPS support
- kmod-tun
- Tailscale / tailscaled
- ca-bundle

## Post-flash Tailscale setup

```sh
ssh root@192.168.1.1
/etc/init.d/tailscale enable
/etc/init.d/tailscale start
tailscale up
tailscale status
```

Do not commit Tailscale credentials, auth keys, reusable auth tokens, OAuth secrets, API keys, or other secrets to this repository.

## Validation and releases

Pull requests apply both local patches to OpenWrt **25.12.5** and **25.12.6**
and test FIT upgrade/image-check dispatch for both `totolink,X30` and
`totolink,x30`. The latest-release workflow also builds firmware for pull
requests, with read-only repository permissions. These runs upload artifacts
for inspection; only successful builds on `main` can publish a release, through
a separate job with write permission. Release tags point to the builder commit
that produced the artifacts. Actions are pinned to full commit SHAs.

The release source tree must pass the dispatch regression test before building.
Run it against an already patched source tree with:

```sh
sh tests/test-x30-fit-upgrade.sh /path/to/openwrt
```

### OpenWrt 25.12.6 patch failure

[Upstream commit 2a9a97a6eca0](https://github.com/openwrt/openwrt/commit/2a9a97a6eca08ac0d602b8718dbcaa3d1e220a7e)
added `wavlink,wl-wnt100x3-ubootmod` to the FIT device lists in `platform.sh`.
This changed the context expected by patch `0002`, so source preparation failed
before compilation. X30 now has dedicated cases for `fit_do_upgrade` and
`fit_check_image`, preserving the previous behavior and both board names without
depending on adjacent entries in those lists. Do not bypass a failed upgrade
patch or image metadata check to get a build through.
