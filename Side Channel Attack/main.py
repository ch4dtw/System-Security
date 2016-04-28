import scipy.io
import numpy
import time

TRACE_PATH_1 = './20160304/20160304-0001'
PLAIN_TEXT_PATH_1 = './20160304/log20160304-0001.txt'
TRACE_PATH_2 = './20160304/20160304-0002'
PLAIN_TEXT_PATH_2 = './20160304/log20160304-0002.txt'
LOG = "LOG.txt"
TRACE_NAME = 'A'

BYTE_AMOUNT = 16  # 16
KEY_AMOUNT = 256  # 00~FF
DATA_AMOUNT = 2500 * 2  # 2500*2
TRACE_AMOUNT = 100004

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


def getY(plainText, nByte, key):
    x = plainText[nByte * 2:nByte * 2 + 2]
    return SBOX[int(x, 16) ^ key]


def hammingWeight(input):
    count = 0
    if input & 0x80:
        count += 1
    if input & 0x40:
        count += 1
    if input & 0x20:
        count += 1
    if input & 0x10:
        count += 1
    if input & 0x08:
        count += 1
    if input & 0x04:
        count += 1
    if input & 0x02:
        count += 1
    if input & 0x01:
        count += 1
    return count


lsb0_count = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT), dtype=int)
lsb1_count = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT), dtype=int)
lsb0_avg = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT, TRACE_AMOUNT, 1), dtype=float)
lsb1_avg = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT, TRACE_AMOUNT, 1), dtype=float)
sub_lsb1_lsb0 = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT, TRACE_AMOUNT, 1), dtype=float)

start_time = time.time()
plainTextFile1 = open(PLAIN_TEXT_PATH_1, 'r')
plainTextFile2 = open(PLAIN_TEXT_PATH_2, 'r')

for i in range(DATA_AMOUNT):

    log_key = ''
    print_key = ''

    if i // 2500 == 0:
        fileName = '%s%s_%04d' % (TRACE_PATH_1, TRACE_PATH_1[len(TRACE_PATH_1) - 14:], i + 1)
        trace_now = scipy.io.loadmat(fileName)[TRACE_NAME]

        dataTemp = plainTextFile1.readline()
        plainText = dataTemp[len(dataTemp) - 33:len(dataTemp) - 1]
        junk = plainTextFile1.readline()

    else:
        fileName = '%s%s_%04d' % (TRACE_PATH_2, TRACE_PATH_2[len(TRACE_PATH_2) - 14:], i + 1)
        trace_now = scipy.io.loadmat(fileName)[TRACE_NAME]

        dataTemp = plainTextFile2.readline()
        plainText = dataTemp[len(dataTemp) - 33:len(dataTemp) - 1]
        junk = plainTextFile2.readline()

    for nByte in range(BYTE_AMOUNT):

        maxPoint = 0.0
        maxKey = 0

        for key in range(KEY_AMOUNT):

            if getY(plainText, nByte, key) % 2 == 0:
                lsb0_count[nByte][key] += 1
                lsb0_avg[nByte][key] += ((trace_now - lsb0_avg[nByte][key]) / lsb0_count[nByte][key])
            else:
                lsb1_count[nByte][key] += 1
                lsb1_avg[nByte][key] += ((trace_now - lsb1_avg[nByte][key]) / lsb1_count[nByte][key])

            sub_lsb1_lsb0[nByte][key] = lsb1_avg[nByte][key] - lsb0_avg[nByte][key]
            pointTemp = numpy.amax(abs(sub_lsb1_lsb0[nByte][key]), axis=0)

            if pointTemp > maxPoint:
                maxPoint = pointTemp
                maxKey = key

        log_key += ("%02X" % maxKey)
        print_key += ("%02X " % maxKey)

    print(str(i) + ': ', print_key)

    end_time = time.time()
    f = open(LOG, "a")
    f.write("round " + str(i) + ": KEY = " + log_key + ",")
    f.write("Cost time = " + str(end_time - start_time) + '\n')
    f.close()
