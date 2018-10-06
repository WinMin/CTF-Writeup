
import string
hash = [0xfc7f, 0xF30F, 0xF361, 0xF151, 0xF886, 0xF3D1, 0xDB57, 0xD9D5,0xE26E, 0xF8CD, 0xF969, 0xD90C, 0xF821, 0xF181, 0xF85F, 0xF883]
#0xd15e
#Av0cad0_Love_2018@flare-on.com
str = string.letters+string.digits+'_@.-'
table = [ord(x)-0x20 for x in str]

r = [[] for i in range(16)]
n = []
for i in xrange(15):
  for x in table:
    for y in table:
      d = x*0x80+y    
      d = d^(0x20*i+i)
      r[i].append((hash[i]-d)&0xffff)
print 'guess param2 is :',
for i in r[0]:
  flag = True
  for j in xrange(1,15):
    if i not in r[j]:
      flag = False
      break
  if flag:
    n.append(i)
    print '0x{:04X}'.format(i),
    
print 
#10 0xD15E, 0xD05E, 0xCFDE, 0xCF5E
#15 0xD15E, 0xD05E, 0xCF5E
#n = [0xD15E, 0xD05E, 0xCF5E]
for i in n:
  s = ['' for c in xrange(15)]
  for j in xrange(15):
    for x in table:
      for y in table:
        d = ((x*0x80+y)^(0x21*j))+i
        if d == hash[j]:
          s[j] += (chr(y+0x20))
          s[j] += (chr(x+0x20))  
  print 'maybe  flag is:'+''.join(s)



  
  