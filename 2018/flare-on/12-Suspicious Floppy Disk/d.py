# -*- coding:utf-8 -*-
import struct

def main():
  fp = open('tmp.dat','rb')
  fp.seek(0x266)
  data = fp.read(0x2dad*2)
  fp.close()
  a = []

  for i in range(0x2dad):
    a.append(struct.unpack('H',data[2*i:2*(i+1)])[0])
  passwd = '1@34'
  a[0x904:len(passwd)+0x904] = [ord(x) for x in passwd]
  t1 = [0x904,0x905,0x906,0x907]

  raw_input('go?')
  idx = 5
  flag = 0
  s = ''
  ins = {}
#  fp = file('log6','ab')
  while 1:
    if idx+3 > 0x2dad:
      break
    key = '{:04x}'.format(idx)
    if  key in ins.keys():
      ins[key] += 1
    else:
      ins[key] = 1
#    print idx,a[idx],a[idx+1],a[idx+2]
#    if  a[idx] in t1 or a[idx+1] in t1:
#      print idx,a[idx],a[idx+1],a[idx+2]
#      print a[0x904:0x910]


    tmp = (a[a[idx+1]] -  a[a[idx]])&0xffff
    a[a[idx+1]] = tmp

    if a[idx+2] and (tmp == 0 or tmp>=0x8000):     
        flag = 1
    else:
      flag = 0
    if flag:
      tmp = a[idx+2]
      if tmp == 0xffff:
        break
      else:
        idx = tmp
    else:
      idx += 3
    if a[4]:
      c = chr(a[2])
      s += c
#      print c
      a[2] = 0
      a[4] = 0
      if s[-3:] == '...':
        print ins
#    if 'password...' in s:
#      fp.write(struct.pack('H',a[idx])+struct.pack('H',a[idx+1])+struct.pack('H',a[idx+2]))

#  fp.close()
  print ins
  print s
  print 'end.'

if __name__ == '__main__':
  main()