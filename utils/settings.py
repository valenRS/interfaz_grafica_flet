# Valentina Rodriguez Sepulveda — 1125789977
# utils/settings.py — Preferencias de unidades de medida (temperatura y velocidad)
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

# ── Estado global de unidades ─────────────────────────────────────────────────
# Se mantiene en memoria durante la sesión; se reinicia al cerrar la app.

_temp_unit: str = "C"   # "C" | "F"
_speed_unit: str = "kmh"  # "kmh" | "mph"


# ── Getters / Setters ─────────────────────────────────────────────────────────

def get_temp_unit() -> str:
    return _temp_unit


def get_speed_unit() -> str:
    return _speed_unit


def set_temp_unit(unit: str) -> None:
    global _temp_unit
    _temp_unit = unit


def set_speed_unit(unit: str) -> None:
    global _speed_unit
    _speed_unit = unit


# ── Conversores ───────────────────────────────────────────────────────────────

def convert_temp(value: float | None) -> float | None:
    """Convierte °C al sistema activo. Devuelve None si el valor es None."""
    if value is None:
        return None
    return round(value * 9 / 5 + 32, 1) if _temp_unit == "F" else round(float(value), 1)


def convert_speed(value: float | None) -> float | None:
    """Convierte km/h al sistema activo. Devuelve None si el valor es None."""
    if value is None:
        return None
    return round(float(value) * 0.621371, 1) if _speed_unit == "mph" else round(float(value), 1)


# ── Etiquetas ─────────────────────────────────────────────────────────────────

def temp_symbol() -> str:
    return "°F" if _temp_unit == "F" else "°C"


def speed_symbol() -> str:
    return "mph" if _speed_unit == "mph" else "km/h"
