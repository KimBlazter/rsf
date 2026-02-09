import os
from dataclasses import dataclass
from random import randint, random

from matplotlib import pyplot as plt


@dataclass
class Data:
    delais_loin: list[float]
    """Délai pour les paquets envoyés par les utilisateurs loin"""
    delais_proche: list[float]
    """Délai pour les paquets envoyés par les utilisateurs proches"""
    ur_utilises: list[int]
    """Nombre d'UR utilisées par UR"""
    bits_par_ur: list[float]
    """Nombre de bits utilisés par UR"""


data = Data([], [], [], [])

# Generate mock data
paquets = 1000
iterations = 100
ur_total = 100
data.delais_loin = [random() + 0.18 for _ in range(paquets)]
data.delais_proche = [random() for _ in range(paquets)]
data.ur_utilises = [randint(1, ur_total) for _ in range(iterations)]

# # Mesures à prendre
# > Pour chaque, faire de moyennes pour les utilisateurs loin / proches
#
# - %UR => pas toutes les UR ne sont utilisées à chaque itération
# - Délai moyen => enregistrer les délais pour chaque paquet (timestamp arrivée - timestamp départ)
# - bits/UR


#######################################################
## Prise des mesures au fur et à mesure
#######################################################


def nb_ur_used(n: int) -> None:
    """ """
    data.ur_utilises.append(n)


def prise2() -> None:
    """ """
    return


def prise3() -> None:
    """ """
    return


#######################################################
#######################################################
#######################################################


def generate_plots() -> None:
    """
    Genère les graphiques à partir des données collectées dans `data`
    """
    print("Génération des graphiques...")

    output_dir = "mesures"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.plot(data.delais_loin)
    plt.xlabel("Paquet")
    plt.ylabel("Délai (s)")
    plt.savefig(f"{output_dir}/loin.png")
    plt.close()

    plt.plot(data.delais_proche)
    plt.xlabel("Paquet")
    plt.ylabel("Délai (s)")
    plt.savefig(f"{output_dir}/proche.png")
    plt.close()

    plt.plot([(d / ur_total) * 100 for d in data.ur_utilises])
    plt.xlabel("Itération")
    plt.ylabel("% d'UR utilisées")
    plt.savefig(f"{output_dir}/ur.png")
    plt.close()

    return


if __name__ == "__main__":
    generate_plots()
