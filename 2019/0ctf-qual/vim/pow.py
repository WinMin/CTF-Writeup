from pwn import *
import hashlib
io = remote('111.186.63.13',10001)


io.readuntil('sha256(XXXX+')

pad = io.readuntil(')')[:-1]
print pad
sha = io.readuntil(' == ').strip()
sha = io.readline()
print sha


for i in xrange(0xff):
    for j in xrange(0xff):
        for a in xrange(0xff):
            for b in xrange(0xff):
                sha256 = hashlib.sha256(chr(i)+chr(j)+chr(a)+chr(b)+pad).hexdigest()
                if sha256 == sha:
                    print(chr(i)+chr(j)+chr(a)+chr(b))
                    break 
                