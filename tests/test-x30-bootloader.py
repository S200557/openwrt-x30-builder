#!/usr/bin/env python3
"""Exercise the real X30 environment in hosted U-Boot; never contact hardware.

Only the hardware input, LED, TFTP and kernel handoff are doubled. UBI, MTD,
environment saves and unexpected menu/reset actions terminate the test.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tarfile
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('openwrt', type=Path)
parser.add_argument('--workdir', type=Path)
parser.add_argument('--reuse-build', action='store_true')
args = parser.parse_args()
openwrt = args.openwrt.resolve()
package = (openwrt/'package/boot/uboot-mediatek/Makefile').read_text()
version = re.search(r'^PKG_VERSION:=(\S+)',package,re.M)[1]
digest = re.search(r'^PKG_HASH:=(\S+)',package,re.M)[1]
archive = openwrt/'dl'/('u-boot-'+version+'.tar.bz2')
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
patch = openwrt/'package/boot/uboot-mediatek/patches/505-add-totolink-x30.patch'
work = (args.workdir or Path(tempfile.mkdtemp(prefix='x30-uboot-recovery-'))).resolve()
source = work/('u-boot-'+version)
inputs = {'archive_sha256':digest,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),
    'stubs_sha256':hashlib.sha256(Path(__file__).with_name('x30-bootloader-stubs.c').read_bytes()).hexdigest()}
receipt = work/'inputs.json'
if args.reuse_build:
    assert receipt.exists() and json.loads(receipt.read_text()) == inputs, 'Sandbox inputs changed; use a new work directory.'
if not args.reuse_build:
    work.mkdir(parents=True,exist_ok=True)
    assert not source.exists(), 'Preserve an existing sandbox; use --reuse-build after inspection.'
    with tarfile.open(archive,'r:bz2') as tar:
        tar.extractall(work,filter='data')
    subprocess.run(['patch','-p1','-i',str(patch)],cwd=source,check=True)
    stub = Path(__file__).with_name('x30-bootloader-stubs.c').read_bytes()
    (source/'cmd/x30_recovery_test.c').write_bytes(stub)
    # reset is registered unconditionally; keep its implementation available
    # under a different test-only name and route 'reset' to the fail-closed stub.
    boot = source/'cmd/boot.c'
    text = boot.read_text()
    assert text.count('reset, 2, 0,\tdo_reset') == 1
    boot.write_text(text.replace('reset, 2, 0,\tdo_reset','sandbox_original_reset, 2, 0,\tdo_reset'))
    with (source/'cmd/Makefile').open('a') as output:
        output.write('\nobj-y += x30_recovery_test.o\n')
    subprocess.run(['make','sandbox_defconfig'],cwd=source,check=True)
    receipt.write_text(json.dumps(inputs,indent=2)+'\n')
disable = ['CMD_NET','NET','CMD_LED','CMD_BUTTON','CMD_MTD','CMD_MTDPARTS',
    'CMD_UBI','CMD_SAVEENV','CMD_BOOTM','CMD_BOOTMENU','CMD_BOOTD',
    'UNIT_TEST','CMD_UPL','LTO','SANDBOX_SDL','VIDEO','EFI_LOADER','TOOLS_MKEFICAPSULE',
    'BINMAN','PYLIBFDT','ENV_IS_IN_FAT','ENV_IS_IN_EXT4','ENV_IS_IN_SPI_FLASH']
command = ['scripts/config']
for option in disable:
    command.extend(['--disable',option])
command.extend(['--enable','ENV_IS_NOWHERE','--enable','HUSH_PARSER'])
subprocess.run(command,cwd=source,check=True)
subprocess.run(['make','olddefconfig'],cwd=source,check=True)
subprocess.run(['make','-j2','u-boot','u-boot.dtb'],cwd=source,check=True)

defconfig = (source/'configs/mt7981_totolink_x30_defconfig').read_text()
assert 'CONFIG_USE_PREBOOT=y' in defconfig.splitlines()
environment = source/'defenvs/totolink_x30_env'
values = dict(line.split('=',1) for line in environment.read_text().splitlines() if line and not line.startswith('#'))
assert values['preboot'] == 'run boot_reset'
assert 'boot_tftp_recovery' not in values['boot_tftp_forever']
pending, seen = ['preboot'], set()
while pending:
    name = pending.pop()
    if name in seen:
        continue
    seen.add(name)
    script = values[name]
    assert not re.search(r'\b(?:saveenv|ubi|mtd)\b|\benv\s+save\b',script), 'Storage access reachable from preboot: '+name
    for match in re.finditer(r'\brun\s+([^\s;]+)',script):
        callee = match[1]
        assert re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',callee) and callee in values, 'Unresolved recovery dispatch'
        pending.append(callee)

cases = [
    ('normal boot',0,0,0,False,0,0),
    ('reset RAM boot',1,0,0,False,1,1),
    ('reset ignores stale NAND-write controls',1,0,0,True,1,1),
    ('retry failed transfer and rejected image',1,2,1,True,4,2),
]
for name,pressed,tftp_fail,boot_fail,stale,transfers,boots in cases:
    command = 'host load hostfs - 100000 '+shlex.quote(str(environment))+'; env import -t 100000 ${filesize}; '
    command += f'setenv x30_test_reset {pressed}; setenv x30_test_tftp_failures {tftp_fail}; setenv x30_test_bootm_failures {boot_fail}; '
    if stale:
        command += 'setenv replacevol 1; setenv noboot 1; '
    command += 'run preboot; x30_done'
    result = subprocess.run([str(source/'u-boot'),'-d',str(source/'u-boot.dtb'),'-c',command],cwd=source,capture_output=True,timeout=20)
    output = result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace')
    (work/(re.sub('[^a-z0-9]+','-',name.lower())+'.log')).write_text(output)
    assert result.returncode == 0, output[-3000:]
    assert 'X30_FORBIDDEN_ACTION' not in output, output
    assert len(re.findall(r'X30_TRANSFER_\d+',output)) == transfers, output
    assert len(re.findall(r'X30_IMAGE_CHECK_\d+',output)) == boots, output
    assert ('X30_RAM_BOOT_OK' in output) == bool(pressed), output
    assert ('X30_NORMAL_BOOT_ALLOWED' in output) == (not pressed), output
    print('PASS: '+name,flush=True)
print('PASS: hosted recovery flow never accesses NAND or saves the environment; hardware remains untested.',flush=True)
