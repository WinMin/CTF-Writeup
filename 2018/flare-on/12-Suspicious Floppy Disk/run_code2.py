
import struct
fp = open('tmp_ori.dat','rb')
tmp = fp.read(0x2dad*2)
fp.close()      
data = list(struct.unpack('11693H',tmp[:0x2dad*2]))
data[0x904:0x904+33] = [ord(x) for x in 'Av0cad0_Love_2018@flare-on.com123']
data[0xf5] = 0x25b7
data[0xf6] = 0x7f6
data[0xf7] = 0xeb
data[0xfb] = 0xf8
data[0xff] = 0xf8
data[0x10f] = 0x7f6 #var_010F
data[0x148] = 0x25b7
data[0x1ad] = 0x15b  #[0x7f6] = 0x15b off  var_01AD
#data[0x7f6] = 0xb4b-0x7f6
#data[0x94f] = 0x154
base = 0x7f6
off = 0x15b
end = 0x25b7
#fp = file('rssb_ins_final','w')
while True:
  off = data[0x7f6]
  addr = base+off
  ins = data[addr]
  
#  if addr == 0xb4b:
#    data[0x949] = 1
#    text = '{:04X}: {:04X} {:04X} {:04X} {:04X} {:04X} {:04X} {:04X}\n'.format(0x948,data[0x948],data[0x949],data[0x94a],data[0x94b],data[0x94c],data[0x94d],data[0x94e])
#    print text
#  if addr == 0x2cde:
#    data[0x136e] = 1
  if off >= end or ins == 0xfffe: 
#    fp.close()
    exit()  
  
  if ins == 0xffff:
    data[0x7f6] += 1  #off+1
  else:
#   if base+ins >= 0x904:
    text = '{:04X}: {:04X} {:04X} {:04X} {:04X} {:04X}\n'.format(addr,ins,base+ins,data[base+ins],data[0x7f7],(data[base+ins]- data[0x7f7])&0xffff )
#    fp.write(text)
#   print text
    tmp = (data[base+ins]- data[0x7f7])&0xffff 
    data[0x7f7] = tmp
    if ins != 2:  #0x7f8 => Z 
      data[base+ins] = tmp
    if tmp & 0x8000:
      data[0x7f6] += 1   #skip
    data[0x7f6] += 1
  tmp = data[0x7fc] #flag output
  if tmp == 1:    #0x7fa--4  0x7fb--5  0x7fc--6  
    data[0x7fc] = 0   
    data[2]  = data[0x7fa]    
    print chr(data[2]),
    data[4] = 1
    data[0x7fa] = 0 
  tmp = data[0x7fb]
  if tmp == 1:
    data[0x7fb] = 0
    data[3] = 1
    data[0x7f9] = data[1]





