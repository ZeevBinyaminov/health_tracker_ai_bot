from io import BytesIO
from typing import Dict, Iterable, List


import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def _prepare_series(stats: Iterable[Dict]) -> tuple[list[str], list[int], list[int]]:
    rows = sorted(stats, key=lambda item: item["date"])
    labels = []
    water = []
    kcal = []
    for item in rows:
        date_value = item["date"]

        labels.append(date_value)
        water.append(int(item.get("water_ml", 0)))
        kcal.append(int(item.get("kcal", 0)))
    return labels, water, kcal


def _render_plot(fig) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


def build_water_plot(stats: List[Dict]) -> bytes:
    if not stats:
        return b""
    labels, water, _ = _prepare_series(stats)
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
    ax.bar(labels, water, color="#2a9d8f", alpha=0.85)
    ax.set_title("Прием воды (последние 7 дней)")
    ax.set_ylabel("мл")
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis='x', labelrotation=45)

    ax.set_axisbelow(True)
    fig.tight_layout()
    return _render_plot(fig)


def build_kcal_plot(stats: List[Dict]) -> bytes:
    if not stats:
        return b""
    labels, _, kcal = _prepare_series(stats)
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
    ax.plot(labels, kcal, marker="o", color="#e76f51", linewidth=2)
    ax.fill_between(labels, kcal, alpha=0.15, color="#e76f51")
    ax.set_title("Прием калорий (последние 7 дней)")
    ax.set_ylabel("ккал")
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis='x', labelrotation=45)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return _render_plot(fig)
