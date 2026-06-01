# Valentina Rodriguez Sepulveda — 1125789977
# views/home_view.py — Ventana principal: clima actual
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import base64
import io
from datetime import datetime
from typing import Callable

import flet as ft
import pandas as pd
from PIL import Image, ImageDraw

import utils.settings as settings
from utils.api_client import obtener_clima_actual, obtener_clima_actual_desde_geo, buscar_ciudades
from utils.data_manager import agregar_ciudad, obtener_ciudades, obtener_cache_clima, guardar_cache_clima

# ── Generación de íconos con Pillow ──────────────────────────────────────────

_PALETA_ICONOS: dict[str, tuple[str, str]] = {
    "sunny":         ("#FDD835", "#F57F17"),
    "partly_cloudy": ("#90CAF9", "#42A5F5"),
    "cloudy":        ("#90A4AE", "#546E7A"),
    "fog":           ("#CFD8DC", "#B0BEC5"),
    "drizzle":       ("#81D4FA", "#0288D1"),
    "rain":          ("#42A5F5", "#1565C0"),
    "snow":          ("#E3F2FD", "#90CAF9"),
    "thunderstorm":  ("#546E7A", "#FDD835"),
    "unknown":       ("#B0BEC5", "#78909C"),
}

_cache_iconos: dict[str, str] = {}


def _hex_a_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


def _crear_icono(condition: str) -> str:
    """Genera un ícono del clima con Pillow y retorna el PNG codificado en base64."""
    if condition in _cache_iconos:
        return _cache_iconos[condition]

    bg_hex, ac_hex = _PALETA_ICONOS.get(condition, _PALETA_ICONOS["unknown"])
    bg = _hex_a_rgb(bg_hex)
    ac = _hex_a_rgb(ac_hex)

    size = 80
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    m, cx, cy = 3, size // 2, size // 2

    # Círculo base
    draw.ellipse([m, m, size - m, size - m], fill=bg)

    # Decoración específica por condición
    if condition == "sunny":
        r = size // 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ac)

    elif condition in ("rain", "drizzle"):
        step = 10
        for offset in range(-size, size, step):
            x1 = cx + offset
            draw.line([(x1, m + 6), (x1 - 16, size - m - 6)], fill=ac, width=2)

    elif condition == "snow":
        rd = 5
        for dx, dy in [(-18, 0), (18, 0), (0, -18), (0, 18),
                       (-12, -12), (12, 12), (-12, 12), (12, -12)]:
            draw.ellipse([cx + dx - rd, cy + dy - rd,
                          cx + dx + rd, cy + dy + rd], fill=(255, 255, 255, 220))

    elif condition == "thunderstorm":
        pts = [(cx - 4, cy - 18), (cx + 9, cy - 2), (cx + 2, cy - 2),
               (cx + 4, cy + 18), (cx - 9, cy + 2), (cx - 2, cy + 2)]
        draw.polygon(pts, fill=ac)

    elif condition == "fog":
        for dy in (-10, 0, 10):
            draw.rectangle([cx - 20, cy + dy - 3, cx + 20, cy + dy + 3], fill=ac)

    elif condition == "cloudy":
        draw.ellipse([cx - 20, cy - 10, cx + 20, cy + 14], fill=ac)
        draw.ellipse([cx - 8,  cy - 18, cx + 18, cy + 4],  fill=ac)

    else:
        r = size // 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ac)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = base64.b64encode(buf.getvalue()).decode()
    _cache_iconos[condition] = result
    return result


# ── Vista ─────────────────────────────────────────────────────────────────────


class HomeView:
    """
    Pantalla principal. Muestra el clima actual de una ciudad buscada o favorita.
    Permite guardar ciudades favoritas y activa avisos de alerta de temperatura.
    """

    def __init__(
        self,
        page: ft.Page,
        username: str,
        on_go_history: Callable,
        on_go_cities: Callable,
        on_go_alerts: Callable,
        on_logout: Callable,
    ) -> None:
        self.page = page
        self.username = username
        self.on_go_history = on_go_history
        self.on_go_cities = on_go_cities
        self.on_go_alerts = on_go_alerts
        self.on_logout = on_logout
        self._datos_clima: dict | None = None
        self._dialogo_seleccion: ft.AlertDialog | None = None

        # ── Controles: búsqueda ───────────────────────────────────────────────

        self._entrada_ciudad = ft.TextField(
            label="Buscar ciudad",
            hint_text="Ej: Bogotá, Madrid, Buenos Aires…",
            prefix_icon=ft.Icons.SEARCH,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            border_radius=8,
            on_submit=self._al_buscar_ciudad,
            expand=True,
        )

        self._lista_favoritas = ft.Dropdown(
            label="Ciudades favoritas",
            options=[],
            on_change=self._al_seleccionar_de_lista,
            border_radius=8,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            expand=True,
        )

        self._boton_buscar = ft.ElevatedButton(
            text="Buscar",
            icon=ft.Icons.SEARCH,
            on_click=self._al_buscar_ciudad,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._mensaje_estado = ft.Text("", size=13, color="#90CAF9")

        # ── Controles: tarjeta del clima ──────────────────────────────────────

        self._icono_clima = ft.Image(
            src_base64=_crear_icono("unknown"),
            width=72,
            height=72,
        )
        self._etiqueta_ciudad = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self._etiqueta_descripcion = ft.Text("", size=14, color="#E3F2FD")
        self._etiqueta_temperatura = ft.Text("", size=52, weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self._etiqueta_temp_max  = ft.Text("", size=14, color="#FFCC80")
        self._etiqueta_temp_min  = ft.Text("", size=14, color="#80D8FF")
        self._etiqueta_sensacion = ft.Text("", size=13, color="#CFD8DC")
        self._etiqueta_viento = ft.Text("", size=13, color="#CFD8DC")
        self._etiqueta_humedad  = ft.Text("", size=13, color="#CFD8DC")

        # ── Controles: banner de alerta ───────────────────────────────────────

        self._texto_alerta = ft.Text("", color="#FFFFFF", size=14)
        self._banner_alerta = ft.Container(
            visible=False,
            bgcolor="#BF360C",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#FFFFFF", size=22),
                    self._texto_alerta,
                ],
            ),
        )

        # ── Controles: banner sin conexión ──────────────────────────────────────

        self._texto_sin_conexion = ft.Text("", color="#FFFFFF", size=13)
        self._banner_sin_conexion = ft.Container(
            visible=False,
            bgcolor="#E65100",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.WIFI_OFF, color="#FFFFFF", size=22),
                    self._texto_sin_conexion,
                ],
            ),
        )

        # Tarjeta del clima (armada en build())
        self._tarjeta_clima: ft.Container | None = None

        # ── Controles: unidades de medida ─────────────────────────────────────
        _btn_style = ft.ButtonStyle(
            color="#FFFFFF",
            side=ft.BorderSide(color="#90CAF9", width=1),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )
        self._boton_unidad_temp = ft.OutlinedButton(
            text=settings.simbolo_temperatura(),
            on_click=self._cambiar_unidad_temperatura,
            style=_btn_style,
            height=32,
        )
        self._boton_unidad_vel = ft.OutlinedButton(
            text=settings.simbolo_velocidad(),
            on_click=self._cambiar_unidad_velocidad,
            style=_btn_style,
            height=32,
        )

        # Botones duplicados para la cabecera (sin quitar los de la tarjeta)
        self._boton_cabecera_unidad_temp = ft.OutlinedButton(
            text=settings.simbolo_temperatura(),
            on_click=self._cambiar_unidad_temperatura,
            style=_btn_style,
            height=28,
        )
        self._boton_cabecera_unidad_vel = ft.OutlinedButton(
            text=settings.simbolo_velocidad(),
            on_click=self._cambiar_unidad_velocidad,
            style=_btn_style,
            height=28,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _actualizar_lista_ciudades(self, update: bool = False) -> None:
        df = obtener_ciudades(self.username)
        self._lista_favoritas.options = [
            ft.dropdown.Option(str(row["ciudad"])) for _, row in df.iterrows()
        ]
        if update:
            self.page.update()

    def _al_seleccionar_de_lista(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self._entrada_ciudad.value = e.control.value
            self.page.update()

    def _al_buscar_ciudad(self, e: ft.ControlEvent) -> None:
        city = (self._entrada_ciudad.value or "").strip()
        if not city:
            self._mensaje_estado.value = "Escribe el nombre de una ciudad."
            self._mensaje_estado.color = "#EF9A9A"
            self.page.update()
            return

        self._mensaje_estado.value = "Buscando…"
        self._mensaje_estado.color = "#90CAF9"
        self.page.update()

        options = buscar_ciudades(city, cantidad=5)
        if not options:
            # Sin resultado: puede ser falta de internet → intentar cache
            cached = obtener_cache_clima(city, self.username)
            if cached is not None:
                self._mostrar_clima_sin_conexion(cached)
                return
            self._mensaje_estado.value = "Ciudad no encontrada o sin conexión a internet."
            self._mensaje_estado.color = "#EF9A9A"
            self._datos_clima = None
            self._tarjeta_clima.visible = False
            self._banner_alerta.visible = False
            self._banner_sin_conexion.visible = False
            self.page.update()
            return

        if len(options) == 1:
            self._al_elegir_ciudad(options[0])
        else:
            self._mostrar_opciones_ciudad(options)

    def _mostrar_clima_sin_conexion(self, cached: dict) -> None:
        """Muestra el último clima cacheado con un aviso de sin conexión."""
        self._datos_clima = cached
        self._mostrar_clima_en_tarjeta(cached)
        self._verificar_alerta_clima(cached)

        fecha = cached.get("ultima_consulta", "")
        try:
            dt = datetime.fromisoformat(str(fecha))
            fecha_str = dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            fecha_str = str(fecha)

        self._texto_sin_conexion.value = (
            f"Sin internet · Último dato: {fecha_str}"
        )
        self._banner_sin_conexion.visible = True

        fav_df = obtener_ciudades(self.username)
        is_fav = not fav_df[fav_df["ciudad"].str.lower() == cached["ciudad"].lower()].empty
        self._mensaje_estado.value = ""
        self.page.update()

    # ── Mostrar clima en tarjeta ──────────────────────────────────
    # El diccionario `data` fue creado por api_client._consultar_clima_desde_geo()
    # a partir de la respuesta JSON de Open-Meteo. Sus claves ya están en español:
    #
    #   data["temperatura"]       ← Open-Meteo envía "temperature_2m"
    #   data["sensacion_termica"] ← Open-Meteo envía "apparent_temperature"
    #   data["humedad"]           ← Open-Meteo envía "relative_humidity_2m"
    #   data["viento"]            ← Open-Meteo envía "wind_speed_10m"
    #   data["temp_max"]          ← Open-Meteo envía daily["temperature_2m_max"]
    #   data["temp_min"]          ← Open-Meteo envía daily["temperature_2m_min"]
    #   data["icono"]             ← traducido desde el código WMO (weathercode)
    #   data["descripcion"]       ← traducido desde el código WMO

    def _mostrar_clima_en_tarjeta(self, data: dict) -> None:
        self._icono_clima.src_base64 = _crear_icono(data.get("icono", "unknown"))
        self._etiqueta_ciudad.value = f"{data['ciudad']}, {data['pais']}"
        self._etiqueta_descripcion.value = data.get("descripcion", "")

        sym = settings.simbolo_temperatura()
        spd = settings.simbolo_velocidad()

        t  = settings.convertir_temperatura(data.get("temperatura"))
        mx = settings.convertir_temperatura(data.get("temp_max"))
        mn = settings.convertir_temperatura(data.get("temp_min"))
        st = settings.convertir_temperatura(data.get("sensacion_termica"))
        wi = settings.convertir_velocidad(data.get("viento"))
        hu = data.get("humedad")

        self._etiqueta_temperatura.value = f"{t:.0f}{sym}" if t is not None else "—"
        self._etiqueta_temp_max.value  = f"↑ {mx:.0f}{sym}" if mx is not None else ""
        self._etiqueta_temp_min.value  = f"↓ {mn:.0f}{sym}" if mn is not None else ""
        self._etiqueta_sensacion.value = f"Sensación  {st:.0f}{sym}" if st is not None else ""
        self._etiqueta_viento.value = f"💨 {wi:.1f} {spd}" if wi is not None else ""
        self._etiqueta_humedad.value  = f"💧 {hu}%"  if hu is not None else ""

        self._tarjeta_clima.visible = True

    def _verificar_alerta_clima(self, data: dict) -> None:
        fav_df = obtener_ciudades(self.username)
        match = fav_df[fav_df["ciudad"].str.lower() == data["ciudad"].lower()]
        if match.empty:
            self._banner_alerta.visible = False
            return

        temp = data.get("temperatura")
        if temp is None:
            self._banner_alerta.visible = False
            return

        row = match.iloc[0]
        max_t = row["alerta_max_temp"]
        min_t = row["alerta_min_temp"]

        sym  = settings.simbolo_temperatura()
        unit = settings.obtener_unidad_temperatura()

        msg = ""
        if pd.notna(max_t) and temp > float(max_t):
            disp_temp = settings.convertir_temperatura(temp)
            if unit == "F":
                disp_max = (float(row["alerta_max_temp_f"])
                            if pd.notna(row.get("alerta_max_temp_f"))
                            else round(float(max_t) * 9 / 5 + 32, 1))
            else:
                disp_max = float(max_t)
            msg = f"Temperatura actual ({disp_temp:.0f}{sym}) supera el umbral máximo ({disp_max:.0f}{sym})"
        elif pd.notna(min_t) and temp < float(min_t):
            disp_temp = settings.convertir_temperatura(temp)
            if unit == "F":
                disp_min = (float(row["alerta_min_temp_f"])
                            if pd.notna(row.get("alerta_min_temp_f"))
                            else round(float(min_t) * 9 / 5 + 32, 1))
            else:
                disp_min = float(min_t)
            msg = f"Temperatura actual ({disp_temp:.0f}{sym}) está bajo el umbral mínimo ({disp_min:.0f}{sym})"

        self._texto_alerta.value = msg
        self._banner_alerta.visible = bool(msg)

    # ── Unidades de medida ─────────────────────────────────────────────────────

    def _cambiar_unidad_temperatura(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_temperatura("F" if settings.obtener_unidad_temperatura() == "C" else "C")
        self._boton_unidad_temp.text = settings.simbolo_temperatura()
        # Also update header button if exists
        if hasattr(self, "_boton_cabecera_unidad_temp"):
            self._boton_cabecera_unidad_temp.text = settings.simbolo_temperatura()
        if self._datos_clima:
            self._mostrar_clima_en_tarjeta(self._datos_clima)
        self.page.update()

    def _cambiar_unidad_velocidad(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_velocidad("mph" if settings.obtener_unidad_velocidad() == "kmh" else "kmh")
        self._boton_unidad_vel.text = settings.simbolo_velocidad()
        # Also update header button if exists
        if hasattr(self, "_boton_cabecera_unidad_vel"):
            self._boton_cabecera_unidad_vel.text = settings.simbolo_velocidad()
        if self._datos_clima:
            self._mostrar_clima_en_tarjeta(self._datos_clima)
        self.page.update()

    # ── Búsqueda con opciones múltiples ────────────────────────────────────────

    def _mostrar_opciones_ciudad(self, options: list[dict]) -> None:
        """Muestra un diálogo para que el usuario elija entre varias ciudades."""
        tiles = [
            ft.ListTile(
                title=ft.Text(
                    f"{opt['name']}, {opt['country']}",
                    color="#FFFFFF",
                    weight=ft.FontWeight.W_500,
                ),
                subtitle=ft.Text(
                    f"Lat {opt['latitude']:.2f}   Lon {opt['longitude']:.2f}",
                    color="#90CAF9",
                    size=12,
                ),
                on_click=lambda e, o=opt: self._al_elegir_ciudad(o),
            )
            for opt in options
        ]
        self._dialogo_seleccion = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Qué ciudad buscas?", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            bgcolor="#0D47A1",
            content=ft.Column(tight=True, controls=tiles, spacing=0, width=380),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._cerrar_dialogo(),
                    style=ft.ButtonStyle(color="#90CAF9"),
                ),
            ],
        )
        self._mensaje_estado.value = ""
        self.page.open(self._dialogo_seleccion)

    def _al_elegir_ciudad(self, geo: dict) -> None:
        self._cerrar_dialogo()
        self._mensaje_estado.value = "Consultando…"
        self._mensaje_estado.color = "#90CAF9"
        self.page.update()

        data = obtener_clima_actual_desde_geo(geo)
        if data is None:
            # Sin conexión: intentar cache por nombre de ciudad
            cached = obtener_cache_clima(geo.get("name", ""), self.username)
            if cached is not None:
                self._mostrar_clima_sin_conexion(cached)
                return
            self._mensaje_estado.value = "Sin conexión a internet."
            self._mensaje_estado.color = "#EF9A9A"
            self.page.update()
            return

        # Éxito: guardar en cache y ocultar banner offline
        guardar_cache_clima(data, self.username)
        self._banner_sin_conexion.visible = False
        self._datos_clima = data
        self._mensaje_estado.value = ""
        self._mostrar_clima_en_tarjeta(data)
        self._verificar_alerta_clima(data)

        fav_df = obtener_ciudades(self.username)
        is_fav = not fav_df[fav_df["ciudad"].str.lower() == data["ciudad"].lower()].empty
        self.page.update()
        
        if not is_fav:
            def on_yes(e):
                agregar_ciudad(
                    self.username,
                    data["ciudad"],
                    data["pais"],
                    data["latitud"],
                    data["longitud"],
                )
                self._actualizar_lista_ciudades(update=True)
                self.page.close(self._dialogo_favorito)
                self.page.update()
                
            def on_no(e):
                self.page.close(self._dialogo_favorito)
                self.page.update()
            
            self._dialogo_favorito = ft.AlertDialog(
                modal=True,
                title=ft.Text("Agregar a favoritas", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                bgcolor="#0D47A1",
                content=ft.Text(f"¿Desea agregar la ciudad {data['ciudad']} como favorita?", color="#E3F2FD"),
                actions=[
                    ft.TextButton("Sí", on_click=on_yes, style=ft.ButtonStyle(color="#A5D6A7")),
                    ft.TextButton("No", on_click=on_no, style=ft.ButtonStyle(color="#EF9A9A")),
                ],
            )
            self.page.open(self._dialogo_favorito)

    def _cerrar_dialogo(self) -> None:
        if self._dialogo_seleccion is not None:
            self.page.close(self._dialogo_seleccion)

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._actualizar_lista_ciudades()

        self._tarjeta_clima = ft.Container(
            visible=False,
            bgcolor="#0D47A1",
            border_radius=16,
            padding=ft.padding.all(28),
            shadow=ft.BoxShadow(blur_radius=24, color="black26", offset=ft.Offset(0, 8)),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            self._icono_clima,
                            ft.Column(
                                spacing=4,
                                controls=[self._etiqueta_ciudad, self._etiqueta_descripcion],
                            ),
                        ],
                    ),
                    self._etiqueta_temperatura,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=24,
                        controls=[self._etiqueta_temp_max, self._etiqueta_temp_min],
                    ),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=28,
                        controls=[self._etiqueta_sensacion, self._etiqueta_viento, self._etiqueta_humedad],
                    ),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Text("Unidades:", size=12, color="#90CAF9"),
                            self._boton_unidad_temp,
                            self._boton_unidad_vel,
                        ],
                    ),
                ],
            ),
        )

        header = ft.Container(
            bgcolor="#0D47A1",
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.CLOUD, color="#29B6F6", size=28),
                        ft.Text("MeteoApp", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ]),
                    ft.Row(spacing=4, controls=[
                        ft.TextButton(
                            "Historial",
                            icon=ft.Icons.BAR_CHART,
                            on_click=lambda _: self.on_go_history(),
                            style=ft.ButtonStyle(color="#FFFFFF"),
                        ),
                        ft.TextButton(
                            "Ciudades",
                            icon=ft.Icons.LOCATION_CITY,
                            on_click=lambda _: self.on_go_cities(),
                            style=ft.ButtonStyle(color="#FFFFFF"),
                        ),
                        ft.TextButton(
                            "Alertas",
                            icon=ft.Icons.NOTIFICATIONS,
                            on_click=lambda _: self.on_go_alerts(),
                            style=ft.ButtonStyle(color="#FFFFFF"),
                        ),
                        # Botones de unidades en header (duplicados)
                        self._boton_cabecera_unidad_temp,
                        self._boton_cabecera_unidad_vel,
                        ft.VerticalDivider(width=1, color="#42A5F5"),
                        ft.Text(f"👤 {self.username}", color="#90CAF9", size=13),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color="#EF9A9A",
                            tooltip="Cerrar sesión",
                            on_click=lambda _: self.on_logout(),
                        ),
                    ]),
                ],
            ),
        )

        search_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(20),
            shadow=ft.BoxShadow(blur_radius=12, color="black12", offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text(
                        "Consultar clima actual",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#FFFFFF",
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[self._entrada_ciudad, self._boton_buscar],
                    ),
                    self._lista_favoritas,
                    self._mensaje_estado,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor="#1976D2",
            content=ft.Column(
                spacing=0,
                controls=[
                    header,
                    ft.Container(
                        expand=True,
                        padding=ft.padding.all(20),
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                            controls=[
                                search_panel,
                                self._banner_sin_conexion,
                                self._tarjeta_clima,
                                self._banner_alerta,
                            ],
                        ),
                    ),
                ],
            ),
        )
