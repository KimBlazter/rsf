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
    
    
    
    def __init__(self, max_size_bits: int):
        self.queue: deque[Packet] = deque()
        self.max_size: int = max_size_bits
        self.current_size: int = 0
        self.dropped_packets: int = 0 # Compteur de paquets perdus car le buffer était plein (tail-drop)



    def push(self, packet: Packet) -> None:
        """
        Étape "remplir les buffers" : tente d'ajouter un paquet dans la file.
        Si l'espace restant est suffisant, le paquet entre.
        Sinon, il est droppé (politique tail-drop).
        
        Args:
            packet: objet avec attribut .size (taille en bits)
        """
        if self.current_size + packet.size <= self.max_size:
            # Il reste assez de place → on ajoute le paquet en bout de file
            self.queue.append(packet)
            self.current_size += packet.size
        else:
            # Buffer plein → le paquet est perdu
            self.dropped_packets += 1



    def pop(self, bits):
        """
        Étape "vider les buffers schedulés" : retire des paquets de la file
        dans la limite du budget de bits alloué par le scheduler.
        
        On transmet des paquets ENTIERS : si le prochain paquet ne tient pas
        dans le budget restant, on s'arrête.
        
        Args:
            bits: nombre de bits alloués par le scheduler pour cette itération
            
        Returns:
            tuple (transmitted, delay_sum) :
                - transmitted : nombre réel de bits transmis
                - delay_sum   : somme des arrival_time des paquets transmis
                                (utile pour calculer le délai moyen plus tard)
        """
        transmitted = 0
        delay_sum = 0

        while self.queue and transmitted < bits:
            # On regarde le premier paquet de la file (sans le retirer encore)
            pkt = self.queue[0]
            if transmitted + pkt.size <= bits:
                # Le paquet tient dans le budget → on le transmet
                transmitted += pkt.size
                delay_sum += pkt.arrival_time
                # On retire le paquet de la file
                self.queue.popleft()
                self.current_size -= pkt.size
            else:
                # Le prochain paquet est trop gros pour le budget restant → on arrête
                break
        return transmitted, delay_sum



    def size(self):
        return self.current_size
