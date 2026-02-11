from buffer import Buffer
from packet import Packet, PacketGenerator
import sys

class User:
    def __init__(self, id, avgSNR):
        self.id = id
        self.buffer:Buffer = Buffer(1000)  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR

    def consume_packet(self, packet):
        self.buffer.pop(packet)  # Consume the packet from the buffer

DUMMY_USER = User(-1, sys.maxsize)