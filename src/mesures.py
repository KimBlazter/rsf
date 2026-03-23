import os

import numpy as np
from matplotlib import pyplot as plt
from constant import PROCHE_AVG_SNR

# Données collectées au fil de la simulation
_ur_pct: list[float] = []  # %UR utilisées, une entrée par tick
_delais_proche: list[float] = []  # délai par paquet (proche)
_delais_loin: list[float] = []  # délai par paquet (loin)
_bits_proche: list[int] = []  # bits par UR (proche)
_bits_loin: list[int] = []  # bits par UR (loin)
_bits_ur_by_user: list[tuple[float, int]] = []  # (bits/UR moyen, nb utilisateurs)

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
    if avg_snr == PROCHE_AVG_SNR:
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
    if avg_snr == PROCHE_AVG_SNR:
        _bits_proche.append(bits)
    else:
        _bits_loin.append(bits)


def finalise_round(n_users: int) -> None:
    """Finalise le tour de simulation pour un nombre n d'utilisateurs.

    Args:
        n_users: nombre d'utilisateurs dans le tour de simulation

    Appelée une fois par tour de simulation (tick courant == MAX_TICKS).
    """
    # Calcul bits par UR moyen
    bits_per_ur = _bits_proche + _bits_loin

    avg = sum(bits_per_ur) / len(bits_per_ur)

    _bits_ur_by_user.append((avg, n_users))

    # clear values for next round
    _ur_pct.clear()
    _delais_proche.clear()
    _delais_loin.clear()
    _bits_proche.clear()
    _bits_loin.clear()


#######################################################
## Génération des graphiques
#######################################################


def generate_plots(sim_id: int) -> None:
    """Génère les graphiques à partir des données collectées."""
    print("Génération des graphiques...")

    output_dir = f"mesures/sim-{sim_id}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # %UR utilisées par tick
    plt.figure()
    plt.plot(_ur_pct)
    plt.xlabel("Tick")
    plt.ylabel("% d'UR utilisées")
    plt.title("Taux d'utilisation des UR par tick")
    plt.savefig(f"{output_dir}/ur_usage.png")
    plt.close()

    # Délai par paquet (proche vs loin)
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

    # CDF des bits par UR (proche vs loin)
    plt.figure()
    if _bits_proche:
        sorted_proche = np.sort(_bits_proche)
        cdf_proche = np.arange(1, len(sorted_proche) + 1) / len(sorted_proche)
        plt.plot(sorted_proche, cdf_proche, label="Proche", alpha=0.7)
    if _bits_loin:
        sorted_loin = np.sort(_bits_loin)
        cdf_loin = np.arange(1, len(sorted_loin) + 1) / len(sorted_loin)
        plt.plot(sorted_loin, cdf_loin, label="Loin", alpha=0.7)
    plt.xlabel("Bits par UR")
    plt.ylabel("CDF")
    plt.title("CDF des bits par UR")
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

    print(f"DEBUG {max(_bits_proche)}")
    print("Graphiques sauvegardés dans", output_dir)


def generate_final_plot() -> None:
    """Génère un graphique final avec bits/UR en y et nb_user en x."""
    output_dir = "mesures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nb_users = [entry[1] for entry in _bits_ur_by_user]
    bits_per_ur = [entry[0] for entry in _bits_ur_by_user]

    plt.figure()
    plt.plot(nb_users, bits_per_ur, marker="o")
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Bits/UR moyen")
    plt.title("Bits par UR en fonction du nombre d'utilisateurs")
    plt.savefig(f"{output_dir}/bits_ur_by_user.png")
    plt.close()

    print(f"Graphique final sauvegardé dans {output_dir}/bits_ur_by_user.png")


if __name__ == "__main__":
    from random import randint, random

    # Simuler plusieurs tours avec un nombre croissant d'utilisateurs
    for sim_id, n_users in enumerate([5, 10, 15, 20, 25]):
        # Simuler 100 ticks par tour
        for tick in range(100):
            # UR usage: entre 400 et 640 UR utilisées par tick
            record_ur_usage(randint(400, 640), 640)

            # Quelques paquets transmis par tick
            for _ in range(randint(5, 20)):
                # Proche (avgSNR=11): délai entre 0 et 5 ticks
                record_delay(random() * 5, avg_snr=11)
                record_bits(randint(20, 88), avg_snr=11)

                # Loin (avgSNR=7): délai plus élevé, entre 2 et 10 ticks
                record_delay(2 + random() * 8, avg_snr=7)
                record_bits(randint(4, 56), avg_snr=7)

        generate_plots(sim_id)
        finalise_round(n_users)

    generate_final_plot()
