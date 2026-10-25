// SPDX-License-Identifier: GPL-2.0-only
/* Test-only hardware doubles for the hosted X30 recovery-flow check. */
#include <command.h>
#include <env.h>
#include <os.h>
#include <stdio.h>
#include <linux/string.h>

static unsigned int transfers;
static unsigned int boots;

static int test_button(struct cmd_tbl *cmdtp, int flag, int argc,
		       char *const argv[])
{
	if (argc != 2 || strcmp(argv[1], "reset"))
		os_exit(90);
	return env_get_ulong("x30_test_reset", 10, 0) ? 0 : 1;
}

static int test_led(struct cmd_tbl *cmdtp, int flag, int argc,
		    char *const argv[])
{
	return 0;
}

static int test_tftp(struct cmd_tbl *cmdtp, int flag, int argc,
		     char *const argv[])
{
	if (argc != 3 || strcmp(argv[2],
		"openwrt-mediatek-filogic-totolink_x30-initramfs-recovery.bin"))
		os_exit(91);
	transfers++;
	printf("X30_TRANSFER_%u\n", transfers);
	return transfers <= env_get_ulong("x30_test_tftp_failures", 10, 0);
}

static int test_bootm(struct cmd_tbl *cmdtp, int flag, int argc,
		      char *const argv[])
{
	if (argc != 2 || !strstr(argv[1], "#config-1"))
		os_exit(92);
	boots++;
	printf("X30_IMAGE_CHECK_%u\n", boots);
	if (boots <= env_get_ulong("x30_test_bootm_failures", 10, 0))
		return 1;
	puts("X30_RAM_BOOT_OK\n");
	os_exit(0);
	return 0;
}

static int deny_storage(struct cmd_tbl *cmdtp, int flag, int argc,
			char *const argv[])
{
	printf("X30_FORBIDDEN_ACTION_%s\n", argv[0]);
	os_exit(99);
	return 1;
}

static int test_done(struct cmd_tbl *cmdtp, int flag, int argc,
		     char *const argv[])
{
	puts("X30_NORMAL_BOOT_ALLOWED\n");
	os_exit(0);
	return 0;
}

U_BOOT_CMD(button, 2, 1, test_button, "test-only reset input", "");
U_BOOT_CMD(led, 4, 1, test_led, "test-only indicator", "");
U_BOOT_CMD(tftpboot, 3, 1, test_tftp, "test-only transfer", "");
U_BOOT_CMD(bootm, 2, 1, test_bootm, "test-only RAM handoff", "");
U_BOOT_CMD(ubi, 16, 1, deny_storage, "forbidden in recovery test", "");
U_BOOT_CMD(mtd, 16, 1, deny_storage, "forbidden in recovery test", "");
U_BOOT_CMD(saveenv, 1, 1, deny_storage, "forbidden in recovery test", "");
U_BOOT_CMD(bootmenu, 2, 1, deny_storage, "unexpected menu during preboot", "");
U_BOOT_CMD(reset, 1, 1, deny_storage, "unexpected reset", "");
U_BOOT_CMD(x30_done, 1, 1, test_done, "test-only normal handoff", "");
