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
  passwd = '12@4'
  a[0x904:len(passwd)+0x904] = [ord(x) for x in passwd]
  t1 = [0x904]#,0x905,0x906,0x907]
  
  raw_input('go?')
  idx = 5
  flag = 0
  s = ''
  fp = file('log_insno.txt','ab')
  n = 0
  kl = []
  while 1:
    if idx+3 > 0x2dad:
      break
    idx_s = '{:04X}'.format(idx)
    if idx_s not in kl:
      kl.append(idx_s)
#    print idx,a[idx],a[idx+1],a[idx+2]
#    if  a[idx] in t1 or a[idx+1] in t1 or n:
#      txt = '{:04x}\t{:04x}\t{:04x}\t{:04x}\t{:04x}\t{:04x}\t{:04x}\r\n'.format(idx,a[idx],a[idx+1],a[idx+2],a[a[idx]],a[a[idx+1]],(a[a[idx+1]] -  a[a[idx]])&0xffff)
#      fp.write(txt)
#      print a[0x904:0x910]
#      n += 1
#      n %= 20000


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
#    if 'password...' in s:
#      fp.write(struct.pack('H',a[idx])+struct.pack('H',a[idx+1])+struct.pack('H',a[idx+2]))
  fp.write('\r\n'.join(kl))
  fp.close()
  
  print s
  print 'end.'

if __name__ == '__main__':
  main()