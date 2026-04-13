import os
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import pyplot as plt

from constant import LOIN_AVG_SNR, PROCHE_AVG_SNR

if TYPE_CHECKING:
    from user import User

# Données collectées au fil de la simulation
_ur_pct: list[float] = []  # %UR utilisées, une entrée par tick
_delais_proche: list[float] = []  # délai par paquet (proche)
_delais_loin: list[float] = []  # délai par paquet (loin)
_bits_proche: list[int] = []  # bits par UR (proche)
_bits_loin: list[int] = []  # bits par UR (loin)
_bits_ur_by_user: list[tuple[float, int]] = []  # (bits/UR moyen, nb utilisateurs)[]
_ur_pct_by_user: list[tuple[float, int]] = []  # (%UR moyen, nb utilisateurs)[]
_delai_proche_by_user: list[tuple[float, int]] = []  # (délai moyen, nb utilisateurs)[]
_delai_loin_by_user: list[tuple[float, int]] = []  # (délai moyen, nb utilisateurs)[]

OUTPUT_DIR = "mesures"

COLORS = {
    "MaxSNR": "#3b82f6",
    "MaxSNR-loin": "#1e40af",
    "RR": "#9333ea",
    "RR-loin": "#581c87",
    "CEI": "#65a30d",
    "CEI-loin": "#3f6212",
    "WFO": "#dc2626",
    "WFO-loin": "#7f1d1d",
}

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


def process_delay(users: list[User], curr_tick: int) -> None:
    """Met en forme les delais depuis une liste d'utilisateurs
        et les enregistre.

    Appelée une fois par tick.

    Args:
        users: la liste des utilisateurs
        curr_tick: le tick actuel de la simulation
    """
    packet_c_loin = 0
    packet_c_proche = 0
    sum_proche = 0
    sum_loin = 0
    for u in users:
        for p in u.buffer.queue:
            if u.avgSNR == PROCHE_AVG_SNR:
                sum_proche += curr_tick - p.timestamp
                packet_c_proche += 1
            else:
                sum_loin += curr_tick - p.timestamp
                packet_c_loin += 1
    record_delay(
        sum_proche / packet_c_proche if packet_c_proche != 0 else 0,
        PROCHE_AVG_SNR,
    )
    record_delay(
        sum_loin / packet_c_loin if packet_c_loin != 0 else 0,
        LOIN_AVG_SNR,
    )


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


def finalise_round(
    n_users: int,
) -> tuple[tuple[float, int], tuple[float, int], tuple[float, int], tuple[float, int]]:
    """Finalise le tour de simulation pour un nombre n d'utilisateurs.

    Args:
        n_users: nombre d'utilisateurs dans le tour de simulation

    Returns:
        ((avg_bits, n_users), (avg_ur_usage, n_users), (avg_delay_proche, n_users), (avg_delay_loin, n_users))

    Appelée une fois par tour de simulation (tick courant == MAX_TICKS).
    """
    # Calcul bits par UR moyen
    bits_per_ur = _bits_proche + _bits_loin

    avg_bits = sum(bits_per_ur) / len(bits_per_ur)
    avg_ur_usage = sum(_ur_pct) / len(_ur_pct)
    avg_delay_proche = sum(_delais_proche) / len(_delais_proche)
    avg_delay_loin = sum(_delais_loin) / len(_delais_loin)

    # clear values for next round
    _ur_pct.clear()
    _bits_proche.clear()
    _bits_loin.clear()
    _delais_proche.clear()
    _delais_loin.clear()

    return (
        (avg_bits, n_users),
        (avg_ur_usage, n_users),
        (avg_delay_proche, n_users),
        (avg_delay_loin, n_users),
    )


#######################################################
## Génération des graphiques
#######################################################


def generate_plots(sim_id: int, algorithm: str) -> None:
    """Génère les graphiques à partir des données collectées."""
    print("Génération des graphiques...")

    output_dir = f"{OUTPUT_DIR}/{algorithm}/sim-{sim_id}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # %UR utilisées par tick
    plt.figure()
    plt.plot(_ur_pct, color="green")
    plt.xlabel("Tick")
    plt.ylabel("% d'UR utilisées")
    plt.title(f"Taux d'utilisation des UR par tick ({algorithm})")
    plt.savefig(f"{output_dir}/ur_usage.png")
    plt.close()

    # Délai par paquet (proche vs loin)
    plt.figure()
    plt.plot(_delais_proche, label="Proche", alpha=0.7, color="green")
    plt.plot(_delais_loin, label="Loin", alpha=0.7, color="red")
    plt.xlabel("Temps (Tick)")
    plt.ylabel("Délai moyen (par user)")
    plt.title(f"Délai moyen par tick ({algorithm})")
    plt.legend()
    plt.savefig(f"{output_dir}/delai.png")
    plt.close()

    # CDF des bits par UR (proche vs loin)
    plt.figure()
    if _bits_proche:
        sorted_proche = np.sort(_bits_proche)
        cdf_proche = np.arange(1, len(sorted_proche) + 1) / len(sorted_proche)
        plt.plot(sorted_proche, cdf_proche, label="Proche", alpha=0.7, color="green")
    if _bits_loin:
        sorted_loin = np.sort(_bits_loin)
        cdf_loin = np.arange(1, len(sorted_loin) + 1) / len(sorted_loin)
        plt.plot(sorted_loin, cdf_loin, label="Loin", alpha=0.7, color="red")
    plt.xlabel("Bits par UR")
    plt.ylabel("CDF")
    plt.title(f"CDF des bits par UR ({algorithm})")
    plt.legend()
    plt.savefig(f"{output_dir}/bits_par_ur.png")
    plt.close()

    print("Graphiques sauvegardés dans", output_dir)


def generate_final_plot(
    bits_ur_by_user: list[tuple[float, int]],
    ur_pct_by_user: list[tuple[float, int]],
    delai_proche_by_user: list[tuple[float, int]],
    delai_loin_by_user: list[tuple[float, int]],
    algorithm: str = "",
) -> None:
    """Génère un graphique final avec bits/UR en y et nb_user en x."""

    output_dir = f"{OUTPUT_DIR}/{algorithm}" if algorithm else OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    label = f" ({algorithm})" if algorithm else ""

    nb_users = [entry[1] for entry in bits_ur_by_user]
    bits_per_ur = [entry[0] for entry in bits_ur_by_user]

    plt.figure()
    plt.plot(nb_users, bits_per_ur, marker="o", color="blue")
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Bits/UR moyen")
    plt.title(f"Bits par UR en fonction du nombre d'utilisateurs{label}")
    plt.savefig(f"{output_dir}/bits_ur_by_user.png")
    plt.close()

    nb_users = [entry[1] for entry in ur_pct_by_user]
    avg_ur_usage = [entry[0] for entry in ur_pct_by_user]

    plt.figure()
    plt.plot(nb_users, avg_ur_usage, marker="o", color="blue")
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Pourcentage d'UR utilisées")
    plt.title(f"Pourcentage d'UR utilisées en fonction du nombre d'utilisateurs{label}")
    plt.savefig(f"{output_dir}/ur_usage_by_user.png")
    plt.close()

    # Délai moyen par nombre d'utilisateurs (proche vs loin)
    nb_users_proche = [entry[1] for entry in delai_proche_by_user]
    delai_proche = [entry[0] for entry in delai_proche_by_user]

    nb_users_loin = [entry[1] for entry in delai_loin_by_user]
    delai_loin = [entry[0] for entry in delai_loin_by_user]

    plt.figure()
    plt.plot(nb_users_proche, delai_proche, marker="o", label="Proche", color="green")
    plt.plot(nb_users_loin, delai_loin, marker="o", label="Loin", color="red")
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Délai moyen")
    plt.title(f"Délai moyen en fonction du nombre d'utilisateurs{label}")
    plt.legend()
    plt.savefig(f"{output_dir}/delai_by_user.png")
    plt.close()

    print(f"Graphiques finaux sauvegardés dans {output_dir}/")


def generate_combined_plot(
    results_by_algo: dict[
        str,
        list[
            tuple[
                tuple[float, int],
                tuple[float, int],
                tuple[float, int],
                tuple[float, int],
            ]
        ],
    ],
) -> None:
    """Génère des graphiques comparatifs avec toutes les algorithmes sur le même graphe."""

    # Bits/UR par nombre d'utilisateurs
    plt.figure()
    for algo, results in results_by_algo.items():
        nb_users = [r[0][1] for r in results]
        bits_per_ur = [r[0][0] for r in results]
        plt.plot(nb_users, bits_per_ur, marker="o", label=algo, color=COLORS[algo])
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Bits/UR moyen")
    plt.title("Bits par UR en fonction du nombre d'utilisateurs")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/bits_ur_by_user.png")
    plt.close()

    # %UR utilisées par nombre d'utilisateurs
    plt.figure()
    for algo, results in results_by_algo.items():
        nb_users = [r[1][1] for r in results]
        avg_ur_usage = [r[1][0] for r in results]
        plt.plot(nb_users, avg_ur_usage, marker="o", label=algo, color=COLORS[algo])
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Pourcentage d'UR utilisées")
    plt.title("Pourcentage d'UR utilisées en fonction du nombre d'utilisateurs")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/ur_usage_by_user.png")
    plt.close()

    # Délai moyen par nombre d'utilisateurs (proche vs loin)
    plt.figure()
    for algo, results in results_by_algo.items():
        nb_users = [r[2][1] for r in results]
        delai_proche = [r[2][0] for r in results]
        delai_loin = [r[3][0] for r in results]
        plt.plot(
            nb_users,
            delai_proche,
            marker="o",
            label=f"{algo} (Proche)",
            color=COLORS[algo],
        )
        plt.plot(
            nb_users,
            delai_loin,
            marker="x",
            label=f"{algo} (Loin)",
            color=COLORS[f"{algo}-loin"],
        )
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Délai moyen")
    plt.title("Délai moyen en fonction du nombre d'utilisateurs")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/delai_by_user.png")
    plt.close()

    print(f"Graphiques comparatifs sauvegardés dans {OUTPUT_DIR}/")
