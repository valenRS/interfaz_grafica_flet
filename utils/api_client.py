# Valentina Rodriguez Sepulveda — 1125789977
# utils/api_client.py — Comunicación con la API Open-Meteo
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import requests
import pandas as pd

# ── URLs de la API ────────────────────────────────────────────────────────────
# Open-Meteo es un servicio gratuito que responde preguntas sobre el clima.
# Tiene varios "endpoints" (URLs) para distintos tipos de consulta.

_URL_GEOCODIFICACION     = "https://geocoding-api.open-meteo.com/v1/search"
"""Convierte el nombre de una ciudad en coordenadas (latitud, longitud)."""

_URL_PRONOSTICO          = "https://api.open-meteo.com/v1/forecast"
"""Devuelve el clima actual y el pronóstico de los próximos días."""

_URL_ARCHIVO_HISTORICO   = "https://archive-api.open-meteo.com/v1/archive"
"""Devuelve datos meteorológicos de fechas pasadas (historial)."""

_TIEMPO_ESPERA_SEGUNDOS  = 10
"""Si la API no responde en esta cantidad de segundos, abortamos la consulta."""

# ── Mapa de códigos WMO ───────────────────────────────────────────────────────
# La Organización Meteorológica Mundial (WMO) asigna un número a cada tipo de clima.
# Aquí traducimos ese número a texto en español y a una clave de ícono.
# Fuente: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

CODIGOS_WMO: dict[int, tuple[str, str]] = {
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

def geocodificar_ciudad(ciudad: str) -> dict | None:
    """
    Retorna un dict con las claves 'name', 'country', 'latitude', 'longitude'
    para la ciudad dada, o None si no se encuentra o hay error de red.
    """
    params = {"name": ciudad, "count": 1, "language": "es", "format": "json"}
    try:
        resp = requests.get(_URL_GEOCODIFICACION, params=params, timeout=_TIEMPO_ESPERA_SEGUNDOS)
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
    except requests.Timeout:
        # ⚠️ El servidor no respondió en _TIEMPO_ESPERA_SEGUNDOS segundos
        return None
    except requests.ConnectionError:
        # ⚠️ No hay conexión a internet (cable desconectado, WiFi apagado)
        return None
    except requests.HTTPError:
        # ⚠️ El servidor respondió pero con un código de error (404, 500, etc.)
        return None
    except requests.RequestException:
        # ⚠️ Otro error de red no previsto
        return None


def _consultar_clima_desde_geo(geo: dict) -> dict | None:
    """
    Obtiene el clima actual a partir de un diccionario de geocodificación
    (que ya tiene name/country/lat/lon). Traduce toda la respuesta JSON
    de Open-Meteo a un diccionario con claves en español.

    Parámetros que enviamos a la API (Open-Meteo los exige en inglés):
      current                      → grupo de variables del clima EN ESTE MOMENTO
        temperature_2m             → temperatura a 2 metros del suelo (°C)
        apparent_temperature       → sensación térmica / temperatura aparente (°C)
        relative_humidity_2m       → humedad relativa a 2 metros (%)
        wind_speed_10m             → velocidad del viento a 10 metros (km/h)
        weathercode                → código numérico WMO de la condición climática
      daily                        → grupo de variables DEL DÍA DE HOY
        temperature_2m_max         → temperatura máxima diaria a 2 m (°C)
        temperature_2m_min         → temperatura mínima diaria a 2 m (°C)
      timezone                     → zona horaria ("auto" = la de la ubicación)
      forecast_days                → cuántos días de pronóstico (1 = solo hoy)
    """
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
        resp = requests.get(_URL_PRONOSTICO, params=params, timeout=_TIEMPO_ESPERA_SEGUNDOS)
        resp.raise_for_status()
        data    = resp.json()
        current = data.get("current", {})
        daily   = data.get("daily", {})
        code    = current.get("weathercode", 0)
        descripcion, icono = CODIGOS_WMO.get(code, ("Desconocido", "unknown"))
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
    except requests.Timeout:
        # ⚠️ La API no respondió a tiempo — posiblemente el servidor está lento
        return None
    except requests.ConnectionError:
        # ⚠️ No hay internet — no se puede consultar el clima
        return None
    except requests.HTTPError:
        # ⚠️ La API devolvió un error HTTP (ej. coordenadas inválidas)
        return None
    except requests.RequestException:
        # ⚠️ Cualquier otro error de red inesperado
        return None


def obtener_clima_actual(ciudad: str) -> dict | None:
    """
    Geocodifica la ciudad y retorna sus datos de clima actual.
    Retorna None si la ciudad no se encuentra o hay error de red.
    """
    geo = geocodificar_ciudad(ciudad)
    if geo is None:
        return None
    return _consultar_clima_desde_geo(geo)


def obtener_clima_actual_desde_geo(geo: dict) -> dict | None:
    """
    Versión que recibe un dict de geocodificación ya existente (evita una
    segunda llamada de geocodificación cuando el usuario elige de una lista).
    """
    return _consultar_clima_desde_geo(geo)


def buscar_ciudades(ciudad: str, cantidad: int = 5) -> list[dict]:
    """
    Retorna hasta `cantidad` ciudades que coincidan con `ciudad`.
    Cada dict tiene las claves 'name', 'country', 'latitude', 'longitude'.
    Retorna lista vacía si no hay resultados o hay error de red.
    """
    params = {"name": ciudad, "count": cantidad, "language": "es", "format": "json"}
    try:
        resp = requests.get(_URL_GEOCODIFICACION, params=params, timeout=_TIEMPO_ESPERA_SEGUNDOS)
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
    except requests.Timeout:
        # ⚠️ La API de geocodificación tardó demasiado en responder
        return []
    except requests.ConnectionError:
        # ⚠️ No hay conexión a internet
        return []
    except requests.HTTPError:
        # ⚠️ La API respondió con un error HTTP
        return []
    except requests.RequestException:
        return []


def obtener_historial(
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

    Parámetros que enviamos a la API de archivo histórico de Open-Meteo:
      daily                        → grupo de variables diarias históricas
        temperature_2m_max         → temperatura máxima diaria a 2 m (°C)
        temperature_2m_min         → temperatura mínima diaria a 2 m (°C)
        precipitation_sum          → precipitación acumulada diaria (mm).
                                    1 mm = 1 litro de agua por metro cuadrado.
        wind_speed_10m_max         → velocidad máxima diaria del viento (km/h)

    Retorna None si hay error de red o no hay datos en el rango.
    """
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "daily":      "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone":   "auto",
        "start_date": inicio,
        "end_date":   fin,
    }
    try:
        resp = requests.get(_URL_ARCHIVO_HISTORICO, params=params, timeout=_TIEMPO_ESPERA_SEGUNDOS)
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
    except requests.Timeout:
        # ⚠️ El servidor de archivo histórico no respondió a tiempo
        return None
    except requests.ConnectionError:
        # ⚠️ No hay conexión a internet para consultar el historial
        return None
    except requests.HTTPError:
        # ⚠️ La API devolvió un error HTTP
        return None
    except requests.RequestException:
        return None
