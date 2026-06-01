# Valentina Rodriguez Sepulveda — 1125789977
# utils/settings.py — Preferencias de unidades de medida (temperatura y velocidad)
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

# ── Estado global de unidades ─────────────────────────────────────────────────
# ⚠️ IMPORTANTE: Estas variables son "globales" (existen una sola vez en toda
# la app) porque la preferencia de unidades debe mantenerse aunque el usuario
# navegue entre ventanas. Si cambia °C → °F en la pantalla principal, al ir
# al historial debe seguir en °F. Por eso NO están dentro de una clase.
# Se mantiene en memoria durante la sesión; se reinicia al cerrar la app.

_unidad_temperatura: str = "C"   # "C" | "F"
_unidad_velocidad: str = "kmh"   # "kmh" | "mph"


# ── Getters / Setters ─────────────────────────────────────────────────────────

def obtener_unidad_temperatura() -> str:
    return _unidad_temperatura


def obtener_unidad_velocidad() -> str:
    return _unidad_velocidad


def establecer_unidad_temperatura(unidad: str) -> None:
    global _unidad_temperatura
    _unidad_temperatura = unidad


def establecer_unidad_velocidad(unidad: str) -> None:
    global _unidad_velocidad
    _unidad_velocidad = unidad


# ── Conversores ───────────────────────────────────────────────────────────────

def convertir_temperatura(valor: float | None) -> float | None:
    """Convierte °C al sistema activo. Devuelve None si el valor es None."""
    if valor is None:
        return None
    return round(valor * 9 / 5 + 32, 1) if _unidad_temperatura == "F" else round(float(valor), 1)


def convertir_velocidad(valor: float | None) -> float | None:
    """Convierte km/h al sistema activo. Devuelve None si el valor es None."""
    if valor is None:
        return None
    return round(float(valor) * 0.621371, 1) if _unidad_velocidad == "mph" else round(float(valor), 1)


# ── Etiquetas ─────────────────────────────────────────────────────────────────

def simbolo_temperatura() -> str:
    return "°F" if _unidad_temperatura == "F" else "°C"


def simbolo_velocidad() -> str:
    return "mph" if _unidad_velocidad == "mph" else "km/h"
