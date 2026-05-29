# Valentina Rodriguez Sepulveda — 1125789977
# utils/chart_generator.py — Generación de gráficas con matplotlib
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Backend sin GUI — obligatorio antes de importar pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────

_CHARTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "charts"
_CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Paleta ────────────────────────────────────────────────────────────────────

_COLOR_MAX  = "#EF5350"  # rojo cálido — temperatura máxima
_COLOR_MIN  = "#42A5F5"  # azul cielo  — temperatura mínima
_COLOR_PREC = "#29B6F6"  # celeste     — precipitación

# ── Funciones públicas ────────────────────────────────────────────────────────

def chart_temperatura(df: pd.DataFrame, ciudad: str) -> str:
    """
    Genera una gráfica de líneas con temperatura máxima y mínima diaria.
    Retorna la ruta absoluta (str) del PNG guardado en assets/charts/.
    """
    data = df.copy()
    data["fecha"] = pd.to_datetime(data["fecha"])

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        data["fecha"], data["temp_max"],
        color=_COLOR_MAX, linewidth=2, label="Temp. máxima (°C)",
        marker="o", markersize=3,
    )
    ax.plot(
        data["fecha"], data["temp_min"],
        color=_COLOR_MIN, linewidth=2, label="Temp. mínima (°C)",
        marker="o", markersize=3,
    )
    ax.fill_between(data["fecha"], data["temp_min"], data["temp_max"], alpha=0.12, color=_COLOR_MIN)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.set_title(f"Temperatura — {ciudad}", fontsize=14, fontweight="bold", color="#1565C0")
    ax.set_ylabel("°C")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()

    out_path = _CHARTS_DIR / f"temperatura_{ciudad.lower().replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


def chart_precipitacion(df: pd.DataFrame, ciudad: str) -> str:
    """
    Genera una gráfica de barras con la lluvia acumulada por día (mm).
    Cada barra = milímetros de agua caída ese día. 0 mm = día sin lluvia.
    Retorna la ruta absoluta (str) del PNG guardado en assets/charts/.
    """
    data = df.copy()
    data["fecha"] = pd.to_datetime(data["fecha"])
    data["precipitacion"] = pd.to_numeric(data["precipitacion"], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(data["fecha"], data["precipitacion"], color=_COLOR_PREC, width=0.8, edgecolor="white")

    # Anotación cuando no hubo lluvia en todo el período
    if data["precipitacion"].sum() == 0:
        ax.text(
            0.5, 0.5,
            "Sin precipitación registrada en este período",
            transform=ax.transAxes,
            ha="center", va="center",
            fontsize=12, color="#90A4AE", style="italic",
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.set_title(f"Lluvia diaria acumulada — {ciudad}", fontsize=14, fontweight="bold", color="#1565C0")
    ax.set_ylabel("Precipitación (mm)")
    ax.set_xlabel("Cada barra = lluvia caída ese día  ·  0 mm = día sin lluvia")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    out_path = _CHARTS_DIR / f"precipitacion_{ciudad.lower().replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)
