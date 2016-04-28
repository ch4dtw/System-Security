import scipy.io
import numpy
import time

TRACE_PATH = './20160320'
PLAIN_TEXT_PATH = './20160320/log0320.txt'
LOG = "NEW_LOG_useCC.txt"
TRACE_NAME = 'trace'

BYTE_AMOUNT = 16  # 16
KEY_AMOUNT = 256  # 00~FF
DATA_AMOUNT = 10000  # 1000*10
TRACE_AMOUNT = 48031

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


trace_sum = numpy.zeros((TRACE_AMOUNT, 1), dtype=float)
trace_square_sum = numpy.zeros((TRACE_AMOUNT, 1), dtype=float)
h_sum = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT), dtype=int)
h_square_sum = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT), dtype=int)
h_times_t_sum = numpy.zeros((BYTE_AMOUNT, KEY_AMOUNT, TRACE_AMOUNT, 1), dtype=float)

start_time = time.time()
plainTextFile = open(PLAIN_TEXT_PATH, 'r')

for i in range(DATA_AMOUNT):

    log_key = ''
    print_key = ''

    fileName = '%s%s-%04d_%04d' % (TRACE_PATH, TRACE_PATH[len(TRACE_PATH) - 9:], (i / 1000) + 1, (i % 1000) + 1)
    trace_now = scipy.io.loadmat(fileName)[TRACE_NAME]
    trace_sum += trace_now
    trace_square_sum += (trace_now * trace_now)
    Lyy = trace_square_sum - ((trace_sum ** 2) / (i + 1))

    dataTemp = plainTextFile.readline()
    plainText = dataTemp[len(dataTemp) - 33:len(dataTemp) - 1]
    junk = plainTextFile.readline()

    for nByte in range(BYTE_AMOUNT):

        maxCC = 0.0
        maxKey = 0

        for key in range(KEY_AMOUNT):

            h_now = hammingWeight(getY(plainText, nByte, key))
            h_sum[nByte][key] += h_now
            h_square_sum[nByte][key] += (h_now * h_now)
            h_times_t_sum[nByte][key] += h_now * trace_now

            Lxx = h_square_sum[nByte][key] - ((h_sum[nByte][key] ** 2) / (i + 1))

            cc_fractions = h_times_t_sum[nByte][key] - ((h_sum[nByte][key] * trace_sum) / (i + 1))  # 分子
            cc_numerator = (Lxx * Lyy) ** 0.5  # 分母
            cc = cc_fractions / cc_numerator
            cc[numpy.isnan(cc)] = 0

            if cc.max() > maxCC:
                maxCC = cc.max()
                maxKey = key

        log_key += ("%02X" % maxKey)
        print_key += ("%02X " % maxKey)

    print(str(i) + ': ', print_key)

    end_time = time.time()
    f = open(LOG, "a")
    f.write("round " + str(i) + ": KEY = " + log_key + ",")
    f.write("Cost time = " + str(end_time - start_time) + '\n')
    f.close()
