# Valentina Rodriguez Sepulveda — 1125789977
# utils/chart_generator.py — Generación de gráficas con matplotlib
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Backend sin GUI — obligatorio antes de importar pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────

if getattr(sys, "frozen", False):
    _DIRECTORIO_GRAFICAS = Path(sys.executable).parent / "assets" / "charts"
else:
    _DIRECTORIO_GRAFICAS = Path(__file__).resolve().parent.parent / "assets" / "charts"
_DIRECTORIO_GRAFICAS.mkdir(parents=True, exist_ok=True)

# ── Paleta ────────────────────────────────────────────────────────────────────

_COLOR_TEMP_MAX       = "#EF5350"  # rojo cálido — temperatura máxima
_COLOR_TEMP_MIN       = "#42A5F5"  # azul cielo  — temperatura mínima
_COLOR_PRECIPITACION  = "#29B6F6"  # celeste     — precipitación

# ── Funciones públicas ────────────────────────────────────────────────────────

def chart_temperatura(df: pd.DataFrame, ciudad: str) -> str:
    """
    Genera una gráfica de líneas con temperatura máxima y mínima diaria.
    Retorna la ruta absoluta (str) del PNG guardado en assets/charts/.
    """
    datos = df.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos["temp_max"] = pd.to_numeric(datos["temp_max"], errors="coerce")
    datos["temp_min"] = pd.to_numeric(datos["temp_min"], errors="coerce")

    # ⚠️ Eliminar filas donde no se pudo convertir la temperatura (NaN)
    datos = datos.dropna(subset=["temp_max", "temp_min"])
    if datos.empty:
        raise ValueError(f"No hay datos válidos de temperatura para {ciudad}.")

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        datos["fecha"], datos["temp_max"],
        color=_COLOR_TEMP_MAX, linewidth=2, label="Temp. máxima (°C)",
        marker="o", markersize=3,
    )
    ax.plot(
        datos["fecha"], datos["temp_min"],
        color=_COLOR_TEMP_MIN, linewidth=2, label="Temp. mínima (°C)",
        marker="o", markersize=3,
    )
    ax.fill_between(datos["fecha"], datos["temp_min"], datos["temp_max"], alpha=0.12, color=_COLOR_TEMP_MIN)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.set_title(f"Temperatura — {ciudad}", fontsize=14, fontweight="bold", color="#1565C0")
    ax.set_ylabel("°C")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()

    ruta_archivo = _DIRECTORIO_GRAFICAS / f"temperatura_{ciudad.lower().replace(' ', '_')}.png"
    fig.savefig(ruta_archivo, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return str(ruta_archivo)


def chart_precipitacion(df: pd.DataFrame, ciudad: str) -> str:
    """
    Genera una gráfica de barras con la lluvia acumulada por día (mm).
    Cada barra = milímetros de agua caída ese día. 0 mm = día sin lluvia.
    Retorna la ruta absoluta (str) del PNG guardado en assets/charts/.
    """
    datos = df.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos["precipitacion"] = pd.to_numeric(datos["precipitacion"], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(datos["fecha"], datos["precipitacion"], color=_COLOR_PRECIPITACION, width=0.8, edgecolor="white")

    # Anotación cuando no hubo lluvia en todo el período
    if datos["precipitacion"].sum() == 0:
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

    ruta_archivo = _DIRECTORIO_GRAFICAS / f"precipitacion_{ciudad.lower().replace(' ', '_')}.png"
    fig.savefig(ruta_archivo, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return str(ruta_archivo)
