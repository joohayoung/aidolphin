#제한시간내에 입력을 안하면 넘어가는 input함수

import sys, time, msvcrt

def readInput(default, timeout = 5):

    start_time = time.time()
    input = ''
    while True:
        if msvcrt.kbhit():
            byte_arr = msvcrt.getche()
            if ord(byte_arr) == 13: # enter_key
                break
            elif ord(byte_arr) >= 32: #space_char
                input += "".join(map(chr,byte_arr))
            # else :
            #     input += map(chr,byte_arr)
        if len(input) == 0 and (time.time() - start_time) > timeout:
#           print("timing out, using default value.")
            break

#    print('')  # needed to move to next line
    # print("입력값 : ", input)
    if len(input) > 0:
        return input
    else:
        return default
