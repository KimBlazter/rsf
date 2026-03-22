import os

from matplotlib import pyplot as plt

# SNR moyen des utilisateurs proches (défini dans initialization.py)
_PROCHE_AVG_SNR = 11

# Données collectées au fil de la simulation
_ur_pct: list[float] = []  # %UR utilisées, une entrée par tick
_delais_proche: list[float] = []  # délai par paquet (proche)
_delais_loin: list[float] = []  # délai par paquet (loin)
_bits_proche: list[int] = []  # bits par UR (proche)
_bits_loin: list[int] = []  # bits par UR (loin)

# # Mesures à prendre
# > Pour chaque, faire de moyennes pour les utilisateurs loin / proches
#
# - %UR => pas toutes les UR ne sont utilisées à chaque itération
# - Délai moyen => enregistrer les délais pour chaque paquet (timestamp arrivée - timestamp départ)
# - bits/UR


#######################################################
## Prise des mesures au fur et à mesure
#######################################################


def record_ur_usage(ur_used: int, total_ur: int) -> None:
    """Enregistre le taux d'utilisation des UR pour un tick.

    Appelée une fois par tick depuis le scheduler.

    Args:
        ur_used: nombre d'UR effectivement allouées (hors DUMMY_USER)
        total_ur: nombre total d'UR disponibles (640)
    """
    _ur_pct.append((ur_used / total_ur) * 100)


def record_delay(delay: float, avg_snr: int) -> None:
    """Enregistre le délai d'un paquet transmis.

    Appelée une fois par paquet transmis depuis buffer.pop().

    Args:
        delay: délai du paquet (tick courant - timestamp de création)
        avg_snr: SNR moyen de l'utilisateur (pour distinguer proche/loin)
    """
    if avg_snr == _PROCHE_AVG_SNR:
        _delais_proche.append(delay)
    else:
        _delais_loin.append(delay)


def record_bits(bits: int, avg_snr: int) -> None:
    """Enregistre les bits transmis pour une allocation d'UR.

    Appelée une fois par UR allouée depuis scheduler.apply_repartition().

    Args:
        bits: bits effectivement transmis sur cette UR
        avg_snr: SNR moyen de l'utilisateur (pour distinguer proche/loin)
    """
    if avg_snr == _PROCHE_AVG_SNR:
        _bits_proche.append(bits)
    else:
        _bits_loin.append(bits)


#######################################################
## Génération des graphiques
#######################################################


def generate_plots() -> None:
    """Génère les graphiques à partir des données collectées."""
    print("Génération des graphiques...")

    output_dir = "mesures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. %UR utilisées par tick
    plt.figure()
    plt.plot(_ur_pct)
    plt.xlabel("Tick")
    plt.ylabel("% d'UR utilisées")
    plt.title("Taux d'utilisation des UR par tick")
    plt.savefig(f"{output_dir}/ur_usage.png")
    plt.close()

    # 2. Délai par paquet (proche vs loin)
    plt.figure()
    if _delais_proche:
        plt.plot(_delais_proche, label="Proche", alpha=0.7)
    if _delais_loin:
        plt.plot(_delais_loin, label="Loin", alpha=0.7)
    plt.xlabel("Paquet")
    plt.ylabel("Délai (ticks)")
    plt.title("Délai par paquet")
    plt.legend()
    plt.savefig(f"{output_dir}/delai.png")
    plt.close()

    # 3. Bits par UR (proche vs loin)
    plt.figure()
    if _bits_proche:
        plt.plot(_bits_proche, label="Proche", alpha=0.7)
    if _bits_loin:
        plt.plot(_bits_loin, label="Loin", alpha=0.7)
    plt.xlabel("UR")
    plt.ylabel("Bits")
    plt.title("Bits par UR")
    plt.legend()
    plt.savefig(f"{output_dir}/bits_par_ur.png")
    plt.close()

    # Moyennes
    if _delais_proche:
        print(
            f"  Délai moyen proche: {sum(_delais_proche) / len(_delais_proche):.2f} ticks"
        )
    if _delais_loin:
        print(
            f"  Délai moyen loin:   {sum(_delais_loin) / len(_delais_loin):.2f} ticks"
        )
    if _bits_proche:
        print(f"  Bits/UR moyen proche: {sum(_bits_proche) / len(_bits_proche):.2f}")
    if _bits_loin:
        print(f"  Bits/UR moyen loin:   {sum(_bits_loin) / len(_bits_loin):.2f}")
    if _ur_pct:
        print(f"  %UR moyen:            {sum(_ur_pct) / len(_ur_pct):.2f}%")

    print("Graphiques sauvegardés dans", output_dir)


if __name__ == "__main__":
    generate_plots()
