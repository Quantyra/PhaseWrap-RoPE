"""Generate QRoPE publication figures from repository evidence files.

This script is intentionally read-only with respect to evidence data. It turns
the frozen Stage 4 packet, evaluation JSON, and replication ledger into
publication assets under docs/publication/figures/.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from qiskit import QuantumCircuit


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "publication" / "figures"
STAGE4 = ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_packet"
REPLICATION = ROOT / "logs" / "automated_stage_gates" / "replication_lanes"

INK = "#15211f"
MUTED = "#66736e"
PAPER = "#fbf7ef"
PANEL = "#fffdf8"
TEAL = "#0f766e"
AMBER = "#b7791f"
BLUE = "#2f5d86"
RED = "#9f3a38"
GRID = "#d8d1c3"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def set_common_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": PAPER,
            "axes.facecolor": PANEL,
            "axes.edgecolor": "#cfc6b6",
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": GRID,
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "savefig.facecolor": PAPER,
            "savefig.bbox": "tight",
        }
    )


def save(fig: plt.Figure, filename: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / filename, dpi=220)
    plt.close(fig)


def add_source_note(fig: plt.Figure, text: str) -> None:
    fig.text(0.01, 0.012, text, color=MUTED, fontsize=9)


def draw_circuit(filename: str, *, entangling: bool) -> None:
    packet = load_json(STAGE4 / "frozen_packet.json")
    row = packet["rows"][0]
    params = row["circuit_parameters"]

    circuit = QuantumCircuit(2)
    circuit.ry(params["ry_q0"], 0)
    circuit.ry(params["ry_q1"], 1)
    if entangling:
        circuit.cx(0, 1)
    circuit.measure_all()

    fig = circuit.draw(output="mpl", fold=-1, idle_wires=False)
    fig.set_size_inches(10.5, 3.4)
    fig.set_facecolor(PAPER)
    title = "QRoPE entangling CX witness circuit" if entangling else "QRoPE product-state witness circuit"
    subtitle = "Circuit parameters shown for the first frozen Stage 4 packet row."
    fig.suptitle(title, x=0.02, y=0.98, ha="left", va="top", fontsize=16, fontweight="bold", color=INK)
    fig.text(0.02, 0.88, subtitle, ha="left", va="top", fontsize=10, color=MUTED)
    save(fig, filename)


def stage4_prediction_chart() -> None:
    evaluation = load_json(STAGE4 / "evaluation.json")
    rows = evaluation["per_row_results"]
    x = np.arange(len(rows))
    labels = np.array([row["label"] for row in rows], dtype=float)
    witness = np.array([row["hardware_predictions"]["witness"] for row in rows], dtype=float)
    control = np.array([row["hardware_predictions"]["control"] for row in rows], dtype=float)
    witness_error = np.abs(witness - labels)
    control_error = np.abs(control - labels)

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(12.5, 8.2),
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.22},
    )
    fig.suptitle("Stage 4 packet: labels, witness predictions, and control predictions", x=0.01, ha="left", fontsize=18, fontweight="bold", color=INK)
    fig.text(0.01, 0.935, "Single IBM hardware packet, 16 rows, 4096 shots per row. This is not a cross-backend claim.", color=MUTED, fontsize=10)

    ax_top.plot(x, labels, color=INK, linewidth=2.2, marker="o", markersize=5, label="Frozen label")
    ax_top.plot(x, witness, color=TEAL, linewidth=2.0, marker="o", markersize=5, label=f"Witness MAE {evaluation['witness']['mae']:.3f}")
    ax_top.plot(x, control, color=AMBER, linewidth=2.0, marker="s", markersize=5, label=f"Control MAE {evaluation['control']['mae']:.3f}")
    ax_top.set_ylabel("Normalized score")
    ax_top.set_ylim(-0.03, 1.03)
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([str(i) for i in x])
    ax_top.grid(True, axis="y", linestyle="--", linewidth=0.7)
    ax_top.legend(loc="upper left", frameon=False, ncol=3)

    width = 0.38
    ax_bottom.bar(x - width / 2, witness_error, width=width, color=TEAL, label="Witness abs. error")
    ax_bottom.bar(x + width / 2, control_error, width=width, color=AMBER, label="Control abs. error")
    ax_bottom.set_ylabel("Absolute error")
    ax_bottom.set_xlabel("Frozen packet row")
    ax_bottom.set_xticks(x)
    ax_bottom.set_xticklabels([str(i) for i in x])
    ax_bottom.grid(True, axis="y", linestyle="--", linewidth=0.7)
    ax_bottom.legend(loc="upper left", frameon=False, ncol=2)

    add_source_note(fig, "Source: logs/automated_stage_gates/stage4_hardware_packet/evaluation.json")
    save(fig, "qrope-stage4-predictions-v1.png")


def stage4_metric_chart() -> None:
    evaluation = load_json(STAGE4 / "evaluation.json")
    labels = ["Witness", "Control"]
    mae = [evaluation["witness"]["mae"], evaluation["control"]["mae"]]
    rank = [evaluation["witness"]["rank_correlation"], evaluation["control"]["rank_correlation"]]
    colors = [TEAL, AMBER]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.8), gridspec_kw={"wspace": 0.28})
    fig.suptitle("Stage 4 summary metrics", x=0.01, ha="left", fontsize=18, fontweight="bold", color=INK)
    fig.text(0.01, 0.91, "Witness versus additive single-band readout control for the published frozen packet.", color=MUTED, fontsize=10)

    axes[0].bar(labels, mae, color=colors, width=0.58)
    axes[0].set_title("Mean absolute error")
    axes[0].set_ylabel("MAE, lower is better")
    axes[0].set_ylim(0, max(mae) * 1.32)
    axes[0].grid(True, axis="y", linestyle="--", linewidth=0.7)
    for idx, value in enumerate(mae):
        axes[0].text(idx, value + max(mae) * 0.035, f"{value:.3f}", ha="center", va="bottom", fontweight="bold", color=INK)

    axes[1].bar(labels, rank, color=colors, width=0.58)
    axes[1].axhline(0, color="#8c8375", linewidth=1.2)
    axes[1].set_title("Rank correlation")
    axes[1].set_ylabel("Spearman rank correlation, higher is better")
    axes[1].set_ylim(-0.32, 1.02)
    axes[1].grid(True, axis="y", linestyle="--", linewidth=0.7)
    for idx, value in enumerate(rank):
        offset = 0.045 if value >= 0 else -0.075
        va = "bottom" if value >= 0 else "top"
        axes[1].text(idx, value + offset, f"{value:.3f}", ha="center", va=va, fontweight="bold", color=INK)

    add_source_note(fig, "Source: logs/automated_stage_gates/stage4_hardware_packet/evaluation.json")
    save(fig, "qrope-stage4-metrics-v1.png")


def replication_status_chart() -> None:
    ledger = load_json(REPLICATION / "replication-ledger.json")
    lanes = ledger["lanes"]
    names = {
        "stage4-product-original": "Product original",
        "product-rerun-a": "Product rerun A",
        "product-rerun-b": "Product rerun B",
        "cx-rerun-a": "CX rerun A",
        "cx-rerun-b": "CX rerun B",
    }
    status_text = {
        "published_completed": "Completed and published",
        "blocked_pending_credentials_and_backend_selection": "Blocked: credentials/backend",
        "implemented_not_executed_on_hardware": "Implemented, not executed",
    }
    status_color = {
        "published_completed": TEAL,
        "blocked_pending_credentials_and_backend_selection": RED,
        "implemented_not_executed_on_hardware": BLUE,
    }

    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    fig.suptitle("Replication lane status", x=0.01, ha="left", fontsize=18, fontweight="bold", color=INK)
    fig.text(0.01, 0.92, "Only the original product-state hardware packet is completed. CX and cross-backend lanes remain outside the evidence claim.", color=MUTED, fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.75, len(lanes) - 0.25)
    ax.axis("off")

    for idx, lane in enumerate(reversed(lanes)):
        y = idx
        status = lane["status"]
        color = status_color.get(status, MUTED)
        box = FancyBboxPatch(
            (0.02, y - 0.32),
            0.96,
            0.62,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            linewidth=1.1,
            edgecolor="#cfc6b6",
            facecolor=PANEL,
        )
        ax.add_patch(box)
        ax.scatter([0.07], [y], s=170, color=color, edgecolor="white", linewidth=1.4, zorder=3)
        ax.text(0.12, y + 0.11, names.get(lane["lane_id"], lane["lane_id"]), ha="left", va="center", color=INK, fontsize=12, fontweight="bold")
        ax.text(0.12, y - 0.12, lane.get("circuit_family", lane.get("target", "")), ha="left", va="center", color=MUTED, fontsize=9)
        ax.text(0.72, y + 0.08, status_text.get(status, status), ha="left", va="center", color=color, fontsize=10, fontweight="bold")
        if "backend" in lane:
            detail = f"{lane['backend']} | {lane.get('date_utc', '')} | {lane.get('outcome', '')}"
        else:
            detail = lane.get("target", "")
        ax.text(0.72, y - 0.14, detail, ha="left", va="center", color=MUTED, fontsize=8.5)

    add_source_note(fig, "Source: logs/automated_stage_gates/replication_lanes/replication-ledger.json")
    save(fig, "qrope-replication-status-v1.png")


def main() -> None:
    set_common_style()
    draw_circuit("qrope-product-state-circuit-v1.png", entangling=False)
    draw_circuit("qrope-cx-witness-circuit-v1.png", entangling=True)
    stage4_prediction_chart()
    stage4_metric_chart()
    replication_status_chart()


if __name__ == "__main__":
    main()
