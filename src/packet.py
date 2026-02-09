from dataclasses import dataclass
import random
from buffer import Buffer


@dataclass
class Packet:
    """Represents a network packet with a size and timestamp.

    Attributes:
        size: Packet size in bits.
        timestamp: Packet creation timestamp.
    """

    size: int
    timestamp: int


class PacketGenerator:
    """Packet generator to simulate user network traffic.

    Attributes:
        CHANCE_TO_GENERATE_PACKET: Probability of generating a packet for each
            user at each time step.
        cbr: Constant Bit Rate in bits/second.
        packetSize: Size of generated packets in bits.
    """

    CHANCE_TO_GENERATE_PACKET = 0.5

    def __init__(self, constantBitRate: int, packetSize: int) -> None:
        """Initializes the packet generator.

        Args:
            constantBitRate: Constant bit rate in bits/second.
            packetSize: Size of each packet in bits.
        """
        self.cbr = constantBitRate
        self.packetSize = packetSize

    def _generatePackets(self, t: int) -> list[Packet]:
        """Generates packets based on the constant bit rate and configured size.

        Args:
            t: Packet generation timestamp.

        Returns:
            List of generated packets.
        """
        numPackets = int(self.cbr / self.packetSize)
        return [Packet(self.packetSize, timestamp=t) for _ in range(numPackets)]

    def generateUsersPackets(self, users: dict[int, Buffer], t: int, n: int) -> None:
        """Generates packets for all users at a given timestamp.

        For each user, performs n generation attempts based on the
        CHANCE_TO_GENERATE_PACKET probability.

        Args:
            t: Current timestamp.
            n: Number of generation attempts per user.
        """
        for user in users.keys():
            for _ in range(n):
                if random.random() < self.CHANCE_TO_GENERATE_PACKET:
                    users[user].push(self._generatePackets(t))
