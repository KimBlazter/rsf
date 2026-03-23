PROCHE_AVG_SNR = 12 # SNR for close users
LOIN_AVG_SNR = 4 # SNR for far users
BUFFER_SIZE = 50000 # max bits each we can store to send to each users (if more bits comes in they will be discarded)
BITS_PER_SNR_POINT = 80 # when allocatin a UR, how much bits do we remove from buffer per SNR point
MAX_UR = 640 # 128 * 5 # how much UR are available each tick