# Valentina Rodriguez Sepulveda — 1125789977
# utils/api_client.py — Comunicación con la API Open-Meteo
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import requests
import pandas as pd

# ── URLs de la API ────────────────────────────────────────────────────────────

_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL  = "https://api.open-meteo.com/v1/forecast"
_ARCHIVE_URL   = "https://archive-api.open-meteo.com/v1/archive"
_TIMEOUT       = 10  # segundos

# ── Mapa de códigos WMO ───────────────────────────────────────────────────────

WMO_CODES: dict[int, tuple[str, str]] = {
    0:  ("Cielo despejado",            "sunny"),
    1:  ("Mayormente despejado",        "sunny"),
    2:  ("Parcialmente nublado",        "partly_cloudy"),
    3:  ("Nublado",                     "cloudy"),
    45: ("Niebla",                      "fog"),
    48: ("Niebla con escarcha",         "fog"),
    51: ("Llovizna ligera",             "drizzle"),
    53: ("Llovizna moderada",           "drizzle"),
    55: ("Llovizna intensa",            "drizzle"),
    61: ("Lluvia ligera",               "rain"),
    63: ("Lluvia moderada",             "rain"),
    65: ("Lluvia intensa",              "rain"),
    71: ("Nevada ligera",               "snow"),
    73: ("Nevada moderada",             "snow"),
    75: ("Nevada intensa",              "snow"),
    80: ("Chubascos ligeros",           "rain"),
    81: ("Chubascos moderados",         "rain"),
    82: ("Chubascos fuertes",           "rain"),
    95: ("Tormenta eléctrica",          "thunderstorm"),
    96: ("Tormenta con granizo",        "thunderstorm"),
    99: ("Tormenta fuerte con granizo", "thunderstorm"),
}

# ── Funciones públicas ────────────────────────────────────────────────────────

def geocode_city(ciudad: str) -> dict | None:
    """
    Retorna un dict con las claves 'name', 'country', 'latitude', 'longitude'
    para la ciudad dada, o None si no se encuentra o hay error de red.
    """
    params = {"name": ciudad, "count": 1, "language": "es", "format": "json"}
    try:
        resp = requests.get(_GEOCODING_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results")
        if not results:
            return None
        r = results[0]
        return {
            "name":      r.get("name", ciudad),
            "country":   r.get("country", ""),
            "latitude":  r["latitude"],
            "longitude": r["longitude"],
        }
    except requests.RequestException:
        return None


def _get_weather_from_geo(geo: dict) -> dict | None:
    """Obtiene clima actual dado un dict de geocodificación (name/country/lat/lon)."""
    params = {
        "latitude":      geo["latitude"],
        "longitude":     geo["longitude"],
        "current":       (
            "temperature_2m,apparent_temperature,"
            "relative_humidity_2m,wind_speed_10m,weathercode"
        ),
        "daily":         "temperature_2m_max,temperature_2m_min",
        "timezone":      "auto",
        "forecast_days": 1,
    }
    try:
        resp = requests.get(_FORECAST_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data    = resp.json()
        current = data.get("current", {})
        daily   = data.get("daily", {})
        code    = current.get("weathercode", 0)
        descripcion, icono = WMO_CODES.get(code, ("Desconocido", "unknown"))
        return {
            "ciudad":            geo["name"],
            "pais":              geo["country"],
            "latitud":           geo["latitude"],
            "longitud":          geo["longitude"],
            "temperatura":       current.get("temperature_2m"),
            "sensacion_termica": current.get("apparent_temperature"),
            "humedad":           current.get("relative_humidity_2m"),
            "viento":            current.get("wind_speed_10m"),
            "codigo_clima":      code,
            "descripcion":       descripcion,
            "icono":             icono,
            "temp_max":          daily.get("temperature_2m_max", [None])[0],
            "temp_min":          daily.get("temperature_2m_min", [None])[0],
        }
    except requests.RequestException:
        return None


def get_current_weather(ciudad: str) -> dict | None:
    """
    Geocodifica la ciudad y retorna sus datos de clima actual.
    Retorna None si la ciudad no se encuentra o hay error de red.
    """
    geo = geocode_city(ciudad)
    if geo is None:
        return None
    return _get_weather_from_geo(geo)


def get_current_weather_from_geo(geo: dict) -> dict | None:
    """
    Versión que recibe un dict de geocodificación ya existente (evita una
    segunda llamada de geocodificación cuando el usuario elige de una lista).
    """
    return _get_weather_from_geo(geo)


def search_cities(ciudad: str, count: int = 5) -> list[dict]:
    """
    Retorna hasta `count` ciudades que coincidan con `ciudad`.
    Cada dict tiene las claves 'name', 'country', 'latitude', 'longitude'.
    Retorna lista vacía si no hay resultados o hay error de red.
    """
    params = {"name": ciudad, "count": count, "language": "es", "format": "json"}
    try:
        resp = requests.get(_GEOCODING_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results") or []
        return [
            {
                "name":      r.get("name", ciudad),
                "country":   r.get("country", ""),
                "latitude":  r["latitude"],
                "longitude": r["longitude"],
            }
            for r in results
        ]
    except requests.RequestException:
        return []


def get_historical(
    ciudad: str,
    lat: float,
    lon: float,
    inicio: str,
    fin: str,
) -> pd.DataFrame | None:
    """
    Retorna un DataFrame con columnas:
    ciudad, fecha, temp_max, temp_min, precipitacion, viento_max
    para el rango de fechas dado (formato YYYY-MM-DD).
    Usa el endpoint de forecast con past_days (hasta 92 días atrás).
    Retorna None si hay error de red o no hay datos en el rango.
    """
    from datetime import date as _date
    today = _date.today()
    start = _date.fromisoformat(inicio)
    past_days = max(1, min((today - start).days + 1, 92))

    params = {
        "latitude":      lat,
        "longitude":     lon,
        "daily":         "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone":      "auto",
        "past_days":     past_days,
        "forecast_days": 0,
    }
    try:
        resp = requests.get(_FORECAST_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})
        df = pd.DataFrame({
            "ciudad":        ciudad,
            "fecha":         daily.get("time", []),
            "temp_max":      daily.get("temperature_2m_max", []),
            "temp_min":      daily.get("temperature_2m_min", []),
            "precipitacion": daily.get("precipitation_sum", []),
            "viento_max":    daily.get("wind_speed_10m_max", []),
        })
        df = df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)].reset_index(drop=True)
        return df if not df.empty else None
    except requests.RequestException:
        return None
