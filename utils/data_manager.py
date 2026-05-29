# Valentina Rodriguez Sepulveda — 1125789977
# utils/data_manager.py — Lectura y escritura de archivos CSV con pandas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from pathlib import Path

import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USUARIOS_CSV  = DATA_DIR / "usuarios.csv"
CIUDADES_CSV  = DATA_DIR / "ciudades.csv"
HISTORIAL_CSV = DATA_DIR / "historial_clima.csv"
CACHE_CSV     = DATA_DIR / "cache_clima.csv"

_USUARIOS_COLS = ["id", "username", "password_hash", "fecha_registro"]
_CIUDADES_COLS = [
    "id", "username", "ciudad", "pais", "latitud", "longitud",
    "alerta_max_temp", "alerta_min_temp", "alerta_max_temp_f", "alerta_min_temp_f",
    # Último clima consultado (cache offline):
    "temperatura", "temp_max", "temp_min", "sensacion_termica",
    "humedad", "viento", "codigo_clima", "descripcion", "icono", "ultima_consulta",
]

# Columnas de texto en ciudades.csv que deben permanecer como object/str
_CIUDADES_STR_COLS = {"username", "ciudad", "pais", "codigo_clima", "descripcion", "icono", "ultima_consulta"}
_HISTORIAL_COLS = ["id", "ciudad", "fecha", "temp_max", "temp_min", "precipitacion", "viento_max"]
_CACHE_COLS     = [
    "ciudad", "pais", "latitud", "longitud",
    "temperatura", "temp_max", "temp_min", "sensacion_termica",
    "humedad", "viento", "codigo_clima", "descripcion", "icono",
    "ultima_consulta",
]

# ── Helpers privados ──────────────────────────────────────────────────────────

def _read_csv(path: Path, cols: list, str_cols: set | None = None) -> pd.DataFrame:
    """Lee un CSV; si no existe o está vacío retorna un DataFrame con las columnas indicadas.

    Args:
        str_cols: conjunto de nombres de columnas que deben mantenerse como dtype object
                  (string). Evita que pandas infiera float64 en columnas vacías de texto.
    """
    if path.exists() and path.stat().st_size > 0:
        dtype_map = {col: object for col in str_cols if col in cols} if str_cols else None
        df = pd.read_csv(path, dtype=dtype_map)
        # Migración automática: añadir columnas nuevas que no existan en CSV anteriores
        for col in cols:
            if col not in df.columns:
                df[col] = None
        # Forzar dtype object en columnas de texto que pudieran haberse inferido como float64
        if str_cols:
            for col in str_cols:
                if col in df.columns and df[col].dtype != object:
                    df[col] = df[col].astype(object)
        return df
    return pd.DataFrame(columns=cols)


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


# ── Usuarios ──────────────────────────────────────────────────────────────────

def get_user(username: str) -> dict | None:
    """Retorna el usuario como dict, o None si no existe."""
    df = _read_csv(USUARIOS_CSV, _USUARIOS_COLS)
    row = df[df["username"] == username]
    return row.iloc[0].to_dict() if not row.empty else None


def create_user(username: str, password_hash: str) -> bool:
    """Crea un nuevo usuario. Retorna False si el username ya existe."""
    df = _read_csv(USUARIOS_CSV, _USUARIOS_COLS)
    if not df[df["username"] == username].empty:
        return False
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "username": username,
        "password_hash": password_hash,
        "fecha_registro": pd.Timestamp.today().strftime("%Y-%m-%d"),
    }])
    _write_csv(pd.concat([df, new_row], ignore_index=True), USUARIOS_CSV)
    return True


# ── Ciudades ──────────────────────────────────────────────────────────────────

def get_cities(username: str) -> pd.DataFrame:
    """Retorna las ciudades favoritas del usuario dado."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    if df.empty:
        return df
    return df[df["username"] == username].copy()


def add_city(username: str, ciudad: str, pais: str, latitud: float, longitud: float) -> bool:
    """Agrega una ciudad para el usuario. Retorna False si ya existe para ese usuario."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    user_df = df[df["username"] == username] if not df.empty else df
    if not user_df[user_df["ciudad"].str.lower() == ciudad.lower()].empty:
        return False
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "username": username,
        "ciudad": ciudad,
        "pais": pais,
        "latitud": latitud,
        "longitud": longitud,
        "alerta_max_temp": None,
        "alerta_min_temp": None,
        "alerta_max_temp_f": None,
        "alerta_min_temp_f": None,
    }])
    _write_csv(pd.concat([df, new_row], ignore_index=True), CIUDADES_CSV)
    return True


def delete_city(username: str, city_id: int) -> None:
    """Elimina la ciudad del usuario dado por su id."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    # Solo elimina si la ciudad pertenece al usuario
    _write_csv(df[~((df["id"] == city_id) & (df["username"] == username))], CIUDADES_CSV)


def update_city_weather(username: str, ciudad: str, data: dict) -> None:
    """Guarda el último clima consultado en la fila de la ciudad favorita del usuario en ciudades.csv."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS, str_cols=_CIUDADES_STR_COLS)
    mask = (df["username"] == username) & (df["ciudad"].str.lower() == ciudad.lower())
    if mask.sum() == 0:
        return  # no es favorita de este usuario, nada que actualizar
    idx = df[mask].index[0]
    for key in ("temperatura", "temp_max", "temp_min", "sensacion_termica",
                "humedad", "viento", "codigo_clima", "descripcion", "icono"):
        df.at[idx, key] = data.get(key)
    df.at[idx, "ultima_consulta"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    _write_csv(df, CIUDADES_CSV)


def update_alert(city_id: int, max_temp: float | None, min_temp: float | None) -> None:
    """Actualiza los umbrales de alerta en °C y °F para una ciudad."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    max_f = round(max_temp * 9 / 5 + 32, 1) if max_temp is not None else None
    min_f = round(min_temp * 9 / 5 + 32, 1) if min_temp is not None else None
    df.loc[df["id"] == city_id, "alerta_max_temp"]   = max_temp
    df.loc[df["id"] == city_id, "alerta_min_temp"]   = min_temp
    df.loc[df["id"] == city_id, "alerta_max_temp_f"] = max_f
    df.loc[df["id"] == city_id, "alerta_min_temp_f"] = min_f
    _write_csv(df, CIUDADES_CSV)


# ── Historial ─────────────────────────────────────────────────────────────────

def get_history(ciudad: str, fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
    """
    Retorna registros del historial para una ciudad en el rango dado.
    Las fechas deben tener formato YYYY-MM-DD.
    """
    df = _read_csv(HISTORIAL_CSV, _HISTORIAL_COLS)
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"])
    mask = (
        (df["ciudad"].str.lower() == ciudad.lower())
        & (df["fecha"] >= pd.to_datetime(fecha_inicio))
        & (df["fecha"] <= pd.to_datetime(fecha_fin))
    )
    return df[mask].copy()


def save_history(new_df: pd.DataFrame) -> None:
    """
    Agrega registros al historial evitando duplicados por (ciudad, fecha).
    Elimina automáticamente registros con más de 365 días de antigüedad.
    """
    existing = _read_csv(HISTORIAL_CSV, _HISTORIAL_COLS)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["ciudad", "fecha"], keep="last")
    combined = combined.sort_values(["ciudad", "fecha"]).reset_index(drop=True)
    # Purgar registros muy antiguos (> 365 días) para mantener el archivo liviano
    combined["fecha"] = pd.to_datetime(combined["fecha"])
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=365)
    combined = combined[combined["fecha"] >= cutoff]
    combined["fecha"] = combined["fecha"].dt.strftime("%Y-%m-%d")
    combined["id"] = combined.index + 1
    _write_csv(combined, HISTORIAL_CSV)


# ── Cache de último clima consultado por ciudad ───────────────────────────────

def save_weather_cache(data: dict, username: str | None = None) -> None:
    """Guarda o actualiza el último clima completo consultado para una ciudad.

    - Si la ciudad es favorita del usuario, actualiza también ciudades.csv.
    - Siempre actualiza cache_clima.csv (cubre ciudades no favoritas también).
    """
    # 1. Persistir en ciudades.csv si es favorita del usuario
    if username is not None:
        update_city_weather(username, data["ciudad"], data)

    # 2. Actualizar cache general
    df = _read_csv(CACHE_CSV, _CACHE_COLS)
    # Reemplazar registro existente de la misma ciudad
    df = df[df["ciudad"].str.lower() != data["ciudad"].lower()]
    new_row = pd.DataFrame([{
        "ciudad":            data.get("ciudad", ""),
        "pais":              data.get("pais", ""),
        "latitud":           data.get("latitud"),
        "longitud":          data.get("longitud"),
        "temperatura":       data.get("temperatura"),
        "temp_max":          data.get("temp_max"),
        "temp_min":          data.get("temp_min"),
        "sensacion_termica": data.get("sensacion_termica"),
        "humedad":           data.get("humedad"),
        "viento":            data.get("viento"),
        "codigo_clima":      data.get("codigo_clima"),
        "descripcion":       data.get("descripcion", ""),
        "icono":             data.get("icono", "unknown"),
        "ultima_consulta":   pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    _write_csv(pd.concat([df, new_row], ignore_index=True), CACHE_CSV)


def get_weather_cache(ciudad: str, username: str | None = None) -> dict | None:
    """Retorna el último clima guardado para la ciudad.

    Busca primero en ciudades.csv (favorita del usuario con clima guardado),
    luego en cache_clima.csv (ciudades no favoritas consultadas).
    """
    _NUM_KEYS = ("temperatura", "temp_max", "temp_min", "sensacion_termica", "humedad", "viento")

    def _normalizar(row: dict) -> dict:
        for key in _NUM_KEYS:
            val = row.get(key)
            row[key] = float(val) if pd.notna(val) else None
        return row

    # 1. Buscar en ciudades favoritas del usuario
    if username is not None:
        fav_df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS, str_cols=_CIUDADES_STR_COLS)
        fav_match = fav_df[
            (fav_df["username"] == username)
            & (fav_df["ciudad"].str.lower() == ciudad.lower())
        ]
        if not fav_match.empty:
            row = fav_match.iloc[0].to_dict()
            if pd.notna(row.get("ultima_consulta")):
                return _normalizar(row)

    # 2. Fallback: cache general
    df = _read_csv(CACHE_CSV, _CACHE_COLS)
    if df.empty:
        return None
    match = df[df["ciudad"].str.lower() == ciudad.lower()]
    if match.empty:
        return None
    return _normalizar(match.iloc[0].to_dict())
