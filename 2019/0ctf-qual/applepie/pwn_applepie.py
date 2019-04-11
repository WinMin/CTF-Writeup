from pwn import *

io = process('./applepie')


ru = lambda x : io.recvuntil(x)
sn = lambda x : io.send(x)
rl = lambda : io.recvline()
sl = lambda x : io.sendline(x)
rv = lambda x : io.recv(x)
sa = lambda a,b : io.sendafter(a,b)
sla = lambda a,b : io.sendlineafter(a,b)



def add(Style,Shape,Size,Name):
    sla('Choice:','1')
    sla('Choice:',str(Style))
    sla('Choice:',str(Shape))
    sla('Size:',str(Size))
    sla('Name:',str(Name))

def show(Idx):
    sla('Choice:','2')
    sla('Index:',str(Idx))

def update(Idx):
    sla('Choice:','3')
    sla('Index:',str(Idx))
    sla('Choice:',str(Style))
    sla('Choice:',str(Shape))


def delete(Idx):
    sla('Choice:','4')
    sla('Index:',str(Idx))

"""
======Style======        ======Shape======
 1. Dutch                   1. Circle
 2. English                 2. Star
 3. French                  3. Heart
 4. Swedish                 4. Square
 5. American                5. Triangle
"""


for i in xrange(3):
    add('1','1',0x100,'AAAAAAAA')

pause()