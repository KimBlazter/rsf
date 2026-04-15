import os
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import pyplot as plt

from constant import LOW_RELAY_RATIO, PROCHE_AVG_SNR

if TYPE_CHECKING:
    from user import User

_ur_pct: list[float] = []  # %UR utilisées, une entrée par tick
_delais_proche: list[float] = []  # délai par paquet (proche)
_delais_loin: list[float] = []  # délai par paquet (loin)
_bits_proche: list[int] = []  # bits par UR (proche)
_bits_loin: list[int] = []  # bits par UR (loin)

_delais_cei: dict[str, list[float]] = {"PL": [], "PH": [], "LL": [], "LH": []}
_bits_cei: dict[str, list[int]] = {"PL": [], "PH": [], "LL": [], "LH": []}

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
    "PF": "#eab308",
    "PF-loin": "#a16207",
}

CEI_COLORS = {
    "PL": "#a3e635",
    "PH": "#22c55e",
    "LL": "#ca8a04",
    "LH": "#166534",
}

CEI_LABELS = {
    "PL": "Proche + Relai bas",
    "PH": "Proche + Relai élevé",
    "LL": "Loin + Relai bas",
    "LH": "Loin + Relai élevé",
}


def _cei_key(avg_snr: float, relay_ratio: float) -> str:
    p = "P" if avg_snr == PROCHE_AVG_SNR else "L"
    r = "L" if relay_ratio == LOW_RELAY_RATIO else "H"
    return p + r


#######################################################
## Prise des mesures au fur et à mesure
#######################################################


def record_ur_usage(ur_used: int, total_ur: int) -> None:
    _ur_pct.append((ur_used / total_ur) * 100)


def process_delay(users: list["User"], curr_tick: int, algorithm: str) -> None:
    if algorithm == "CEI":
        sums: dict[str, float] = {"PL": 0, "PH": 0, "LL": 0, "LH": 0}
        counts: dict[str, int] = {"PL": 0, "PH": 0, "LL": 0, "LH": 0}
        for u in users:
            key = _cei_key(u.avgSNR, u.relay_ratio)
            for p in u.buffer.queue:
                sums[key] += curr_tick - p.timestamp
                counts[key] += 1

        for key in sums:
            avg = sums[key] / counts[key] if counts[key] > 0 else 0
            _delais_cei[key].append(avg)

        # For combined plots: aggregate by relay ratio
        low_sum = sums["PL"] + sums["LL"]
        low_count = counts["PL"] + counts["LL"]
        high_sum = sums["PH"] + sums["LH"]
        high_count = counts["PH"] + counts["LH"]
        _delais_proche.append(low_sum / low_count if low_count > 0 else 0)
        _delais_loin.append(high_sum / high_count if high_count > 0 else 0)
    else:
        packet_c_loin = 0
        packet_c_proche = 0
        sum_proche = 0.0
        sum_loin = 0.0
        for u in users:
            for p in u.buffer.queue:
                if u.avgSNR == PROCHE_AVG_SNR:
                    sum_proche += curr_tick - p.timestamp
                    packet_c_proche += 1
                else:
                    sum_loin += curr_tick - p.timestamp
                    packet_c_loin += 1
        _delais_proche.append(
            sum_proche / packet_c_proche if packet_c_proche > 0 else 0
        )
        _delais_loin.append(sum_loin / packet_c_loin if packet_c_loin > 0 else 0)


def record_bits(
    bits: int, avg_snr: int, relay_ratio: float = 0.0, algorithm: str = ""
) -> None:
    if algorithm == "CEI":
        key = _cei_key(avg_snr, relay_ratio)
        _bits_cei[key].append(bits)
        if relay_ratio == LOW_RELAY_RATIO:
            _bits_proche.append(bits)
        else:
            _bits_loin.append(bits)
    else:
        if avg_snr == PROCHE_AVG_SNR:
            _bits_proche.append(bits)
        else:
            _bits_loin.append(bits)


def verify_data(algorithm: str) -> None:
    print(f"\n--- Vérification des données ({algorithm}) ---")
    print(f"  Ticks enregistrés (UR usage): {len(_ur_pct)}")

    if algorithm == "CEI":
        for key in ["PL", "PH", "LL", "LH"]:
            bits = _bits_cei[key]
            delays = _delais_cei[key]
            avg_b = f", avg bits={sum(bits) / len(bits):.1f}" if bits else ""
            avg_d = f", avg délai={sum(delays) / len(delays):.1f}" if delays else ""
            print(
                f"  {CEI_LABELS[key]}: {len(bits)} bits, {len(delays)} délais{avg_b}{avg_d}"
            )

        total_4cat = sum(len(_bits_cei[k]) for k in _bits_cei)
        total_2cat = len(_bits_proche) + len(_bits_loin)
        if total_4cat != total_2cat:
            print(
                f"  /!\\ INCOHÉRENCE bits: 4-cat total={total_4cat} vs 2-cat total={total_2cat}"
            )
        else:
            print(f"  OK Bits cohérents ({total_2cat} entrées)")

        total_d4 = sum(len(_delais_cei[k]) for k in _delais_cei)
        total_d2 = len(_delais_proche) + len(_delais_loin)
        if total_d4 != total_d2 * 2:
            print(
                f"  /!\\ INCOHÉRENCE délais: 4-cat total={total_d4} vs attendu={total_d2 * 2} (2 par tick x 2 = 4)"
            )
        else:
            print(f"  OK Délais cohérents ({total_d4} entrées en 4 catégories)")
    else:
        for label, data in [("Bits proche", _bits_proche), ("Bits loin", _bits_loin)]:
            avg = f", avg={sum(data) / len(data):.1f}" if data else ""
            print(f"  {label}: {len(data)} entrées{avg}")
        for label, data in [
            ("Délais proche", _delais_proche),
            ("Délais loin", _delais_loin),
        ]:
            avg = f", avg={sum(data) / len(data):.1f}" if data else ""
            print(f"  {label}: {len(data)} entrées{avg}")

    print("---\n")


def finalise_round(n_users: int, algorithm: str = "") -> tuple:
    bits_per_ur = _bits_proche + _bits_loin
    avg_bits = sum(bits_per_ur) / len(bits_per_ur) if bits_per_ur else 0
    avg_ur_usage = sum(_ur_pct) / len(_ur_pct) if _ur_pct else 0
    avg_delay_proche = (
        sum(_delais_proche) / len(_delais_proche) if _delais_proche else 0
    )
    avg_delay_loin = sum(_delais_loin) / len(_delais_loin) if _delais_loin else 0

    result: tuple = (
        (avg_bits, n_users),
        (avg_ur_usage, n_users),
        (avg_delay_proche, n_users),
        (avg_delay_loin, n_users),
    )

    if algorithm == "CEI":
        cei_delays = {}
        for key in ["PL", "PH", "LL", "LH"]:
            d = _delais_cei[key]
            cei_delays[key] = sum(d) / len(d) if d else 0
        result = result + (
            (cei_delays["PL"], n_users),
            (cei_delays["PH"], n_users),
            (cei_delays["LL"], n_users),
            (cei_delays["LH"], n_users),
        )
        for key in _delais_cei:
            _delais_cei[key].clear()
        for key in _bits_cei:
            _bits_cei[key].clear()

    _ur_pct.clear()
    _bits_proche.clear()
    _bits_loin.clear()
    _delais_proche.clear()
    _delais_loin.clear()

    return result


#######################################################
## Génération des graphiques
#######################################################


def generate_plots(sim_id: int, algorithm: str) -> None:
    print("Génération des graphiques...")

    output_dir = f"{OUTPUT_DIR}/{algorithm}/sim-{sim_id}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    verify_data(algorithm)

    # %UR utilisées par tick
    plt.figure()
    plt.plot(_ur_pct, color=COLORS[algorithm])
    plt.xlabel("Tick")
    plt.ylabel("% d'UR utilisées")
    plt.title(f"Taux d'utilisation des UR par tick ({algorithm})")
    plt.savefig(f"{output_dir}/ur_usage.png", bbox_inches="tight")
    plt.close()

    # Délai par tick
    if algorithm == "CEI":
        plt.figure()
        for key in ["PL", "PH", "LL", "LH"]:
            plt.plot(
                _delais_cei[key],
                label=CEI_LABELS[key],
                alpha=0.7,
                color=CEI_COLORS[key],
            )
        plt.xlabel("Temps (Tick)")
        plt.ylabel("Délai moyen (par user)")
        plt.title(f"Délai moyen par tick ({algorithm})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.savefig(f"{output_dir}/delai.png", bbox_inches="tight")
        plt.close()
    else:
        plt.figure()
        plt.plot(
            _delais_proche,
            label="Proche",
            alpha=0.7,
            color=COLORS[algorithm],
        )
        plt.plot(
            _delais_loin,
            label="Loin",
            alpha=0.7,
            color=COLORS[f"{algorithm}-loin"],
        )
        plt.xlabel("Temps (Tick)")
        plt.ylabel("Délai moyen (par user)")
        plt.title(f"Délai moyen par tick ({algorithm})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.savefig(f"{output_dir}/delai.png", bbox_inches="tight")
        plt.close()

    # CDF des bits par UR
    if algorithm == "CEI":
        plt.figure()
        for key in ["PL", "PH", "LL", "LH"]:
            data = _bits_cei[key]
            if data:
                sorted_data = np.sort(data)
                cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
                plt.plot(
                    sorted_data,
                    cdf,
                    label=CEI_LABELS[key],
                    alpha=0.7,
                    color=CEI_COLORS[key],
                )
        plt.xlabel("Bits par UR")
        plt.ylabel("CDF")
        plt.title(f"CDF des bits par UR ({algorithm})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.savefig(f"{output_dir}/bits_par_ur.png", bbox_inches="tight")
        plt.close()
    else:
        plt.figure()
        if _bits_proche:
            sorted_proche = np.sort(_bits_proche)
            cdf_proche = np.arange(1, len(sorted_proche) + 1) / len(sorted_proche)
            plt.plot(
                sorted_proche,
                cdf_proche,
                label="Proche",
                alpha=0.7,
                color=COLORS[algorithm],
            )
        if _bits_loin:
            sorted_loin = np.sort(_bits_loin)
            cdf_loin = np.arange(1, len(sorted_loin) + 1) / len(sorted_loin)
            plt.plot(
                sorted_loin,
                cdf_loin,
                label="Loin",
                alpha=0.7,
                color=COLORS[f"{algorithm}-loin"],
            )
        plt.xlabel("Bits par UR")
        plt.ylabel("CDF")
        plt.title(f"CDF des bits par UR ({algorithm})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.savefig(f"{output_dir}/bits_par_ur.png", bbox_inches="tight")
        plt.close()

    print("Graphiques sauvegardés dans", output_dir)


def generate_final_plot(
    bits_ur_by_user: list[tuple[float, int]],
    ur_pct_by_user: list[tuple[float, int]],
    delai_proche_by_user: list[tuple[float, int]],
    delai_loin_by_user: list[tuple[float, int]],
    algorithm: str = "",
    cei_delai_pl: list[tuple[float, int]] | None = None,
    cei_delai_ph: list[tuple[float, int]] | None = None,
    cei_delai_ll: list[tuple[float, int]] | None = None,
    cei_delai_lh: list[tuple[float, int]] | None = None,
) -> None:
    output_dir = f"{OUTPUT_DIR}/{algorithm}" if algorithm else OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    label = f" ({algorithm})" if algorithm else ""

    nb_users = [entry[1] for entry in bits_ur_by_user]
    bits_per_ur = [entry[0] for entry in bits_ur_by_user]

    plt.figure()
    plt.plot(nb_users, bits_per_ur, marker="o", color=COLORS[algorithm])
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Bits/UR moyen")
    plt.title(f"Bits par UR en fonction du nombre d'utilisateurs{label}")
    plt.savefig(f"{output_dir}/bits_ur_by_user.png", bbox_inches="tight")
    plt.close()

    nb_users = [entry[1] for entry in ur_pct_by_user]
    avg_ur_usage = [entry[0] for entry in ur_pct_by_user]

    plt.figure()
    plt.plot(nb_users, avg_ur_usage, marker="o", color=COLORS[algorithm])
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Pourcentage d'UR utilisées")
    plt.title(f"Pourcentage d'UR utilisées en fonction du nombre d'utilisateurs{label}")
    plt.savefig(f"{output_dir}/ur_usage_by_user.png", bbox_inches="tight")
    plt.close()

    # Délai moyen par nombre d'utilisateurs
    plt.figure()
    if algorithm == "CEI" and cei_delai_pl is not None:
        for data, key in [
            (cei_delai_pl, "PL"),
            (cei_delai_ph, "PH"),
            (cei_delai_ll, "LL"),
            (cei_delai_lh, "LH"),
        ]:
            if data:
                x = [entry[1] for entry in data]
                y = [entry[0] for entry in data]
                plt.plot(x, y, marker="o", label=CEI_LABELS[key], color=CEI_COLORS[key])
    else:
        nb_users_proche = [entry[1] for entry in delai_proche_by_user]
        delai_proche = [entry[0] for entry in delai_proche_by_user]
        nb_users_loin = [entry[1] for entry in delai_loin_by_user]
        delai_loin = [entry[0] for entry in delai_loin_by_user]

        plt.plot(
            nb_users_proche,
            delai_proche,
            marker="o",
            label="Proche",
            color=COLORS[algorithm],
        )
        plt.plot(
            nb_users_loin,
            delai_loin,
            marker="o",
            label="Loin",
            color=COLORS[f"{algorithm}-loin"],
        )

    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Délai moyen")
    plt.title(f"Délai moyen en fonction du nombre d'utilisateurs{label}")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(f"{output_dir}/delai_by_user.png", bbox_inches="tight")
    plt.close()

    print(f"Graphiques finaux sauvegardés dans {output_dir}/")


def generate_combined_plot(
    results_by_algo: dict[str, list],
) -> None:
    # Bits/UR par nombre d'utilisateurs
    plt.figure()
    for algo, results in results_by_algo.items():
        nb_users = [r[0][1] for r in results]
        bits_per_ur = [r[0][0] for r in results]
        plt.plot(nb_users, bits_per_ur, marker="o", label=algo, color=COLORS[algo])
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Bits/UR moyen")
    plt.title("Bits par UR en fonction du nombre d'utilisateurs")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(f"{OUTPUT_DIR}/bits_ur_by_user.png", bbox_inches="tight")
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
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(f"{OUTPUT_DIR}/ur_usage_by_user.png", bbox_inches="tight")
    plt.close()

    # Délai moyen par nombre d'utilisateurs
    plt.figure()
    for algo, results in results_by_algo.items():
        nb_users = [r[2][1] for r in results]
        delai_proche = [r[2][0] for r in results]
        delai_loin = [r[3][0] for r in results]
        label_low = "Relai ratio bas" if algo == "CEI" else "Proche"
        label_high = "Relai ratio élevé" if algo == "CEI" else "Loin"
        plt.plot(
            nb_users,
            delai_proche,
            marker="o",
            label=f"{algo} ({label_low})",
            color=COLORS[algo],
        )
        plt.plot(
            nb_users,
            delai_loin,
            marker="x",
            label=f"{algo} ({label_high})",
            color=COLORS[f"{algo}-loin"],
        )
    plt.xlabel("Nombre d'utilisateurs")
    plt.ylabel("Délai moyen")
    plt.title("Délai moyen en fonction du nombre d'utilisateurs")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(f"{OUTPUT_DIR}/delai_by_user.png", bbox_inches="tight")
    plt.close()

    print(f"Graphiques comparatifs sauvegardés dans {OUTPUT_DIR}/")
