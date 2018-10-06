# -*- coding:utf-8 -*-
import struct

class Subleq(object):
  def __init__(self,fn='',sfn='',action = 'init',idx = 5):
    if fn:
      self._file = fn
    else:
      self._file = 'tmp.dat'
    self._sfile = sfn
    self._action = action
    self._idx = idx
    self._flag = False
    self._end = True
    self._stop = False
    self._d1 = 0
    self._d2 = 0
    self._a1 = 0
    self._a2 = 0
    self._a3 = 0
    self._ouput = ''
    self._data = []
    self._ba_list = []
    self._bd_list = []
    self._bj_list = []
    self._bs = ''
    self._bc = ''
#    if action == 'init' and self._file != '':
#      self.load(self._file)
#    elif action == 'restore' and self._sfile != '':
#      self.restore(self._sfile)
  
  def load(self,*args):
    argc = len(args) 
    if argc > 0:
      self._file = args[0]
    if self._file:
      fp = open(self._file,'rb')
      fp.seek(0x266)
      data = fp.read(0x2dad*2)
      fp.close()      
      self._data = list(struct.unpack('11693H',data[:0x2dad*2]))
#      for i in range(0x2dad):
#        self._data.append(struct.unpack('H',data[2*i:2*(i+1)])[0])
      self._idx = 5
      self.get_curr()
      self._end = False
      self._stop = False
      self._output = ''
    else:
      print '[!]File name is None.need file name.'
        
  def restore(self,*args):
    argc = len(args) 
    if argc > 0:
      self._sfile = args[0]
    if self._sfile:
      data = open(self._sfile,'rb').read()       
      self._data = list(struct.unpack('11693H',data[:0x2dad*2]))
#      for i in range(0x2dad):
#        self._data.append(struct.unpack('H',data[2*i:2*(i+1)])[0])

      self._idx = struct.unpack('H',data[0x2dad*2:0x2dad*2+2])[0]
      self._flag = bool(ord(data[0x2dad*2+2]))
      self._output = data[0x2dad*2+3:]
      self.get_curr()
      self._end = False
      self._stop = False
    else:
      print '[!]r filename'
      
  
  def store(self,*args):
    argc = len(args) 
    if argc > 0:
      self._sfile = args[0]
    if self._sfile:
      with open(self._sfile,'wb') as fp:
        data = ''.join([struct.pack('H',x) for x in self._data])
        fp.write(data)
        fp.write(struct.pack('H',self._idx))
        fp.write(chr(int(self._flag)))
        fp.write(self._output)
    else:
      print '[!]s filename'
  
  def get_curr(self):
    self._a1 = self._data[self._idx]
    self._a2 = self._data[self._idx+1]
    self._a3 = self._data[self._idx+2]
    self._d1 = self._data[self._a1]
    self._d2 = self._data[self._a2]  
  
  def juge(self):
    tmp = (self._d2 - self._d1)&0xffff
    if self._a3 and (tmp == 0 or tmp>=0x8000):     
      flag = 1
    else:
      flag = 0
    return tmp,flag
  
  def check_bp(self):
    if self._idx in self._ba_list or self._a1 in self._bd_list or self._a2 in self._bd_list or (self._bs and self._bs in self._output) or self._a3 in self._bj_list:
      self._stop = True
    if self._bc and eval(self._bc):
      self._stop = True
      
  def run_once(self):
    if self._idx+3 > 0x2dad:
      self._end = True
      return
    self._data[self._a2],self._flag = self.juge()
    if self._flag:      
      if self._a3 == 0xffff:
        self._end = True
        return
      else:
        self._idx = self._a3
    else:
      self._idx += 3
    if self._data[4]:
      c = chr(self._data[2])
      print c,
      self._output += c
      self._data[2] = 0
      self._data[4] = 0
      
    self.get_curr()
    self.check_bp()      

  def modifly (self,*args):
    argc = len(args)    
    if argc < 2:
      print 'e addr data1 data2...'
      return
    else:
      addr = int(args[0],16)
      d = args[1:]
      self._data[addr:len(d)+addr] = [int(x,16) for x in d]
    
  def dump_data(self,*args):
    argc = len(args)    
    if argc == 0:
      print 'd addr [count]'
      return
    addr = int(args[0],16)
    if argc == 1:
      count = 10
    else:
      count = int(args[1],16)
    text = ''
    for i in range(count):
      text += '{:04X}:  {:04X} {:04X} {:04X} {:04X}  {:04X} {:04X} {:04X} {:04X}\r\n'.format(i*8+addr,self._data[i*8+addr],self._data[i*8+addr+1],self._data[i*8+addr+2],self._data[i*8+addr+3],self._data[i*8+addr+4],self._data[i*8+addr+5],self._data[i*8+addr+6],self._data[i*8+addr+7])
    print text

  def print_curr(self,*args):
    tmp,flag = self.juge()
    text = '{:04X}:  {:04X} {:04X} {:04X} \td1={:04X} d2={:04X} d2-d1={:04X}\r\n'.format(self._idx,self._a1,self._a2,self._a3,self._d1,self._d2,tmp)
    if flag:
      text += 'flag=True\t jmp to {:04X}\r\n'.format(self._a3)
      text += '{:04X}:  {:04X} {:04X} {:04X} \td1={:04X} d2={:04X} d2-d1={:04X}\r\n'.format(self._a3,self._data[self._a3],self._data[self._a3+1],self._data[self._a3+2],self._data[self._data[self._a3]],self._data[self._data[self._a3+1]],(self._data[self._data[self._a3+1]]-self._data[self._data[self._a3]])&0xffff)
    elif self._a3:
      text += 'flag=False no jmp'
    print text
  
  def print_ins(self,*args):
    return
    
  def set_bp(self,*args):
    argc = len(args) 
    if argc == 0:
      text = ''
      for i in self._ba_list:
        text += '{:04X} '.format(i)
      print 'address bp:'+text
      text = ''
      for i in self._bd_list:
        text += '{:04X} '.format(i)
      print 'data bp:'+text
      text = ''
      for i in self._bj_list:
        text += '{:04X} '.format(i)
      print 'jump bp:'+text
      print 'condition bp:'+self._bc
      print 'string bp:'+self._bs
    elif argc > 1:
      t = args[0]
      d = args[1:]
      if t == 'a':
        self._ba_list += [int(x,16) for x in d]
        print '[*]break point(s) set.'
      elif t == 'd':
        self._bd_list += [int(x,16) for x in d]
        print '[*]break point(s) set.'
      elif t == 'j':
        self._bj_list += [int(x,16) for x in d]
        print '[*]break point(s) set.'
      elif t == 'c':
        self._bc = d[0]
        print '[*]break point(s) set.'
      elif t == 's':
        self._bs = d[0]
        print '[*]break point(s) set.'
    else:
      print '[*]b [a|d|s|j] param1 param2...'    
    
  def clear_bp(self,*args):
    argc = len(args) 
    if argc == 1:
      if args[0] == 'a':
        self._ba_list = []
      elif args[0] == 'd':
        self._bd_list = []
      elif args[0] == 'j':
        self._bj_list = []
      elif args[0] == 'c':
        self._bc = ''
      elif args[0] == 's':
        self._bs = ''
    elif argc > 1:
      t = args[0]
      d = l[1:]
      if t == 'a':
        for i in d:
          if i in self._ba_list:
            self._ba_list.remove(i)
      elif t == 'd':
        for i in d:
          if i in self._bd_list:
            self._bd_list.remove(i)
      elif t == 'j':
        for i in d:
          if i in self._bj_list:
            self._bj_list.remove(i)
    else:
      print '[*]bc a|d|s|j [param1 param2...]'    
    return
    
  def step(self,*args):
    argc = len(args) 
    if argc == 0:
      n = 1
    else:
      n = int(args[0],16)
    for i in range(n):
      if not self._end :
        self.run_once()
        if self._stop:
          self._stop = False
          break
      else:
        print '[!]program end.'
        return
    print
    self.print_curr() 

  def go(self,*args):
    while True:
      if not self._end :
        self.run_once()
        if self._stop:
          self._stop = False
          break
      else:
        print '[!]program end.'
        return
    print
    self.print_curr()   
  def find_mem(self,*args):
    argc = len(args) 
    if argc == 1:
      n = int(args[0],16)
      idx = []
      tmp = 0
      while True:
        if n in self._data[tmp:]:
          tmp1 = self._data[tmp:].index(n)
          tmp += tmp1
          idx.append(tmp)
          tmp += 1
        else:
          break
      for i in idx:
        print '{:04X}'.format(i),
      print 
      
    
def execute(cmd,last_cmd,func_l,subleq):
  if cmd :
    input = cmd
  else:
    input = last_cmd 
  if input[0] == 'q':
    exit()
  if subleq._end and input[0] != 'l' and input[0] != 'r':
    print '[!]program end.please try load or restore'
    return
  l = input.split(' ')
  if l[0] in func_l.keys():
    func_l[l[0]](*l[1:])
  else:
    print '[!]error command'
  
def main(): 
  last_cmd = ''
  subleq = Subleq()
  func_l = {'d':subleq.dump_data,'i':subleq.print_curr,'t':subleq.step,'e':subleq.modifly,'u':subleq.print_ins,'s':subleq.store,'r':subleq.restore,'l':subleq.load,'b':subleq.set_bp,'bc':subleq.clear_bp,'g':subleq.go,'f':subleq.find_mem}
  while True:    
    cmd = raw_input('(dbg)$').strip()
    execute(cmd,last_cmd,func_l,subleq)
    if cmd:
      last_cmd = cmd

  print 'end.'

if __name__ == '__main__':
  main()