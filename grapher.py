import os
import logging
from datetime import datetime, timezone
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import Config
from crypto import SecurePayload

logger = logging.getLogger(__name__)


class DataStore:
    def __init__(self):
        self.data = deque(maxlen=Config.MAX_DATA_POINTS)

    def add_point(self, x, y):
        self.data.append((x, y))

    def get_all(self):
        return list(self.data)

    def clear(self):
        self.data.clear()


class Grapher:
    def __init__(self, output_path=None):
        self.output_path = output_path or Config.GRAPH_OUTPUT
        self.secure = SecurePayload()
        self.dpi = Config.GRAPH_DPI
        self.figsize = Config.GRAPH_FIGSIZE
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        if Config.PI_OPTIMIZED:
            logger.info(f"Raspberry Pi optimizado: DPI={self.dpi}, figsize={self.figsize}")

    def plot(self, data_store, title="Datos en Tiempo Real"):
        points = data_store.get_all()
        if not points:
            return None

        xs, ys = zip(*points)

        fig, ax = plt.subplots(figsize=self.figsize, facecolor="#1e1e1e")
        ax.set_facecolor("#252526")

        ax.plot(xs, ys, color="#00ff88", linewidth=2, marker="o", markersize=4,
                markerfacecolor="#00cc66", markeredgecolor="none", alpha=0.85)

        ax.fill_between(xs, ys, alpha=0.15, color="#00ff88")

        ax.set_title(self.secure.cipher.encrypt(title),
                     color="#e0e0e0", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel(self.secure.cipher.encrypt("Tiempo / Indice"),
                      color="#b0b0b0", fontsize=11)
        ax.set_ylabel(self.secure.cipher.encrypt("Valor"),
                      color="#b0b0b0", fontsize=11)

        ax.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax.tick_params(colors="#b0b0b0", which="both")

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            encrypted = self.secure.cipher.encrypt(label.get_text())
            label.set_text(encrypted)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#444444")
        ax.spines["bottom"].set_color("#444444")

        timestamp_enc = self.secure.cipher.encrypt(
            f"Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        fig.text(0.99, 0.01, timestamp_enc, ha="right", va="bottom",
                 fontsize=8, color="#666666", style="italic")

        fig.tight_layout()
        fig.savefig(self.output_path, dpi=self.dpi, bbox_inches="tight",
                    facecolor="#1e1e1e")
        plt.close(fig)

        logger.info(f"Grafico guardado en {self.output_path}")
        return self.output_path
