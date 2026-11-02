# Màu và style dùng chung cho các biểu đồ trong notebook 04 và README.
# 4 màu chính đã kiểm tra phân biệt được với người mù màu và đủ tương phản trên nền kem.
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams

GOLD       = "#b07d00"   # v2, Uptrend
BLUE       = "#2f63a8"   # bản gốc, Downtrend
TEAL       = "#1f9a8a"
RED        = "#c4473a"
GOLD_LIGHT = "#f1d27a"
GOLD_PALE  = "#f8ecc4"
GRAY       = "#a39c8c"   # benchmark
SURFACE    = "#fbf8f1"
INK        = "#2b2618"
INK_2      = "#5c5547"
MUTED      = "#8a8170"
GRID       = "#ece5d3"
AXIS       = "#cfc6b0"

PALETTE = [GOLD, BLUE, TEAL, RED]


def set_theme():
    rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "figure.dpi": 110, "savefig.dpi": 160,
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"], "font.size": 10,
        "text.color": INK, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 20, "axes.axisbelow": True,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "lines.linewidth": 2.0, "legend.frameon": False, "legend.fontsize": 9,
        "figure.titlesize": 14, "figure.titleweight": "bold",
    })


def subtitle(ax, text):
    ax.text(0, 1.01, text, transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")


def save(fig, name, fig_dir):
    os.makedirs(fig_dir, exist_ok=True)
    path = os.path.join(fig_dir, name)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25)
    return path
