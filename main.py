import scipy.io
import numpy
import time

TRACE_PATH = './20160304/20160304-0001'
PLAIN_TEXT_PATH = './20160304/log20160304-0001.txt'
TRACE_PATH_2 = './20160304/20160304-0002'
PLAIN_TEXT_PATH_2 = './20160304/log20160304-0002.txt'
LOG = "LOG.txt"
TRACE_NAME = 'A'

CS_TIME = time.time()
BYTE_AMOUNT = 16 # 0~15
KEY_AMOUNT = 256 # 00~FF
DATA_AMOUNT = 2500*2 # old is 2500
TRACE_AMOUNT = 100004
traceList = []
plainTextList = []
junk = ""
SBOX = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125,
        250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204,
        52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226,
        235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132,
        83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251,
        67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245,
        188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61,
        100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219,
        224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109,
        141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198,
        232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185,
        134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223,
        140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
print_KEY = ""
log_KEY = ""

def getY( plainText, nByte, key ):
    x = plainText[nByte*2:nByte*2+2]
    return SBOX[ int(x,16) ^ key ]

for i in range(DATA_AMOUNT//2):
    fileName= '%s%s_%04d' % ( TRACE_PATH, TRACE_PATH[len( TRACE_PATH )-14:], i+1 )
    traceList.append( scipy.io.loadmat( fileName ) )
for i in range(DATA_AMOUNT//2):
    fileName = '%s%s_%04d' % ( TRACE_PATH_2, TRACE_PATH_2[len( TRACE_PATH_2 ) - 14:], i + 1 )
    traceList.append( scipy.io.loadmat( fileName ) )


plainTextFile = open(PLAIN_TEXT_PATH, 'r')
for i in range( DATA_AMOUNT//2 ):
    dataTemp = plainTextFile.readline()
    plainTextList.append( dataTemp[len( dataTemp )-33:len( dataTemp )-1] )
    junk = plainTextFile.readline()
plainTextFile.close()

plainTextFile2 = open(PLAIN_TEXT_PATH_2, 'r')
for i in range( DATA_AMOUNT//2 ):
    dataTemp = plainTextFile2.readline()
    plainTextList.append( dataTemp[len( dataTemp )-33:len( dataTemp )-1] )
    junk = plainTextFile2.readline()
plainTextFile2.close()




LSB0_Count = [0.0]*KEY_AMOUNT*BYTE_AMOUNT
LSB1_Count = [0.0]*KEY_AMOUNT*BYTE_AMOUNT
LSB0_Avg = [0.0]*KEY_AMOUNT*BYTE_AMOUNT
LSB1_Avg = [0.0]*KEY_AMOUNT*BYTE_AMOUNT
SUB_LSB1Avg_LSB0Avg = [0.0]*KEY_AMOUNT*BYTE_AMOUNT
keyTemp = [0.0]*KEY_AMOUNT*BYTE_AMOUNT

S_time = time.time()

for i in range( DATA_AMOUNT ):
    for nByte in range( BYTE_AMOUNT ):
        for key in range( KEY_AMOUNT ):
            if getY(plainTextList[i], nByte, key) % 2 == 0:
                LSB0_Avg[key + KEY_AMOUNT*nByte] += (
                (traceList[i][TRACE_NAME] - LSB0_Avg[key + KEY_AMOUNT*nByte]) / (LSB0_Count[key + KEY_AMOUNT*nByte] + 1) )
                LSB0_Count[key + KEY_AMOUNT*nByte] += 1
            else:
                LSB1_Avg[key + KEY_AMOUNT*nByte] += (
                (traceList[i][TRACE_NAME] - LSB1_Avg[key + KEY_AMOUNT*nByte]) / (LSB1_Count[key + KEY_AMOUNT*nByte] + 1) )
                LSB1_Count[key + KEY_AMOUNT*nByte] += 1
            SUB_LSB1Avg_LSB0Avg[key + KEY_AMOUNT*nByte] = LSB0_Avg[key + KEY_AMOUNT*nByte] - LSB1_Avg[
                key + KEY_AMOUNT*nByte]

        for key in range( KEY_AMOUNT ):
            keyTemp[key + nByte * KEY_AMOUNT] = numpy.amax(abs(SUB_LSB1Avg_LSB0Avg[key + nByte * KEY_AMOUNT]), axis=0)


        max = [0.0, 0] * BYTE_AMOUNT
        for key in range( KEY_AMOUNT ):
            if (keyTemp[key + nByte * KEY_AMOUNT][0] > max[0]):
                max[0] = keyTemp[key + nByte * KEY_AMOUNT][0]
                max[1] = key

        log_KEY += ("%02X" % max[1])
        print_KEY += ("%02X " %max[1])

    print(str(i)+': ',print_KEY)

    E_time = time.time()
    f = open(LOG, "a")
    f.write("round " + str(i) + ": KEY = " + log_KEY + ",")
    f.write("Cost time = " + str(E_time - S_time) + '\n')
    f.close()

    log_KEY = ""
    print_KEY = ""

