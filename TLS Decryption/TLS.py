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

cli_handshake_mesg = b''
serv_handshake_mesg = b''
# unpacket client packets
while  content1:
	# one byte for contentType
	content_type = content1[0]
	# two bytes for ProtocolVersion ,{3,3} means TLS1.2
	protocol_version = (content1[1]<<8)+content1[2]
	# two bytes for length of packets
	length = (content1[3]<<8)+content1[4]
	# contents of length
	fragment = content1[5:5+length]
	# 22 means handshake
	if(content_type == 0x16):
		print("Get one fragment for client: ",len(fragment))
		cli_handshake_mesg += fragment
	else:
		print("content_type : " ,content_type)
	content1 = content1[5+length:]

while content2:
	# one byte for contentType
	content_type = content2[0]
	# two bytes for ProtocolVersion ,{3,3} means TLS1.2
	protocol_version = (content2[1]<<8)+content2[2]
	# two bytes for length of packets
	length = (content2[3]<<8)+content2[4]
	# contents of length
	fragment = content2[5:5+length]
	# 22 means handshake
	if(content_type == 0x16):
		print("Get one fragment for server: ",len(fragment))
		serv_handshake_mesg += fragment
	else:
		print("content_type : " ,content_type)
	content2 = content2[5+length:]

# one byte for handshake type
# three bytes for handshake length
# two bytes for ProtocolVersion
# 1+3+2 = 6
cli_random = cli_handshake_mesg[6:38]
serv_random = serv_handshake_mesg[6:38]
serv_handshake_mesg = serv_handshake_mesg[38:]
cli_handshake_mesg = cli_handshake_mesg[38:]
print("cli_random : ",cli_random.hex())
print("serv_random : ",serv_random.hex())

# def output():
# 	f1 = open('test1/out1', 'wb')
# 	f1.write(b'Hello world')
# 	f1.close()
# 	f2 = open('test1/out1', 'wb')
# 	f2.write(b'Hello world')
# 	f2.close()
