import sys

from buffer import Buffer
from mesures import record_bits
from packet import Packet


class User:
    def __init__(self, id, avgSNR, relay_ratio):
        self.id = id
        self.buffer: Buffer = Buffer()  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR
        self.relay_ratio = relay_ratio

    def _add_packet(self, packet: Packet) -> None:
        self.buffer.push(packet)

    def add_packets(self, packets: list[Packet]) -> None:
        for p in packets:
            self._add_packet(p)

    def allocate_bits(self, bits: int, curr_tick: int) -> None:
        self.buffer.pop(bits, curr_tick)
        record_bits(bits, self.avgSNR)


DUMMY_USER = User(-1, sys.maxsize, 0)
