PROCHE_AVG_SNR = 12 # SNR for close users
LOIN_AVG_SNR = 4 # SNR for far users

LOW_RELAY_RATIO = 0.1
HIGH_RELAY_RATIO = 0.8

PDOR_THRESHOLD = 50

BITS_PER_SNR_POINT = 80 # when allocatin a UR, how much bits do we remove from buffer per SNR point
MAX_UR = 640 # 128 * 5 # how much UR are available each tick
PACKET_SIZE = 50

# (moySNR * bits per snr * nb ur) / bits per user per tick 