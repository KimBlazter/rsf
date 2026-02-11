from buffer import Buffer
from packet import Packet, PacketGenerator

class User:
    def __init__(self, id, avgSNR):
        self.id = id
        self.buffer:Buffer = Buffer(1000)  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR

    def consume_packet(self, packet):
        self.buffer.pop(packet)  # Consume the packet from the buffer
