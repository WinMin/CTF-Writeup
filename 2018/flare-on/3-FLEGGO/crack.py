# -*- coding:utf-8 -*-
import os
import subprocess

def print_res():
  l1 = ['12268605.png','13147895.png','15566524.png','16295588.png','16544936.png','16785906.png','18309310.png','18376743.png','19343964.png','30171375.png','33098947.png','33662866.png','33718379.png','36494753.png','36870498.png','37723511.png','42255131.png','44958449.png','47202222.png','47619326.png','47893007.png','51227743.png','52817899.png','58770751.png','60075496.png','61006829.png','61333226.png','63223880.png','64915798.png','65141174.png','65626704.png','67322218.png','67782682.png','70037217.png','71290032.png','72263993.png','72501159.png','72562746.png','73903128.png','75072258.png','79545849.png','80333569.png','82100368.png','82236857.png','85934406.png','87730986.png','88763595.png','89295012.png']
  l2 = [33,23,41,6,24,16,36,21,43,9,13,40,45,10,48,17,14,5,20,30,29,39,44,47,25,38,37,22,4,7,12,18,1,11,19,15,46,42,34,3,32,2,27,8,35,26,28,31]
  l3 = ['65141174.png','85934406.png','67782682.png','75072258.png','16544936.png','67322218.png','58770751.png','64915798.png','88763595.png','18376743.png','36870498.png','72501159.png','47619326.png','70037217.png','18309310.png','15566524.png','82100368.png','60075496.png','71290032.png','33718379.png','42255131.png','16295588.png','61333226.png','13147895.png','16785906.png','80333569.png','37723511.png','44958449.png','30171375.png','72263993.png','82236857.png','33098947.png','33662866.png','47893007.png','61006829.png','89295012.png','87730986.png','65626704.png','72562746.png','36494753.png','79545849.png','63223880.png','51227743.png','73903128.png','52817899.png','19343964.png','12268605.png','47202222.png']
  l4 = ['w','m','m','r','e','_','o','3','e','_','m','c','p','m','@','e','m','s','a','.','t','a','f','w','4','o','n','_','s','h','e','_','r','_','l','0','0','3','-','0','s','a','a','u','n','o','s','n']
  s = ''
  for i in range(48):
    s += l4[l3.index(l1[l2.index(i+1)])]
#  mor3_awes0m3_th4n_an_awes0me_p0ssum@flare-on.com
  print s
def main():
  path = 'E:\\CTF\\flare-on\\2018\\3\\FLEGGO\\'
  fl = os.listdir(path)
  for f in fl:
    if f[-3:] == 'exe':
      fp = open(path+f,'rb')
      fp.seek( 0x2ab0 , 0)
      data = fp.read(0x20)
      fp.close()
#      print data.encode('hex')
      data = data.replace('\x00','')
#      print data
      p = subprocess.Popen(path+f,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
      p.stdin.write(data) 
#      p.wait()
      print p.communicate()
#      print p.stdout.readline()
if __name__ == '__main__':
  print_res()