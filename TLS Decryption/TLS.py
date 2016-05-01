from decoder import *

content1=b''
content2=b''
secret_key=b''

f1 = open('test1/in1', 'rb')
f2 = open('test1/in2', 'rb')
content1 = f1.read()
content2 = f2.read()
f1.close()
f2.close()

mesg = b''
while  content1:
	contentType = content1[0]
	ProtocolVersion = (content1[1]<<8)+content1[2]
	length = (content1[3]<<8)+content1[4]
	fragment = content1[5:5+length]
	if(contentType == 0x16):
		print("Get one fragment : ",len(fragment))
		mesg += fragment
	content1 = content1[5+length:]

# def output():
# 	f1 = open('test1/out1', 'wb')
# 	f1.write(b'Hello world')
# 	f1.close()
# 	f2 = open('test1/out1', 'wb')
# 	f2.write(b'Hello world')
# 	f2.close()
