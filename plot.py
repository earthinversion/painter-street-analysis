"""Three-panel summary of the Painter Street derived-measurement analysis."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


def draw(results, destination):
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
                         "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 12,
                         "ytick.labelsize": 12, "legend.fontsize": 12,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.8, "pdf.fonttype": 42, "ps.fonttype": 42})
    ink, blue, orange = "#16324F", "#0072B2", "#D55E00"
    features = pd.read_csv(results/"novelty.csv")
    modal = pd.read_csv(results/"frequency_panel.csv")
    curve = pd.read_csv(results/"frequency_curve.csv")
    ins = pd.read_csv(results/"inspection.csv", parse_dates=["inspected"])
    summary = json.loads((results/"summary.json").read_text())
    fig = plt.figure(figsize=(7.2, 7.3), facecolor="white")
    grid = fig.add_gridspec(2, 2, left=0.12, right=0.97, bottom=0.16, top=0.95,
                           hspace=0.60, wspace=0.50, height_ratios=[1, 0.88])
    a, b, c = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, :])

    def points(ax, x, y, frame):
        for mask, marker, face, edge in [
            (frame.reference, "o", "white", ink),
            (~frame.reference & ~frame.novel, "o", blue, blue),
            (~frame.reference & frame.novel, "^", orange, ink)]:
            ax.scatter(np.asarray(x)[mask], np.asarray(y)[mask], s=42,
                       marker=marker, facecolor=face, edgecolor=edge, linewidth=0.8, zorder=4)

    ns = summary["novelty"]
    value, vector = np.linalg.eigh(np.asarray(ns["cov"]))
    angle = np.linspace(0, 2*np.pi, 240)
    ellipse = np.asarray(ns["mean"])[:, None] + vector @ (
        np.sqrt(value*ns["threshold_md2"])[:, None]*np.array([np.cos(angle), np.sin(angle)]))
    a.fill(10**ellipse[1], 10**ellipse[0], color="#DFE9F0", zorder=0)
    a.plot(10**ellipse[1], 10**ellipse[0], color=blue, lw=0.8)
    points(a, features.CAV, features.PRA, features)
    a.set(xscale="log", yscale="log", xlabel="CAV (g s)", ylabel="Peak response (g)")
    a.set_xticks([0.03, 0.3, 3], labels=["0.03", "0.3", "3"])
    a.set_yticks([0.03, 0.3, 1], labels=["0.03", "0.3", "1"])
    a.minorticks_off()
    b.fill_between(curve.pga_input_g, curve.lower_pct, curve.upper_pct, color="0.88", lw=0)
    b.plot(curve.pga_input_g, curve.change_pct, color=ink, lw=1.3)
    b.axhline(0, color="0.7", lw=0.7, zorder=0)
    points(b, modal.pga_input_g, modal.frequency_change_pct, modal)
    b.set(xscale="log", xlabel="Peak input (g)", ylabel="Frequency change (%)")
    b.set_xticks([0.02, 0.1, 1], labels=["0.02", "0.1", "1"])
    b.minorticks_off()
    for component, color, marker, linestyle in [("deck", orange, "o", "-"),
                                               ("superstructure", blue, "s", "--"),
                                               ("substructure", ink, "^", ":")]:
        c.step(ins.inspected, ins[component], where="post", color=color,
               linestyle=linestyle, lw=1.3, label=component.capitalize())
        same = ins[component] == ins[component+"_as_first_published"]
        for mask, fill in [(same, color), (~same, "white")]:
            c.scatter(ins.inspected[mask], ins[component][mask], marker=marker,
                       facecolor=fill, edgecolor=color, s=48, linewidth=1, zorder=4)
    c.set(ylabel="Inspection rating", xlabel="Inspection year", ylim=(4.5, 8.5))
    c.set_yticks([5, 6, 7, 8])
    c.xaxis.set_major_locator(mdates.YearLocator(2))
    c.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    c.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=3, frameon=False,
             handlelength=1.5, columnspacing=1.2)
    for ax, label in zip([a, b, c], ["(a)", "(b)", "(c)"]):
        ax.text(-0.02, 1.04, label, transform=ax.transAxes, weight="bold", ha="left", va="bottom")
    handles = [Line2D([], [], marker=m, mfc=f, mec=e, ls="none", label=l, ms=6)
               for m,f,e,l in [("o","white",ink,"Reference"),("o",blue,blue,"Other test"),
                               ("^",orange,ink,"Outside envelope")]]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.53, 0.505), ncol=3,
               frameon=False, handlelength=1, columnspacing=1)
    destination.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination/"painter-street.pdf", metadata={"Title":"Painter Street Overpass analysis"})
    fig.savefig(destination/"painter-street.png", dpi=450)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    draw(root/"results", root/"figures")
