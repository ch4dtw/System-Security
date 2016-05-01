from decoder import *

content1=b''
content2=b''
secret_key=b''

handshake_typelist = {0:'hello_request'\
					,1:'client_hello'\
					,2:'server_hello'\
					,11:'certificate'\
					,12:'server_key_exchange'\
					,13:'certificate_request'\
					,14:'server_hello_done'\
					,15:'certificate_verify'\
					,16:'client_key_exchange'\
					,20:'finished'\
					,255:'Hello world'\
					}
content_typelist = {	20:'change_cipher_spec'\
					, 21:'alert'\
					, 22:'handshake'\
					, 23:'application_data'\
					, 255 :'Hello world'\
					}

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
		print("Get \"", content_typelist[content_type],"\" fragment to server: ",len(fragment))
		cli_handshake_mesg += fragment
	else:
		print("content_type : \"" ,content_typelist[content_type],"\" to server not decoding yet")
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
		print("Get \"", content_typelist[content_type],"\" fragment to client: ",len(fragment))
		serv_handshake_mesg += fragment
	else:
		print("content_type : \"" ,content_typelist[content_type],"\" to client not decoding yet")
	content2 = content2[5+length:]

# one byte for handshake type
# three bytes for handshake length
# two bytes for ProtocolVersion
# 1+3+2 = 6
print("client packet type is : ", handshake_typelist[cli_handshake_mesg[0]])
cli_random = cli_handshake_mesg[6:38]
# four bytes for gmt_unix_time
# twenty-eight bytes for random bytes
# 4+28
cli_handshake_mesg = cli_handshake_mesg[38:]
print("cli_random : ",cli_random.hex())

print("server packet type is : ", handshake_typelist[serv_handshake_mesg[0]])
serv_random = serv_handshake_mesg[6:38]
serv_handshake_mesg = serv_handshake_mesg[38:]
print("serv_random : ",serv_random.hex())


# def output():
# 	f1 = open('test1/out1', 'wb')
# 	f1.write(b'Hello world')
# 	f1.close()
# 	f2 = open('test1/out1', 'wb')
# 	f2.write(b'Hello world')
# 	f2.close()
