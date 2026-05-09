# OpenWrt X30 Builder

Automated OpenWrt builds for the **TOTOLINK X30** router on the MediaTek Filogic target.

This repository builds a custom OpenWrt image for the X30 by combining:

- the official OpenWrt stable branch
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
- Tailscale (includes the tailscaled daemon)
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
