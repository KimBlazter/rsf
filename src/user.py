from buffer import Buffer
from constant import BUFFER_SIZE
from packet import Packet
import sys
from mesures import record_bits, record_delay

class User:
    def __init__(self, id, avgSNR):
        self.id = id
        self.buffer:Buffer = Buffer(BUFFER_SIZE)  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR

    def _add_packet(self, packet: Packet) -> None:
        self.buffer.push(packet)
            
    
    def add_packets(self, packets: list[Packet]) -> None:
        for p in packets:
            self._add_packet(p)
    
    def allocate_bits(self, bits: int, curr_tick: int) -> None:
        _ , delay, nb_packets = self.buffer.pop(bits, curr_tick)
        record_bits(bits, self.avgSNR)
        for _ in range(nb_packets):
            record_delay(delay/nb_packets, self.avgSNR, curr_tick)

DUMMY_USER = User(-1, sys.maxsize)