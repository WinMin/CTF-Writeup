# -*- coding:utf-8 -*-
from base64 import b64decode
from Crypto.Cipher import ARC4 
import struct
from hashlib import md5

def d0(data,round):
  c = round
  s = ''
  for i in data:    
    s  += chr(ord(i)^(0x39 - 0x93 * c)&0xff)
    c = (0x3039 - 0x3E39B193 * c) & 0x7FFFFFFF
  return s

def d1(data,key,length,round):
  k_l =len(key)
  s = ''
  for i in range(length):
    t = (ord(key[i%k_l])+round*i)&0xff
    s  += chr(ord(data[i])^t)
  return s 

def d2(data,key,round):
  ci = ARC4.new(key)
  data_d1 = ci.decrypt(data)
  data_d2 = ''
  c = round&0xff
  d = c-1
  for i in data_d1:
    data_d2 += chr(ord(i)^c)
    c = (c+d)&0xff
  return data_d2




def main():

#decode base64 and rc4
#  data = file('base.bin','rb').read()
#  data_d1 = b64decode(data)
#  ci = ARC4.new('yummy')
#  data_d2 = ci.decrypt(data_d1)
#  with open('base_de.bin','wb') as fp:
#    fp.write(data_d2)

#decode  vbcode
#  f_d = file('vbcode.bin','rb')
#  key = file('key.bin','rb').read()  
#  f_t = file('table.bin','rb')
#  with open('vbcode_de.bin','ab') as fp:
#    for i in range(0x12a):
#      pos = struct.unpack('I',f_t.read(4))[0]
#      length = struct.unpack('I',f_t.read(4))[0]
#      print length
#      data = f_d.read(length)
#      if i%3 == 0:
#        data = d0(data,i)
#      elif i%3 == 1:
#        data = d1(data,key,length,i)
#      else:
#        data = d2(data,key,i)
#      fp.write(data)    

#decrypt flag
#  key = '5db857f15394bdf6b25bfabc8960449b'.decode('hex')
  key = 'ac3b790d7542158f08330d1fb293361f'.decode('hex')
  data_k = file('input.bin','rb').read()
  key = md5(data_k).digest()
  print 'md5:'+key.encode('hex')
  data = file('html.bin','rb').read()
  ci = ARC4.new(key)
  data_d = ci.decrypt(data)
  with open('html.html','wb') as fp:
    fp.write(data_d)
  print 'data:'+data_d
  print 'end.'

if __name__ == '__main__':
  main()