from dataclasses import dataclass
import random
from buffer import Buffer
from user import User


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
        # TODO add mitigation (generate base on chances eg: 80%)
        numPackets = int(self.cbr / self.packetSize)
        return [Packet(self.packetSize, timestamp=t) for _ in range(numPackets)]

    def generateUsersPackets(self, users: list[User], t: int) -> None:
        """Generates packets for all users at a given timestamp.

        For each user, performs n generation attempts based on the
        CHANCE_TO_GENERATE_PACKET probability.

        Args:
            users: List of users receiving packets
            t: Current timestamp.
        """
        # FIXME
        for user in users:
            if random.random() < self.CHANCE_TO_GENERATE_PACKET:
                user.add_packets(self._generatePackets(t))

