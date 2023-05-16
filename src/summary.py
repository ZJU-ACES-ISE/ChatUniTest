data = [
    ["toInt(String, int)", 21, 23, 24, 75],
    ["toLong(String, long)", 20, 20, 21, 31],
    ["toFloat(String, float)", 20, 22, 21, 25],
    ["toDouble(String, double)", 20, 20, 21, 26],
    ["toByte(String, byte)", 20, 23, 23, 25],
    ["toShort(String, short)", 20, 22, 23, 25],
    ["createFloat(String)", 20, 20, 21, 23],
    ["createDouble(String)", 20, 21, 21, 23],
    ["createInteger(String)", 20, 21, 0, 23],
    ["createLong(String)", 20, 21, 23, 21],
    ["createBigInteger(String)", 28, 20, 28, 39],
    ["createBigDecimal(String)", 22, 22, 22, 34],
    ["min(long[])", 27, 22, 22, 37],
    ["min(int, int, int)", 22, 22, 25, 23],
    ["max(float[])", 27, 22, 23, 33],
    ["max(byte, byte, byte)", 23, 22, 22, 25],
    ["isDigits(String)", 20, 23, 23, 26],
    ["isNumber(String)", 44, 51, 33, 76]
]

EVOSUITE = 0
ATHENATEST = 0
A3TEST = 0
TESTGPT = 0

for row in data:
    EVOSUITE += row[1]
    ATHENATEST += row[2]
    A3TEST += row[3]
    TESTGPT += row[4]

print(EVOSUITE, ATHENATEST, A3TEST, TESTGPT)
print("{:.1%}".format(EVOSUITE / 375))
print("{:.1%}".format(ATHENATEST / 375))
print("{:.1%}".format(A3TEST / 375))
print("{:.1%}".format(TESTGPT / 375))
print("TestGPT outperform EVOSUITE                      ", "{:.2%}".format(((TESTGPT - EVOSUITE) / EVOSUITE)))
print("TestGPT outperform ATHENATEST                    ", "{:.2%}".format(((TESTGPT - ATHENATEST) / ATHENATEST)))
print("TestGPT outperform A3TEST                        ", "{:.2%}".format(((TESTGPT - A3TEST) / A3TEST)))
print("ATHENATEST = A3TEST with 0 deleted               ", "{:.2%}".format(((A3TEST + 21 - ATHENATEST) / ATHENATEST)))
print("TestGPT outperform ATHENATEST with 0 deleted     ", "{:.2%}".format(((TESTGPT - 23 - A3TEST) / A3TEST)))
