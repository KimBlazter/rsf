from collections import deque
from packet import Packet

class Buffer:
    
    """
    Buffer FIFO pour un utilisateur du réseau sans fil.
    
    Modélise la file d'attente de paquets en attente de transmission.
    - Les paquets arrivent via push() (étape "remplir les buffers")
    - Les paquets partent via pop() (étape "vider les buffers schedulés")
    - Si le buffer est plein, les paquets sont droppés (perdus)
    """
    
    
    
    def __init__(self):
        self.queue: deque[Packet] = deque()
        self.current_size: int = 0



    def push(self, packet: Packet) -> None:
        """
        Étape "remplir les buffers" : tente d'ajouter un paquet dans la file.
        Si l'espace restant est suffisant, le paquet entre.
        Sinon, il est droppé (politique tail-drop).
        
        Args:
            packet: objet avec attribut .size (taille en bits)
        """
        self.queue.append(packet)
        self.current_size += packet.size
    



    def pop(self, bits, current_tick):
        """
        Étape "vider les buffers schedulés" : retire des paquets de la file
        dans la limite du budget de bits alloué par le scheduler.
        
        On transmet des paquets ENTIERS : si le prochain paquet ne tient pas
        dans le budget restant, on s'arrête.
        
        Args:
            bits: nombre de bits alloués par le scheduler pour cette itération
            current_tick: tick courant de la simulation
            
        Returns:
            tuple (transmitted, delay_sum, sent_packets) :
                - transmitted : nombre réel de bits transmis
                - delay_sum   : somme des délais des paquets transmis
                                (delay = current_tick - timestamp)
                - sent_packets: nombre de paquets transmis
        """
        transmitted = 0
        delay_sum = 0
        sent_packets = 0

        while self.queue and transmitted < bits:
            # On regarde le premier paquet de la file (sans le retirer encore)
            pkt = self.queue[0]
            if transmitted + pkt.size <= bits:
                # Le paquet tient dans le budget → on le transmet entièrement
                transmitted += pkt.size
                delay_sum += current_tick - pkt.timestamp
                sent_packets += 1
                # On retire le paquet de la file
                self.queue.popleft()
                self.current_size -= pkt.size
            else:
                # Le prochain paquet est trop gros pour le budget restant
                # TODO : modif?
                remaining_bits = bits - transmitted
                transmitted += remaining_bits
                pkt.size -= remaining_bits
                self.current_size -= remaining_bits
                break
        return transmitted, delay_sum, sent_packets



    def size(self):
        return self.current_size
