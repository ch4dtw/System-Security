import sys
import binascii
def B2I(b):
    assert type(b) is bytes
    return int.from_bytes(b, byteorder='big')

def I2B(i, length):
    assert type(i) is int
    assert type(length) is int and length >= 0
    return int.to_bytes(i, length, byteorder='big')

def HMAC_SHA256(key, msg):
    import hmac
    return hmac.new(key, msg, 'sha256').digest()

def SYSTEM(command, stdin=None):
    from subprocess import Popen, PIPE
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate(stdin)
    return stdout, stderr, proc.returncode

def RSA_DECRYPT(skfilename, ciphertext):
    assert type(skfilename) is str
    assert type(ciphertext) is bytes
    stdout, stderr, retcode = SYSTEM((
        'openssl', 'rsautl', '-decrypt', '-inkey', skfilename
    ), ciphertext)
    assert retcode == 0 and stderr == b''
    return stdout

def TLS_PRF(secret, label, seed, n_bytes):
    assert type(secret) is bytes
    assert type(label) is bytes
    assert type(seed) is bytes
    assert type(n_bytes) is int and n_bytes >= 0
    last_A = label + seed
    result = b''
    while len(result) < n_bytes:
        last_A = HMAC_SHA256(secret, last_A)
        result += HMAC_SHA256(secret, last_A + label + seed)
    return result[:n_bytes]

def AES128CBC_DECRYPT(secret_key, ini_vector, ciphertext):
    assert type(secret_key) is bytes and len(secret_key) == 16
    assert type(ini_vector) is bytes and len(ini_vector) == 16
    assert type(ciphertext) is bytes and len(ciphertext) % 16 == 0
    stdout, stderr, retcode = SYSTEM((
        'openssl', 'enc', '-aes-128-cbc', '-d', '-nopad',
        '-K', ''.join('%02x'%x for x in secret_key),
        '-iv', ''.join('%02x'%x for x in ini_vector)
    ), ciphertext)
    assert retcode == 0 and stderr == b''
    return stdout
    
    
def main():
	in1,in2,in3,out1,out2 = sys.argv[1:]
	f1 = open(in1,'rb')
	f2 = open(in2,'rb')
	o1 = open(out1,'w')
	o2 = open(out2,'w')
	
	content1 = content3 = f1.read()
	content2 = content4 = f2.read()

	f1.close()
	f2.close()
	#content1 : client-to-server
	#content2 : server-to-client
	
	###########################################################
	
	handshake_msgs_result = b''
	while len(content1) > 0:
		typ, ver1, ver2, len1, len2 = content1[:5]
		length = (len1*256) + len2
		fragmt = content1[5:5+length]
		tail   = content1[5+length:]
		#print('found one recoured with length = ',length)	
		if typ == 22:
			handshake_msgs_result += fragmt
		content1 = tail

	cli_random = handshake_msgs_result[6:6+32]
	print(binascii.hexlify(cli_random))

	###########################################################
	
	shandshake_msgs_result = b''
	while len(content2) > 0:
		typ, ver1, ver2, len1, len2 = content2[:5]
		length = (len1*256) + len2
		fragmt = content2[5:5+length]
		tail   = content2[5+length:]	
		if typ == 22:
			shandshake_msgs_result += fragmt
		content2 = tail	
	ser_random = shandshake_msgs_result[6:32+6]
	print(binascii.hexlify(ser_random))
	###########################################################

	encrypted_pre_master_secret = handshake_msgs_result[292:292+256]
	print(binascii.hexlify(encrypted_pre_master_secret))
	
	###########################################################
	
	pre_master_secret = RSA_DECRYPT(in3,encrypted_pre_master_secret)
	print(binascii.hexlify(pre_master_secret))


	###########################################################
	a = b'master secret'
	b = b'key expansion'
	master_secret = TLS_PRF(pre_master_secret,a,cli_random+ser_random,48)
	print(binascii.hexlify(master_secret))
	
	result_master_secret = TLS_PRF(master_secret,b,ser_random+cli_random,104)
	client_write_MAC_key = result_master_secret[:20]
	server_write_MAC_key = result_master_secret[20:40]
	client_write_key = result_master_secret[40:56]
	server_write_key = result_master_secret[56:72]
	client_write_iv = result_master_secret[72:88]
	server_write_iv = result_master_secret[88:104]
	print(binascii.hexlify(client_write_key))
	print(binascii.hexlify(server_write_key))
	
	###########################################################

	ApplicationData = b''
	while len(content3) > 0:
		typ, ver1, ver2, len1, len2 = content3[:5]
		length = (len1*256) + len2
		fragmt = content3[5:5+length]
		tail   = content3[5+length:]	
		if typ == 23:
			ApplicationData += fragmt
		content3 = tail
	#print(binascii.hexlify(ApplicationData))

	final_result = AES128CBC_DECRYPT(client_write_key, client_write_iv, ApplicationData)
	strfinal_result = str(final_result[16:90])
	o1.write(strfinal_result)
	o1.close()
	#print(len(final_result))
	#print(binascii.hexlify(final_result))
	###########################################################
	sApplicationData = b''
	while len(content4) > 0:
		typ, ver1, ver2, len1, len2 = content4[:5]
		length = (len1*256) + len2
		fragmt = content4[5:5+length]
		tail   = content4[5+length:]	
		if typ == 23:
			sApplicationData += fragmt
		content4 = tail
	#print(binascii.hexlify(sApplicationData))

	sfinal_result = AES128CBC_DECRYPT(server_write_key, server_write_iv, sApplicationData)
	sstrfinal_result = str(sfinal_result)
	
	o2.write(sstrfinal_result)
	o2.close()
	print(len(sfinal_result))
	print(binascii.hexlify(sfinal_result))
	
	
	
	
	
	
main()

              
