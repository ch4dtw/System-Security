import scipy.io
import numpy
import time

TRACE_PATH = './20160304/20160304-0001'
PLAIN_TEXT_PATH = './20160304/log20160304-0001.txt'
LOG = "LOG.txt"
TRACE_NAME = 'A'

CS_TIME = time.time()
BYTE_AMOUNT = 16
KEY_AMOUNT = 256 #00~FF
DATA_AMOUNT = 5
TRACE_AMOUNT = 100004
traceList = []
plainTextList = []
junk = ""
SBOX = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
print_KEY = ""
log_KEY = ""

def getY(plainText,nByte,key):
    x = plainText[nByte*2:nByte*2+2]
    return SBOX[ int(x,16) ^ key ]

def hammingWeight(input):
    count = 0
    if(input & 0x80):
        count += 1
    if (input & 0x40):
        count += 1
    if (input & 0x20):
        count += 1
    if (input & 0x10):
        count += 1
    if (input & 0x08):
        count += 1
    if (input & 0x04):
        count += 1
    if (input & 0x02):
        count += 1
    if (input & 0x01):
        count += 1
    return count


for i in range(DATA_AMOUNT):
    fileName= '%s%s_%04d' % (TRACE_PATH, TRACE_PATH[len(TRACE_PATH)-14:], i+1)
    traceList.append( scipy.io.loadmat(fileName) )

plainTextFile = open(PLAIN_TEXT_PATH, 'r')
for i in range(DATA_AMOUNT):
    dataTemp = plainTextFile.readline()
    plainTextList.append( dataTemp[len(dataTemp)-33:len(dataTemp)-1] )
    junk = plainTextFile.readline()

S_time = time.time()


v_List = [[[0] * KEY_AMOUNT] * DATA_AMOUNT] * BYTE_AMOUNT  # v_List[nByte][第n筆][key]
h_List = [[[0] * KEY_AMOUNT] * DATA_AMOUNT] * BYTE_AMOUNT  # h_List[nByte][第n筆][key]
t_List = [[0] * ( TRACE_AMOUNT // 5 )] * DATA_AMOUNT # t_List[第n筆][Trace的第幾個點點]
r_List = [[[0.0] * ( TRACE_AMOUNT // 5)] * KEY_AMOUNT] * BYTE_AMOUNT # r_List[nByte][key][trace]

x_bar = [[0.0] * KEY_AMOUNT] * BYTE_AMOUNT # x_bar[nByte][key]
x_square_bar = [[0.0] * KEY_AMOUNT] * BYTE_AMOUNT # x_square_bar[nByte][key]
y_bar = [0.0] * ( TRACE_AMOUNT // 5 ) # y_bar[Trace的第幾個點點]
y_square_bar = [0.0] * ( TRACE_AMOUNT // 5 ) # y_square_bar[Trace的第幾個點點]

for i in range(DATA_AMOUNT):
    for nByte in range(BYTE_AMOUNT):
        for key in range(KEY_AMOUNT):
            v_List[nByte][i][key] = getY(plainTextList[i],nByte,key)
            h_List[nByte][i][key] = hammingWeight( v_List[nByte][i][key] )
            x_bar[nByte][key] += ( h_List[nByte][i][key] - x_bar[nByte][key] ) / (i+1)
            x_square_bar[nByte][key] += ( (h_List[nByte][i][key])**2 - x_square_bar[nByte][key]) / (i+1)

for i in range(DATA_AMOUNT):
    for trace in range(TRACE_AMOUNT // 5):
        t_List[i][trace] = traceList[i][TRACE_NAME][trace * 5][0]
        y_bar[trace] += ( t_List[i][trace] - y_bar[trace]) / (i+1)
        y_square_bar += ( t_List[i][trace]**2 - y_square_bar[trace]) / (i+1)

sum = 0.0
max = [0.0,0] * BYTE_AMOUNT
for nByte in range(BYTE_AMOUNT):
    for key in range(KEY_AMOUNT):
        for trace in range (TRACE_AMOUNT // 5):
            for i in range (DATA_AMOUNT):
                sum += h_List[nByte][i][key] * t_List[i][trace]
            r_List[nByte][key][trace] = ( sum - DATA_AMOUNT * x_bar[nByte][key] * y_bar[nByte] ) / ( ( ( x_square_bar[nByte][key] - ( x_bar[nByte][key] )**2  ) * ( y_square_bar[trace] - ( y_bar[trace] ) **2  ) ) ** (0.5) )
            if(r_List[nByte][key][trace] > max[0] ):
                max[nByte * 2 + 0] = r_List[nByte][key][trace]
                max[nByte * 2 + 1] = key

    log_KEY += ("%02x" % max[nByte * 2 + 1]).upper()
    print_KEY += ("%02x " % max[nByte * 2 + 1]).upper()

print(str(i)+': ',print_KEY)

E_time = time.time()
f = open(LOG, "a")
f.write("round " + str(i) + ": KEY = " + log_KEY + ",")
f.write("Cost time = " + str(E_time - S_time) + '\n')
f.close()

log_KEY = ""
print_KEY = ""