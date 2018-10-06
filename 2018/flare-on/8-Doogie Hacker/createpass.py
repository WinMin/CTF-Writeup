# -*- coding:utf-8 -*-
import itertools
import string
def main():
  data = file('1.bin','rb').read()
  a = '\x19\x90\x02\x06'
#  a = '\x97\x41\x20\x60'
  
  st = '@flare-on.com'  
  l = []
  
  for i in range(len(data)):
    l.append(ord(data[i])^ord(a[i%4]))
#  l1 = '8'*17
#  s = ''
#  for j in xrange(len(data)):
#    s += chr(l[j]^ord(l1[j%17]))
#  print s
  
#  for i in range(1178-13):
#    l1 = []
#    s = ''
#    for j in xrange(13):
#      l1.append(ord(st[j])^l[i+j])
#    s = ''.join([ chr(x) for x in l1])
#    if len(s) == 13:
#      n1 = i%17
#      l1 += [0]*4
#      l1 = l1[-n1:]+l1[:-n1]
#      for j in xrange(len(data)):
#        s += chr(l[j]^l1[j%17])
#      print 'index:%d'%i,s
#      print 
    
    
    
    
#    for j in xrange(len(data)):
#      s += chr(ord(data[j])^ord(t[j%tl]))
#    print s
#  a = '\x99\x01\x20\x60'
#  b = 'aaaa@flare-on.com'
#  l = []
#  s = ''
#  for i in range(len(data)):
#    l.append(ord(data[i])^ord(a[i%4]))
#  t = string.digits+string.letters+'_'

#  it = itertools.permutations([x for x in range(0x100)],3)
#  count = 0
#  l = list(data)
#  for i in it:
#    for n in xrange(20):
#      s = ''
#      for j in xrange((len(data)-20)/4):
#        l[4*j+n] = chr(i[(4*j)%3]^ord(l[4*j+n]))
#        s += chr(tmp)
  #      if tmp >=0x20 and tmp < 0x7f:
  #        s += chr(tmp)
  #      else:
  #        break
  #    if len(s) > 200:
  #      print s,i
#      s = ''.join(l)
#      if '@fl' in s:
#        print s,i,n
#      count +=1
#      if count %5000000 == 0:
#        print count


  table1 = string.digits+string.letters+string.punctuation+'\r\n\t\x20'

#  table1 = string.printable+'\x00'
  ll = len(data)
  l2 = string.lowercase#change range
  l2 = [ord(x) for x in l2]
  n = 17
  lr = [[] for x in range(17)]
  for i in range(n):
    for j in l2:
      f = True
      for k in xrange(ll/n):
        if chr(l[n*k+i]^j) not in table1:
          f = False
          break
      if f:
        print '%d:%s %c %s %c'%(i,hex(j),chr(j),hex(l[i]^j),chr(l[i]^j))
        lr[i].append(j)
  print lr       
  
  it = itertools.product(*lr[4:])
  
  for i in it:
    print ''.join(chr(x) for x in i)
#  for i in it:
#    s = ''
#    for j in xrange(len(data)):
#      s += chr(l[j]^i[j%17])
#    with open('output','ab') as fp:
#      fp.write(s+'\r\n\r\n')
  print 'end'

if __name__ == '__main__':
  main()