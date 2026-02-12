from buffer import Buffer
from packet import Packet, PacketGenerator
import sys

class User:
    def __init__(self, id, avgSNR):
        self.id = id
        self.buffer:Buffer = Buffer(1000)  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR

    def _add_packet(self, packet: Packet) -> None:
        self.buffer.push(packet)
    
    def add_packets(self, packets: list[Packet]) -> None:
        map(self._add_packet, packets)
    
    def allocate_bits(self, bits: int) -> None:
        self.buffer.pop(bits)

DUMMY_USER = User(-1, sys.maxsize)