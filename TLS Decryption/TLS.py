from decoder import *
import sys

content1=b''
content2=b''
encrypted_pre_master_secret = b''
pre_master_secret = b''
master_secret=b''
cli_key = b''
serv_key = b''
######################################################
# message list
cli_handshake_mesg = b''
cli_hello = b''
cli_key_exchange = b''
cli_change_cipher_spec = b''
cli_finished = b''
cli_application_data = []
cli_alert = b''
cli_result = b''
cli_write_MAC_key = b''
cli_write_key = b''
cli_write_iv = b''

serv_handshake_mesg = b''
serv_hello = b''
serv_certificate = b''
serv_hello_done = b''
serv_change_cipher_spec = b''
serv_finished = b''
serv_application_data = []
serv_alert = b''
serv_result = b''
serv_write_MAC_key = b''
serv_write_key = b''
serv_write_iv = b''
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
#in1,in2,in3,out1,out2 = sys.argv[1:]
folder = sys.argv[1]
in1, in2, in3, out1, out2 = folder+"in1" ,folder+"in2" ,folder+"in3" ,folder+"out1" ,folder+"out2"
#read from in1 in2
f1 = open(in1, 'rb')
f2 = open(in2, 'rb')
content1 = f1.read()
content2 = f2.read()
f1.close()
f2.close()

#################################################
# split fragment from client
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
		cli_change_cipher_spec += fragment
	elif content_type == 0x15:
		cli_alert += fragment
	elif content_type == 0x16:
		if fragment[0] == 0x01:
			print("\"",handshake_typelist[fragment[0]],"\"")
			cli_hello += fragment
		elif fragment[0] == 0x10:
			print("\"",handshake_typelist[fragment[0]],"\"")
			cli_key_exchange += fragment
		else:
			cli_finished += fragment
	elif content_type == 0x17:
		cli_application_data.append(fragment)
	else :
		print("Unknown content type")
	content1 = content1[5+length:]
#################################################
# split fragment from server
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
	if content_type == 0x14:
		serv_change_cipher_spec += fragment
	elif content_type == 0x15:
		serv_alert += fragment
	elif content_type == 0x16:
		if fragment[0] == 0x02:
			print("\"",handshake_typelist[fragment[0]],"\"")
			serv_hello += fragment
		elif fragment[0] == 0x0B:
			print("\"",handshake_typelist[fragment[0]],"\"")
			serv_certificate += fragment
		elif fragment[0] == 0x0E:
			print("\"",handshake_typelist[fragment[0]],"\"")
			serv_hello_done += fragment
		else:
			serv_finished += fragment
	elif content_type == 0x17:
		serv_application_data.append(fragment)
	else :
		print("Unknown content type")
	content2 = content2[5+length:]

#################################################
# get client and server's random

# 1 byte for handshake type
# 3 bytes for handshake length
# 2 bytes for ProtocolVersion
# 1+3+2 = 6
# random nubmer--
# 4 bytes for gmt_unix_time
# 28 bytes for random bytes
# 4+28 = 32
cli_random = cli_hello[6:38]
print("cli_random : ",cli_random.hex())

#1 byte + session_id's length <0...32>
#2 byte + cipher_suites's length <2..2^16-2>
#if not null
#2 byte + extensions<0..2^16-1>

serv_random = serv_hello[6:38]
print("serv_random : ",serv_random.hex())

#################################################
# get secret key

# 1 byte for handshake type
# 3 bytes for handshake length
# 2 bytes for ProtocolVersion
# 1+3+2 = 6
encrypted_pre_master_secret = cli_key_exchange[6:]
print("encrypted_pre_master_secret : ",encrypted_pre_master_secret.hex())

# RSA decrypt with server secret key
pre_master_secret = RSA_DECRYPT(in3,encrypted_pre_master_secret)
print("pre_master_secret : ", pre_master_secret.hex())

# secret, label, seed, n_bytes
master_secret = TLS_PRF(pre_master_secret ,b'master secret' ,cli_random+serv_random ,48)
print("master_secret : ", master_secret.hex())

result_master_secret = TLS_PRF(master_secret ,b'key expansion' ,serv_random+cli_random,104)
print("result_master_secret : ", result_master_secret.hex())

# 20 + 20 + 16 +16 + 16 + 16
cli_write_MAC_key = result_master_secret[:20]
serv_write_MAC_key = result_master_secret[20:40]
cli_write_key = result_master_secret[40:56]
serv_write_key = result_master_secret[56:72]
cli_write_iv = result_master_secret[72:88]
serv_write_iv = result_master_secret[88:104]
print("client_write_key : ",cli_write_key.hex())
print("server_write_key : ", serv_write_key.hex())
#################################################
# decrypt client data
# 
i = 0
while i < len(cli_application_data):
	# decrypt
	temp = AES128CBC_DECRYPT(cli_write_key, cli_write_iv ,cli_application_data[i])
	# kill iv
	temp = temp[16:]
	# kill padding bytes
	temp = temp[:-temp[-1]-1]
	# kill checksum (MAC)
	temp = temp[:-20]
	# really content
	cli_result += temp
	i += 1
print("client_result : ",cli_result)
#################################################
#decrypt server data
i = 0
while i < len(serv_application_data):
	# decrypt
	temp = AES128CBC_DECRYPT(serv_write_key, serv_write_iv ,serv_application_data[i])
	# kill iv
	temp = temp[16:]
	# kill padding bytes
	temp = temp[:-temp[-1]-1]
	# kill checksum (MAC)
	temp = temp[:-20]
	# really content
	serv_result += temp
	i += 1
print("server_result : ",serv_result)
#################################################
# write file
#
f1 = open(out1, 'wb')
f1.write(cli_result)
f1.close()
f2 = open(out2, 'wb')
f2.write(serv_result)
f2.close()

print ("succeed")
