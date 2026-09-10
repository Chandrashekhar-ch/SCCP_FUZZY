"""
Generates formal patent-style drawings (black & white, numbered reference
labels) for the patent draft:

  FIG. 1  System block diagram
  FIG. 2  Method flowchart
  FIG. 3A Input membership function diagram (pH) - patent B/W style
  FIG. 3B Output membership function diagram (WPI) - patent B/W style
  FIG. 4  Hardware / deployment diagram

Run from project root: python docs/generate_patent_figures.py
Output: outputs/figures/patent_fig*.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = "outputs/figures"
os.makedirs(OUT, exist_ok=True)

BOX_KW = dict(boxstyle="round,pad=0.35,rounding_size=0.06", linewidth=1.4,
              edgecolor="black", facecolor="white")


def box(ax, x, y, w, h, text, ref=None, fontsize=10.5, textweight="normal"):
    p = FancyBboxPatch((x, y), w, h, **BOX_KW)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, weight=textweight, family="DejaVu Sans", wrap=True)
    if ref is not None:
        ax.text(x + w - 0.05, y + h + 0.05, str(ref), ha="right", va="bottom",
                 fontsize=9.5, style="italic")
    return p


def arrow(ax, xy_from, xy_to, style="-|>", lw=1.3, connectionstyle="arc3,rad=0.0"):
    a = FancyArrowPatch(xy_from, xy_to, arrowstyle=style, mutation_scale=14,
                         linewidth=lw, color="black", connectionstyle=connectionstyle)
    ax.add_patch(a)


def new_ax(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 10)
    ax.axis("off")
    return fig, ax


# ══════════════════════════════════════════════════════════════════════
# FIG. 1 — System Block Diagram
# ══════════════════════════════════════════════════════════════════════
fig, ax = new_ax((9, 11))
ax.set_ylim(0, 14)

# Outer system boundary
outer = FancyBboxPatch((0.3, 0.4), 9.4, 13.0, boxstyle="round,pad=0.1,rounding_size=0.05",
                        linewidth=1.0, edgecolor="black", facecolor="none", linestyle="dashed")
ax.add_patch(outer)
ax.text(9.6, 13.55, "SYSTEM (100)", ha="right", fontsize=10, style="italic")

# Sensor array boundary
sarr = FancyBboxPatch((0.7, 10.9), 8.6, 2.2, boxstyle="round,pad=0.1,rounding_size=0.05",
                       linewidth=1.0, edgecolor="black", facecolor="none", linestyle="dashed")
ax.add_patch(sarr)
ax.text(0.9, 13.25, "SENSOR ARRAY (102)", fontsize=9.5, style="italic")

sensor_labels = [
    ("pH SENSOR\n(104)", 0.9),
    ("TURBIDITY\nSENSOR (106)", 2.75),
    ("TDS SENSOR\n(108)", 4.6),
    ("DISSOLVED\nOXYGEN\nSENSOR (110)", 6.45),
    ("TEMPERATURE\nSENSOR (112)", 8.3),
]
for label, x in sensor_labels:
    box(ax, x, 11.2, 1.55, 1.55, label, fontsize=8.7)
    arrow(ax, (x + 0.775, 11.2), (5.0, 10.3))

box(ax, 3.0, 9.6, 4.0, 1.0, "SIGNAL ACQUISITION /\nMICROCONTROLLER UNIT (116)", ref=None, fontsize=9.3)
arrow(ax, (5.0, 9.6), (5.0, 8.85))

box(ax, 2.7, 7.85, 4.6, 1.0, "PREPROCESSING MODULE (114)\n(temp. compensation, outlier\nrejection, moving-average filter)", fontsize=8.6)
arrow(ax, (5.0, 7.85), (5.0, 7.15))

ax.text(5.0, 7.15, "FUZZY INFERENCE ENGINE (118)", fontsize=10, weight="bold", ha="center")

box(ax, 3.0, 5.75, 4.0, 1.0, "FUZZIFICATION UNIT (120)", fontsize=8.9)
arrow(ax, (5.0, 5.75), (5.0, 5.05))

box(ax, 3.0, 4.05, 4.0, 1.0, "RULE EVALUATION UNIT (122)", fontsize=8.9)
box(ax, 7.4, 3.9, 1.7, 1.3, "RULE\nBASE\n(123)\n45 RULES", fontsize=7.8)
arrow(ax, (7.4, 4.55), (7.0, 4.55))
arrow(ax, (5.0, 4.05), (5.0, 3.35))

box(ax, 3.0, 2.35, 4.0, 1.0, "AGGREGATION & DEFUZZIFICATION\nUNIT (124)", fontsize=8.3)
arrow(ax, (5.0, 2.35), (5.0, 1.65))

box(ax, 3.0, 0.65, 4.0, 1.0, "WATER POTABILITY INDEX\n(WPI) CLASSIFIER (126)", fontsize=8.8)
arrow(ax, (5.0, 0.65), (5.0, -0.05))

box(ax, 2.6, -1.05, 4.8, 1.0, "DISPLAY / DASHBOARD\nUNIT (128)", fontsize=8.8)

fis = FancyBboxPatch((2.6, 2.2), 6.9, 4.65, boxstyle="round,pad=0.1,rounding_size=0.05",
                      linewidth=1.0, edgecolor="black", facecolor="none", linestyle="dotted")
ax.add_patch(fis)

fig.suptitle("FIG. 1", fontsize=13, weight="bold", y=0.99)
ax.set_ylim(-1.5, 14.3)
plt.tight_layout()
plt.savefig(f"{OUT}/patent_fig1.png", dpi=300, bbox_inches="tight", pad_inches=0.3)
plt.close()

# ══════════════════════════════════════════════════════════════════════
# FIG. 2 — Method Flowchart
# ══════════════════════════════════════════════════════════════════════
fig, ax = new_ax((7.5, 12))
ax.set_ylim(0, 15)

steps = [
    ("START (200)", "oval"),
    ("ACQUIRE RAW SENSOR\nREADINGS (202)", "box"),
    ("APPLY TEMPERATURE\nCOMPENSATION (204)", "box"),
    ("REJECT OUTLIERS &\nFILTER NOISE (206)", "box"),
    ("FUZZIFY CRISP INPUTS\nINTO MEMBERSHIP\nDEGREES (208)", "box"),
    ("EVALUATE RULE BASE\n(MIN IMPLICATION) (210)", "box"),
    ("AGGREGATE ACTIVATED\nRULES (MAX OPERATOR) (212)", "box"),
    ("DEFUZZIFY VIA\nCENTROID OF AREA (214)", "box"),
    ("CLASSIFY WPI AS NON-\nPOTABLE / MARGINAL /\nPOTABLE (216)", "box"),
    ("OUTPUT RESULT TO\nDASHBOARD (218)", "box"),
]

y = 14.0
positions = []
for label, shape in steps:
    if shape == "oval":
        p = FancyBboxPatch((3.0, y - 0.45), 4.0, 0.9, boxstyle="round,pad=0.3,rounding_size=0.45",
                            linewidth=1.4, edgecolor="black", facecolor="white")
        ax.add_patch(p)
        ax.text(5.0, y, label, ha="center", va="center", fontsize=9.5)
    else:
        box(ax, 2.7, y - 0.55, 4.6, 1.1, label, fontsize=8.8)
    positions.append(y)
    y -= 1.55

for i in range(len(positions) - 1):
    arrow(ax, (5.0, positions[i] - 0.55), (5.0, positions[i + 1] + 0.55))

# Loop-back arrow indicating continuous real-time operation
arrow(ax, (7.3, positions[-1]), (7.3, positions[1]), connectionstyle="arc3,rad=0.0")
arrow(ax, (7.3, positions[1]), (5.0 + 4.6 / 2, positions[1]))
ax.text(7.45, (positions[-1] + positions[1]) / 2, "REPEAT\n(REAL-TIME\nLOOP)", fontsize=7.8,
        rotation=90, va="center", ha="left")

end_y = positions[-1] - 1.4
p = FancyBboxPatch((3.0, end_y - 0.45), 4.0, 0.9, boxstyle="round,pad=0.3,rounding_size=0.45",
                    linewidth=1.4, edgecolor="black", facecolor="white")
ax.add_patch(p)
ax.text(5.0, end_y, "END (220)", ha="center", va="center", fontsize=9.5)
arrow(ax, (5.0, positions[-1] - 0.55), (5.0, end_y + 0.45))

fig.suptitle("FIG. 2", fontsize=13, weight="bold", y=0.995)
ax.set_ylim(end_y - 1.0, 14.7)
plt.tight_layout()
plt.savefig(f"{OUT}/patent_fig2.png", dpi=300, bbox_inches="tight")
plt.close()

# ══════════════════════════════════════════════════════════════════════
# FIG. 3A / 3B — Membership function diagrams (patent B/W line style)
# ══════════════════════════════════════════════════════════════════════
def trapmf(x, a, b, c, d):
    return np.maximum(0, np.minimum(np.minimum((x - a) / (b - a + 1e-9), 1), (d - x) / (d - c + 1e-9)))


def trimf(x, a, b, c):
    return np.maximum(0, np.minimum((x - a) / (b - a + 1e-9), (c - x) / (c - b + 1e-9)))


pH = np.linspace(0, 14, 1000)
ph_mfs = {
    "ACIDIC": trapmf(pH, 0, 0, 5.0, 6.5),
    "SLIGHTLY ACIDIC": trimf(pH, 5.5, 6.5, 7.2),
    "NEUTRAL": trimf(pH, 6.5, 7.0, 7.8),
    "SLIGHTLY ALKALINE": trimf(pH, 7.2, 8.0, 8.8),
    "ALKALINE": trapmf(pH, 8.2, 9.0, 14, 14),
}
linestyles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1))]
fig, ax = plt.subplots(figsize=(8, 4.2))
for (name, y), ls in zip(ph_mfs.items(), linestyles):
    ax.plot(pH, y, label=name, linewidth=1.8, color="black", linestyle=ls)
ax.set_xlabel("INPUT VARIABLE: pH", fontsize=10)
ax.set_ylabel("DEGREE OF MEMBERSHIP", fontsize=10)
ax.legend(loc="upper right", fontsize=8, framealpha=1)
ax.set_ylim(0, 1.15)
ax.grid(True, linestyle=":", alpha=0.5, color="gray")
fig.suptitle("FIG. 3A", fontsize=13, weight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/patent_fig3a.png", dpi=300, bbox_inches="tight")
plt.close()

wpi = np.linspace(0, 10, 1000)
wpi_mfs = {
    "NON-POTABLE": trapmf(wpi, 0, 0, 2, 3.5),
    "MARGINAL": trimf(wpi, 3, 5, 7),
    "POTABLE": trapmf(wpi, 6.5, 8, 10, 10),
}
fig, ax = plt.subplots(figsize=(8, 4.2))
for (name, y), ls in zip(wpi_mfs.items(), ["-", "--", "-."]):
    ax.plot(wpi, y, label=name, linewidth=1.8, color="black", linestyle=ls)
ax.set_xlabel("OUTPUT VARIABLE: WATER POTABILITY INDEX (WPI)", fontsize=10)
ax.set_ylabel("DEGREE OF MEMBERSHIP", fontsize=10)
ax.legend(loc="upper center", fontsize=8, framealpha=1)
ax.set_ylim(0, 1.15)
ax.grid(True, linestyle=":", alpha=0.5, color="gray")
fig.suptitle("FIG. 3B", fontsize=13, weight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/patent_fig3b.png", dpi=300, bbox_inches="tight")
plt.close()

# ══════════════════════════════════════════════════════════════════════
# FIG. 4 — Hardware / Deployment Diagram
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.set_xlim(-0.3, 10.3)
ax.set_ylim(0, 6)
ax.axis("off")

box(ax, 0.5, 3.6, 2.2, 1.6, "SENSOR ARRAY\n(102)\n[pH, Turbidity,\nTDS, DO, Temp.]", fontsize=8.3)
arrow(ax, (2.7, 4.4), (3.5, 4.4))
box(ax, 3.5, 3.6, 2.2, 1.6, "MICROCONTROLLER\n(ESP32) (116)\nADC + Wi-Fi", fontsize=8.3)
arrow(ax, (5.7, 4.4), (6.5, 4.4))
ax.text(6.1, 4.72, "(130)", fontsize=8, style="italic")
ax.text(6.1, 4.18, "Serial / Wi-Fi\nLink", fontsize=7.3, ha="center")

box(ax, 6.5, 3.6, 2.7, 1.6, "HOST PROCESSING UNIT\n(132)\n[Preprocessing (114) +\nFIS Engine (118)]", fontsize=8.0)

arrow(ax, (7.85, 3.6), (7.85, 2.55))
box(ax, 6.5, 0.9, 2.7, 1.5, "DASHBOARD / CLIENT\nDISPLAY DEVICE (128, 134)\n[Web Browser - Flask +\nWebSocket Interface]", fontsize=7.6)

fig.suptitle("FIG. 4", fontsize=13, weight="bold", y=0.98)
plt.tight_layout()
plt.savefig(f"{OUT}/patent_fig4.png", dpi=300, bbox_inches="tight", pad_inches=0.3)
plt.close()

print("[*] Patent figures generated in outputs/figures/ (patent_fig1..4)")
