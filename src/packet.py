from dataclasses import dataclass


@dataclass
class Packet:
    """Represents a network packet with a specified size and timestamp."""
    size: int
    timestamp: int


class PacketGenerator:

    def __init__(self, constantBitRate: int, packetSize: int) -> None:
        self.cbr = constantBitRate
        self.packetSize = packetSize

    def generatePackets(self, t: int) -> list[Packet]:
        """
        Generates packets based on the constant bit rate and packet size.
        
        :param t: The timestamp at which the packets are generated.
        :type t: int
        :return: A list of generated packets.
        :rtype: list[Packet]
        """
        numPackets = int(self.cbr / self.packetSize)
        return [Packet(self.packetSize, timestamp=t) for _ in range(numPackets)]
