from decoder import *

content1=b''
content2=b''
secret_key=b''
######################################################
# message list
cli_handshake_mesg = b''
cli_hello = b''
cli_key_exchange = b''
cli_change_cipher_spec = b''
cli_finished = b''
cli_application_data = b''
cli_alert = b''

serv_handshake_mesg = b''
serv_hello = b''
serv_key_exchange = b''
serv_change_cipher_spec = b''
serv_finished = b''
serv_application_data = b''
serv_alert = b''
serv_certificate = b''
###########################################
#typelist
handshake_typelist = {
					0:'hello_request'\
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
content_typelist = {
					20:'change_cipher_spec'\
					, 21:'alert'\
					, 22:'handshake'\
					, 23:'application_data'\
					, 255 :'Hello world'\
					}
#################################################
#read from in1 in2
f1 = open('test1/in1', 'rb')
f2 = open('test1/in2', 'rb')
content1 = f1.read()
content2 = f2.read()
f1.close()
f2.close()

#################################################
# split fragment from client and server
turn = 1
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

	print("Get \"", content_typelist[content_type],"\" fragment to server: ",len(fragment))
	if content_type == 0x14:
		if turn == 3:
			cli_change_cipher_spec += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x16:
		if turn == 1 :
			cli_hello += fragment
		else :
			 print("fragment analyzed failed")
		if turn == 2:
			cli_key_exchange += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x17:
		if turn == 5:
			cli_application_data += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x20:
		if turn == 4:
			cli_finished += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x21:
		if turn == 6:
			cli_finished += fragment
		else :
			print("fragment analyzed failed")
	else :
		print("Unkonwn type")

		#print("content_type : \"" ,content_typelist[content_type],"\" to server not decoding yet")
	content1 = content1[5+length:]
	turn += 1

turn = 1
while content2:
	# one byte for contentType
	content_type = content2[0]
	# two bytes for ProtocolVersion ,{3,3} means TLS1.2
	protocol_version = (content2[1]<<8)+content2[2]
	# two bytes for length of packets
	length = (content2[3]<<8)+content2[4]
	# contents of length
	fragment = content2[5:5+length]
	print("Get \"", content_typelist[content_type],"\" fragment from server: ",len(fragment))
	if content_type == 0x11:
		if turn == 2:
			serv_change_cipher_spec += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x14:
		if turn == :
			serv_change_cipher_spec += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x16:
		print(turn)
		if turn == 1 :
			serv_hello += fragment
			print("yooooooooooooooooooo")
		else :
			 print("fragment analyzed failed")
		if turn == :
			serv_key_exchange += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x17:
		if turn == :
			serv_application_data += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x20:
		if turn == :
			serv_finished += fragment
		else :
			 print("fragment analyzed failed")
	elif content_type == 0x21:
		if turn == :
			serv_finished += fragment
		else :
			print("fragment analyzed failed")
	else :
		print("Unkonwn type")
	#else:

		#print("content_type : \"" ,content_typelist[content_type],"\" from server not decoding yet")
	content2 = content2[5+length:]
	turn += 1

#################################################
# get client and server's random

# one byte for handshake type
# three bytes for handshake length
# two bytes for ProtocolVersion
# 1+3+2 = 6
print("client packet type is : ", handshake_typelist[cli_hello[0]])
cli_random = cli_hello[6:38]
print("cli_random : ",cli_random.hex())

# four bytes for gmt_unix_time
# twenty-eight bytes for random bytes
# 4+28
#one byte + seession_id's length <0...32>
#two byte + cipher_suites's length <2..2^16-2>
#


print("server packet type is : ", handshake_typelist[serv_hello[0]])
serv_random = serv_hello[6:38]
print("serv_random : ",serv_random.hex())

#################################################


# def output():
# 	f1 = open('test1/out1', 'wb')
# 	f1.write(b'Hello world')
# 	f1.close()
# 	f2 = open('test1/out1', 'wb')
# 	f2.write(b'Hello world')
# 	f2.close()
