#!/bin/sh
# Execute board defaults with strict stubs; never contact a router.
set -eu
tree=${1:?Usage: sh tests/test-x30-hardware.sh OPENWRT_TREE}
network="$tree/target/linux/mediatek/filogic/base-files/etc/board.d/02_network"
sh -n "$network"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
sed '/^\. \/lib\/functions/d' "$network" > "$scratch/network"
board_name() { printf '%s\n' "$TEST_BOARD"; }
board_config_update() { :; }
board_config_flush() { :; }
ucidef_set_interfaces_lan_wan() { printf 'interfaces:%s:%s\n' "$1" "$2"; }
ucidef_set_interface_lan() { printf 'lan:%s\n' "$1"; }
ucidef_set_interface_macaddr() { printf 'mac:%s:%s\n' "$1" "$2"; }
ucidef_set_label_macaddr() { printf 'label:%s\n' "$1"; }
mtd_get_mac_binary() {
	[ "$1" = factory ] && [ "$2" = 0x4 ] || exit 1
	printf '%s\n' '02:11:22:33:44:50'
}
get_mac_binary() {
	[ "$1" = /tmp/tp_data/default-mac ] && [ "$2" = 0 ] || exit 1
	printf '%s\n' '02:11:22:33:44:60'
}
TEST_BOARD=totolink,x30
actual=$(. "$scratch/network")
expected=$(printf '%s\n' 'interfaces:lan1 lan2 lan3 lan4:wan' 'label:02:11:22:33:44:50')
[ "$actual" = "$expected" ] || { printf 'Unexpected X30 defaults:\n%s\n' "$actual" >&2; exit 1; }
echo 'PASS: X30 port defaults and printed-label MAC source'

# Guard the existing multi-board case group beside the new X30 entry.
for TEST_BOARD in mercusys,mr90x-v1 tplink,archer-ax80-v1 tplink,archer-ax80-v1-eu tplink,re6000xd; do
	actual=$(. "$scratch/network")
	printf '%s\n' "$actual" | grep -Fx 'mac:lan:02:11:22:33:44:60' >/dev/null
	printf '%s\n' "$actual" | grep -Fx 'label:02:11:22:33:44:60' >/dev/null
done
echo 'PASS: neighboring Mercusys and TP-Link MAC defaults are preserved'
