#!/bin/sh
# Exercise dispatch with stubs only: no image is read or flashed.
set -eu

platform="${1:?Usage: sh tests/test-x30-fit-upgrade.sh OPENWRT_TREE}/target/linux/mediatek/filogic/base-files/lib/upgrade/platform.sh"
sh -n "$platform"

board_name() { printf '%s\n' "$TEST_BOARD"; }
fit_do_upgrade() { printf 'fit-upgrade:%s\n' "$1"; }
fit_check_image() {
	printf 'fit-check:%s\n' "$1"
	return "$FIT_CHECK_STATUS"
}
nand_do_upgrade() { printf 'nand-upgrade:%s\n' "$1"; }
nand_do_platform_check() { printf 'nand-check:%s:%s\n' "$1" "$2"; }

# shellcheck source=/dev/null
. "$platform"

image='firmware with spaces.bin'
FIT_CHECK_STATUS=0
for TEST_BOARD in totolink,X30 totolink,x30; do
	[ "$(platform_do_upgrade "$image")" = "fit-upgrade:$image" ]
	[ "$(platform_check_image "$image")" = "fit-check:$image" ]

	# A rejected FIT image must remain rejected by the platform wrapper.
	FIT_CHECK_STATUS=17
	if platform_check_image "$image" >/dev/null; then
		echo "ERROR: $TEST_BOARD accepted a rejected FIT image" >&2
		exit 1
	else
		[ "$?" -eq 17 ]
	fi
	FIT_CHECK_STATUS=0
	if platform_check_image "$image" extra >/dev/null; then
		echo "ERROR: $TEST_BOARD accepted multiple images" >&2
		exit 1
	fi
	echo "PASS: $TEST_BOARD uses FIT upgrade and preserves image-check failures"
done

# Existing FIT devices and the generic NAND fallback must keep their routing.
TEST_BOARD=bananapi,bpi-r3
[ "$(platform_do_upgrade "$image")" = "fit-upgrade:$image" ]
[ "$(platform_check_image "$image")" = "fit-check:$image" ]
TEST_BOARD=test,unknown
[ "$(platform_do_upgrade "$image")" = "nand-upgrade:$image" ]
[ "$(platform_check_image "$image")" = "nand-check:$TEST_BOARD:$image" ]
echo 'PASS: existing FIT and generic NAND dispatch are unchanged'
