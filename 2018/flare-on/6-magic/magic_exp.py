#!/usr/bin/env python

from pwn import *
import string
import itertools

table = [0x0, 0x77073096, 0xee0e612c, 0x990951ba, 0x76dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
        0xedb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x9b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
        0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7, 
        0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5, 
        0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b, 
        0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59, 
        0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f, 
        0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d, 
        0x76dc4190, 0x1db7106, 0x98d220bc, 0xefd5102a, 0x71b18589, 0x6b6b51f, 0x9fbfe4a5, 0xe8b8d433, 
        0x7807c9a2, 0xf00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x86d3d2d, 0x91646c97, 0xe6635c01, 
        0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457, 
        0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65, 
        0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb, 
        0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9, 
        0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f, 
        0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad, 
        0xedb88320, 0x9abfb3b6, 0x3b6e20c, 0x74b1d29a, 0xead54739, 0x9dd277af, 0x4db2615, 0x73dc1683, 
        0xe3630b12, 0x94643b84, 0xd6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0xa00ae27, 0x7d079eb1, 
        0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7, 
        0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc, 0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
        0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b, 
        0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79, 
        0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f, 
        0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d, 
        0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x26d930a, 0x9c0906a9, 0xeb0e363f, 0x72076785, 0x5005713, 
        0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0xcb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0xbdbdf21, 
        0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777, 
        0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45, 
        0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db, 
        0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9, 
        0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf, 
        0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d]
table_b = p64(0x2346A7C2645F392A)+p64(0x42704D2847746B53)+p64(0x4A4038626A522549)+p64(0x5024312D59444569)+p64(0x6671764C21547967)+p64(0x304F57516D68632B)+p64(0x6C336E75345A4E65)+p64(0x4B7A617732264837)+p64(0x56)


def fac():
    l = []
    v1 = 0
    v2 = 1
    v3 = 0
    for i in range(0x80):
        v3 = v1+v2
        v1 = v2
        v2 = v3
        l.append(v3&0xffffffffffffffff)
    return l

def crc32(str,length,crchash = 0):
    crchash = ~crchash&0xffffffff
    for i in range(length):
        crchash = table[(crchash^ord(str[i]))&0xff] ^ (crchash >> 8)
    return (~crchash&0xffffffff)

def KSA(key):
    keylength = len(key)

    S = range(256)

    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % keylength]) % 256
        S[i], S[j] = S[j], S[i]  # swap

    return S

def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]  # swap

        K = S[(S[i] + S[j]) % 256]
        yield K

def RC4(key):
    S = KSA(key)
    return PRGA(S)

def debase(msg):  

    bs = ''
    for j in msg:    
        num = table_b.find(j)
        bs += '{:0>6b}'.format(num)        
    l = []
    c = ''
    for j in xrange(0,len(bs),8):
        c += chr(int(bs[j:j+8],2))
    
    return c.replace('\x00','')
'''
1: 0,6,13,15,17,27            a+13 == b
2: 1,7,20,21,24,28,31         fac(a)&0xfffffffffffffff == b
3: 2,10,11,12,16,18,22,26     a^0x2a == b
4: 3,5                        rc4(a) == b  key:Tis but a scratch.
5: 4,9,14,19,23,29            a == b
6: 8,32                       crc32(a) == b
7: 25,30                      enbase(a) == b
'''
def op1(c,d):
  s = ''
  for i in range(c):
    s += chr(ord(d[i])-13)
  return s

def op2(c,d):
  s = ''
  for i in range(c):
    s += chr(table_f.index(u64(d[8*i:8*(i+1)]))+1)
  return s

def op3(c,d):
  s = ''
  for i in range(c):
    s += chr(ord(d[i])^0x2a)
  return s
def op4(c,d):
  s = ''
  key = 'Tis but a scratch.'
  key = [ord(i) for i in key]
  keystream = RC4(key)
  for i in range(c):
    s += chr(ord(d[i]) ^ keystream.next())
  return s

def op5(c,d):
  return d

def op6(c,d):
  table = [chr(i) for i in range(0x20,0x7f)]   
  for x in itertools.product(table, repeat=c):
    if crc32(x,c) == u32(d):
      return ''.join(x)

def op7(c,d):
  return debase(d)

def readdata(filename,size,offset=0):
    fp = open(filename,'rb')
    fp.seek( offset , 0)
    data = fp.read(size)
    fp.close()
    return data

def pwn():
    func_l = [0x400bc6L, 0x400c55L, 0x400d9cL, 0x400e20L, 0x40111eL, 0x40119aL, 0x401498L, 0x401527L, 0x40166eL, 0x401721L, 0x40179dL, 0x401821L, 0x4018a5L, 0x401929L, 0x4019b8L, 0x401a34L, 0x401ac3L, 0x401b47L, 0x401bd6L, 0x401c5aL, 0x401cd6L, 0x401e1dL, 0x401f64L, 0x401fe8L, 0x402064L, 0x4021abL, 0x4024d1L, 0x402555L, 0x4025e4L, 0x40272bL, 0x4027a7L, 0x402acdL, 0x402c14L]
    op_l = [[0,6,13,15,17,27],[1,7,20,21,24,28,31],[2,10,11,12,16,18,22,26],[3,5],[4,9,14,19,23,29],[8,32],[25,30]]
    off_l = [0x8f,0x147,0x84,0x2fe,0x7c,0xb3,0x326]
    op_func_l = [op1,op2,op3,op4,op5,op6,op7]    
    mt = 0
    mt_t = 0
    for round in range(666):      
      # io.stdout.readline()
      # io.communicate()
      while mt == mt_t:
        sleep(0.5)        
        mt_t = os.stat('./magic').st_mtime
      mt = mt_t
      data = readdata('./magic',0x2520,0x5100)  
      # print data[:20].encode('hex')    
      func_addr = []
      xor_length = []
      idx_in = []
      count = []
      idx_out = []
      data_t = []
      for i in xrange(33):
          func_addr.append(u64(data[0x120*i:0x120*i+8]))
          xor_length.append(u32(data[0x120*i+8:0x120*i+12]))
          idx_in.append(u32(data[0x120*i+12:0x120*i+16]))
          count.append(u32(data[0x120*i+16:0x120*i+20]))
          idx_out.append(u32(data[0x120*i+20:0x120*i+24]))
          data_t.append(data[0x120*i+32:0x120*(i+1)])
      key = ['\x00' for t in xrange(69) ]
      for i in xrange(33):
          j = off_l.index(xor_length[i])          
          if j == 0 or j == 2 or j == 3 or j == 4:
            tmp = count[i]
          elif j == 1:
            tmp  = count[i]*8
          elif j == 5:
            tmp = 4
          else:                  
            if count[i]%3:
              tmp = (count[i]/3+1)*4 -(3- count[i]%3)
            else:
              tmp = count[i]/3*4
          res = op_func_l[j](count[i],data_t[i][:tmp])
          # print '%d:%d:%d:%s:%s'%(i,j,count[i],res,res.encode('hex'))
          key[idx_in[i]:idx_in[i]+count[i]] = list(res)
                  
                  
      passwd = ''.join(key)
      io.sendline(passwd)
      # io.stdin.write(passwd)
      # io.communicate()
      log.success('round:%d/666\tkey:%s'%(round+1,passwd))
      # io.recvuntil('Enter key: ')
      # sleep(10)
      

   
    io.interactive()


if __name__  ==  '__main__':
    context(arch='amd64', kernel='amd64', os='linux')
    # libc = ELF('./libc.so.6') 
    if 0:
        e = {'LD_PRELOAD':'./libc6.so'}   
    else:
        e = None
 
    io = process('./magic') 
    # io = subprocess.Popen('./magic',shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE) 
    # io = remote('127.0.0.1',9999)      
    # context.log_level = 'debug'        
    table_f = fac()         
    pwn()



