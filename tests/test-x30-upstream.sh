#!/bin/sh
# Validate the proposed upstream tree without touching a router.
set -eu

tree=${1:?Usage: sh tests/test-x30-upstream.sh OPENWRT_TREE}
tests=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sh "$tests/test-x30-fit-upgrade.sh" "$tree"

network="$tree/target/linux/mediatek/filogic/base-files/etc/board.d/02_network"
sh -n "$network"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
# The three OpenWrt library imports are replaced by strict stubs. The actual
# board-default script still runs, including its calls at the bottom.
sed '/^\. \/lib\/functions/d' "$network" > "$scratch/network"
board_name() { printf '%s\n' 'totolink,x30'; }
board_config_update() { :; }
board_config_flush() { :; }
ucidef_set_interfaces_lan_wan() { printf 'interfaces:%s:%s\n' "$1" "$2"; }
ucidef_set_interface_macaddr() { echo 'Unexpected interface MAC override' >&2; exit 1; }
ucidef_set_label_macaddr() { printf 'label:%s\n' "$1"; }
mtd_get_mac_binary() {
	[ "$1" = factory ] && [ "$2" = 0x4 ] || exit 1
	printf '%s\n' '02:11:22:33:44:50'
}
actual=$(. "$scratch/network")
expected=$(printf '%s\n' 'interfaces:lan1 lan2 lan3 lan4:wan' 'label:02:11:22:33:44:50')
[ "$actual" = "$expected" ] || {
	printf 'Unexpected board defaults:\n%s\n' "$actual" >&2
	exit 1
}
echo 'PASS: four LAN ports, separate WAN and factory label MAC are configured correctly'
