import sys

from buffer import Buffer
from mesures import record_bits
from packet import Packet
import sys
from mesures import record_bits
from constant import PDOR_THRESHOLD

class User:
    def __init__(self, id, avgSNR, relay_ratio):
        self.id = id
        self.buffer: Buffer = Buffer()  # Initialize with a buffer of 1000 bits
        self.avgSNR = avgSNR
        self.relay_ratio = relay_ratio
        self.pdor: float

    def _add_packet(self, packet: Packet) -> None:
        self.buffer.push(packet)

    def add_packets(self, packets: list[Packet]) -> None:
        for p in packets:
            self._add_packet(p)

<<<<<<< src/user.py
    def allocate_bits(self, bits: int, curr_tick: int) -> None:
        transmitted, _, _ = self.buffer.pop(bits, curr_tick)    
        record_bits(
            transmitted if algo != "CEI" else transmitted // (1 - self.relay_ratio), self.avgSNR
        )

        
    def get_pdor(self, tick: int) -> float:
        """Get current PDOR
        
        PDOR = nb_packet with delay > threshold / total_packet_sent

        Args:
            tick (int): current simulation tick
            
        Returns:
            (float) current pdor
        """
        packets_over_threshold = list(filter(lambda p: tick - p.timestamp >  PDOR_THRESHOLD, self.buffer.queue))
        self.pdor = len(packets_over_threshold) / (len(self.buffer.queue) + 0.1)
        return self.pdor


DUMMY_USER = User(-1, sys.maxsize, 1)
