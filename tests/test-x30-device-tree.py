#!/usr/bin/env python3
"""Check the compiled hardware description against observed X30 hardware."""
import struct
import sys
from pathlib import Path


def parse_dtb(path):
    data = Path(path).read_bytes()
    magic, total, start, strings_start, _, version, _, _, strings_size, size = struct.unpack_from('>10I', data)
    assert magic == 0xd00dfeed and version >= 17 and total <= len(data)
    assert start + size <= total and strings_start + strings_size <= total
    strings = data[strings_start:strings_start + strings_size]
    cursor, stack, nodes = start, [], {}
    while cursor < start + size:
        token, = struct.unpack_from('>I', data, cursor)
        cursor += 4
        if token == 1:
            end = data.index(0, cursor)
            stack.append(data[cursor:end].decode())
            nodes['/'.join(stack) or '/'] = {}
            cursor = (end + 4) & ~3
        elif token == 2:
            stack.pop()
        elif token == 3:
            length, offset = struct.unpack_from('>II', data, cursor)
            cursor += 8
            name = strings[offset:strings.index(0, offset)].decode()
            nodes['/'.join(stack) or '/'][name] = data[cursor:cursor + length]
            cursor = (cursor + length + 3) & ~3
        elif token == 4:
            pass
        elif token == 9:
            assert not stack
            return nodes
        else:
            raise AssertionError(f'Invalid FDT token {token}')
    raise AssertionError('FDT end marker missing')


def cells(value):
    assert len(value) % 4 == 0
    return struct.unpack('>' + 'I' * (len(value) // 4), value)


def strings(value):
    return value.rstrip(b'\0').decode().split('\0')


def main(path):
    nodes = parse_dtb(path)
    assert strings(nodes['/']['compatible'])[0] == 'totolink,x30'
    assert cells(nodes['/memory@40000000']['reg']) == (0, 0x40000000, 0, 0x10000000)
    phandles = {cells(p['phandle'])[0]: p for p in nodes.values() if 'phandle' in p}
    led_parent = next(p for p, v in nodes.items() if v.get('compatible') == b'gpio-leds\0')
    leds = [v for p, v in nodes.items() if p.startswith(led_parent + '/') and 'gpios' in v]
    by_function = {strings(v.get('function', b''))[0]: v for v in leds}
    assert cells(by_function['wlan-2ghz']['gpios'])[1:] == (34, 1)
    assert cells(by_function['wlan-5ghz']['gpios'])[1:] == (35, 1)
    assert by_function['wlan-2ghz']['linux,default-trigger'] == b'phy0tpt\0'
    assert by_function['wlan-5ghz']['linux,default-trigger'] == b'phy1tpt\0'
    assert cells(by_function['cpu']['gpios'])[1:] == (15, 1)
    assert 'usb' not in by_function
    for name in ('led-boot', 'led-failsafe', 'led-running', 'led-upgrade'):
        assert nodes[strings(nodes['/aliases'][name])[0]] == by_function['cpu']
    assert 'label-mac-device' not in nodes['/aliases']
    wifi_path, wifi = next((p, v) for p, v in nodes.items() if p.rsplit('/', 1)[-1].startswith('wifi@'))
    assert wifi['status'] == b'okay\0' and wifi['nvmem-cell-names'] == b'eeprom\0'
    assert cells(phandles[cells(wifi['nvmem-cells'])[0]]['reg']) == (0, 0x1000)
    for name, props in nodes.items():
        if name.startswith(wifi_path + '/band@'):
            assert 'nvmem-cells' not in props and 'mac-address' not in props
        if any('xhci' in c or 'mt7981-usb-phy' in c for c in strings(props.get('compatible', b''))):
            assert props.get('status') == b'disabled\0', f'Unexpected enabled USB: {name}'
    for name, increment in [('mac@0', 3), ('mac@1', 1)]:
        mac = next(v for p, v in nodes.items() if p.endswith('/' + name) and v.get('compatible') == b'mediatek,eth-mac\0')
        reference, actual = cells(mac['nvmem-cells'])
        assert actual == increment and cells(phandles[reference]['reg']) == (4, 6)
    partitions = {strings(v['label'])[0]: v for v in nodes.values() if 'label' in v and 'reg' in v and strings(v['label'])[0] in ('bl2', 'u-boot-env', 'factory', 'fip', 'ubi')}
    expected = {'bl2': (0, 0x100000), 'u-boot-env': (0x100000, 0x80000), 'factory': (0x180000, 0x200000), 'fip': (0x380000, 0x200000), 'ubi': (0x580000, 0x7a80000)}
    assert {k: cells(v['reg']) for k, v in partitions.items()} == expected
    assert all('read-only' in partitions[k] for k in ('bl2', 'factory', 'fip'))
    assert any(v.get('volname') == b'fit\0' for v in nodes.values())
    print('PASS: compiled X30 indicators, EEPROM MAC sources, disabled USB and preserved flash layout')


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage: python3 tests/test-x30-device-tree.py DEVICE.dtb'
    main(sys.argv[1])
