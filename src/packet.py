from dataclasses import dataclass


@dataclass
class Packet:
    size: int


class PacketGenerator:

    def __init__(self, constantBitRate: int, packetSize: int) -> None:
        self.cbr = constantBitRate
        self.packetSize = packetSize

    def generatePackets(self) -> list[Packet]:
        numPackets = int(self.cbr / self.packetSize)
        return [Packet(self.packetSize) for _ in range(numPackets)]
