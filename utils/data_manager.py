# Valentina Rodriguez Sepulveda — 1121789977
# utils/data_manager.py — Lectura y escritura de archivos CSV con pandas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from pathlib import Path

import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USUARIOS_CSV = DATA_DIR / "usuarios.csv"
CIUDADES_CSV = DATA_DIR / "ciudades.csv"
HISTORIAL_CSV = DATA_DIR / "historial_clima.csv"

_USUARIOS_COLS = ["id", "username", "password_hash", "fecha_registro"]
_CIUDADES_COLS = ["id", "ciudad", "pais", "latitud", "longitud",
                  "alerta_max_temp", "alerta_min_temp",
                  "alerta_max_temp_f", "alerta_min_temp_f"]
_HISTORIAL_COLS = ["id", "ciudad", "fecha", "temp_max", "temp_min", "precipitacion", "viento_max"]

# ── Helpers privados ──────────────────────────────────────────────────────────

def _read_csv(path: Path, cols: list) -> pd.DataFrame:
    """Lee un CSV; si no existe o está vacío retorna un DataFrame con las columnas indicadas."""
    if path.exists() and path.stat().st_size > 0:
        df = pd.read_csv(path)
        # Migración automática: añadir columnas nuevas que no existan en CSV anteriores
        for col in cols:
            if col not in df.columns:
                df[col] = None
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

def get_cities() -> pd.DataFrame:
    """Retorna todas las ciudades favoritas."""
    return _read_csv(CIUDADES_CSV, _CIUDADES_COLS)


def add_city(ciudad: str, pais: str, latitud: float, longitud: float) -> bool:
    """Agrega una ciudad. Retorna False si ya existe (por nombre, insensible a mayúsculas)."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    if not df[df["ciudad"].str.lower() == ciudad.lower()].empty:
        return False
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{
        "id": new_id,
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


def delete_city(city_id: int) -> None:
    """Elimina una ciudad por su id."""
    df = _read_csv(CIUDADES_CSV, _CIUDADES_COLS)
    _write_csv(df[df["id"] != city_id], CIUDADES_CSV)


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
    El DataFrame entrante debe tener las columnas de _HISTORIAL_COLS (excepto id).
    """
    existing = _read_csv(HISTORIAL_CSV, _HISTORIAL_COLS)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["ciudad", "fecha"], keep="last")
    combined = combined.sort_values(["ciudad", "fecha"]).reset_index(drop=True)
    combined["id"] = combined.index + 1
    _write_csv(combined, HISTORIAL_CSV)
