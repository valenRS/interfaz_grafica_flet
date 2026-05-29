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
from utils.api_client import get_current_weather, get_current_weather_from_geo, search_cities
from utils.data_manager import add_city, get_cities, get_weather_cache, save_weather_cache

# ── Generación de íconos con Pillow ──────────────────────────────────────────

_ICON_PALETTE: dict[str, tuple[str, str]] = {
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

_icon_cache: dict[str, str] = {}


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


def _make_icon(condition: str) -> str:
    """Genera un ícono del clima con Pillow y retorna el PNG codificado en base64."""
    if condition in _icon_cache:
        return _icon_cache[condition]

    bg_hex, ac_hex = _ICON_PALETTE.get(condition, _ICON_PALETTE["unknown"])
    bg = _hex_to_rgb(bg_hex)
    ac = _hex_to_rgb(ac_hex)

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
    _icon_cache[condition] = result
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
        self._weather_data: dict | None = None
        self._dlg: ft.AlertDialog | None = None

        # ── Controles: búsqueda ───────────────────────────────────────────────

        self._city_input = ft.TextField(
            label="Buscar ciudad",
            hint_text="Ej: Bogotá, Madrid, Buenos Aires…",
            prefix_icon=ft.Icons.SEARCH,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            border_radius=8,
            on_submit=self._on_search,
            expand=True,
        )

        self._dropdown = ft.Dropdown(
            label="Ciudades favoritas",
            options=[],
            on_change=self._on_dropdown_select,
            border_radius=8,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            expand=True,
        )

        self._save_checkbox = ft.Checkbox(
            label="Guardar como favorita",
            value=False,
            disabled=True,
            on_change=self._on_save_toggle,
            label_style=ft.TextStyle(color="#FFFFFF"),
        )

        self._search_btn = ft.ElevatedButton(
            text="Buscar",
            icon=ft.Icons.SEARCH,
            on_click=self._on_search,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._msg = ft.Text("", size=13, color="#90CAF9")

        # ── Controles: tarjeta del clima ──────────────────────────────────────

        self._weather_icon = ft.Image(
            src_base64=_make_icon("unknown"),
            width=72,
            height=72,
        )
        self._city_lbl = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self._desc_lbl = ft.Text("", size=14, color="#E3F2FD")
        self._temp_lbl = ft.Text("", size=52, weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self._max_lbl  = ft.Text("", size=14, color="#FFCC80")
        self._min_lbl  = ft.Text("", size=14, color="#80D8FF")
        self._sens_lbl = ft.Text("", size=13, color="#CFD8DC")
        self._wind_lbl = ft.Text("", size=13, color="#CFD8DC")
        self._hum_lbl  = ft.Text("", size=13, color="#CFD8DC")

        # ── Controles: banner de alerta ───────────────────────────────────────

        self._alert_text = ft.Text("", color="#FFFFFF", size=14)
        self._alert_banner = ft.Container(
            visible=False,
            bgcolor="#BF360C",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#FFFFFF", size=22),
                    self._alert_text,
                ],
            ),
        )

        # ── Controles: banner sin conexión ──────────────────────────────────────

        self._offline_text = ft.Text("", color="#FFFFFF", size=13)
        self._offline_banner = ft.Container(
            visible=False,
            bgcolor="#E65100",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.WIFI_OFF, color="#FFFFFF", size=22),
                    self._offline_text,
                ],
            ),
        )

        # Tarjeta del clima (armada en build())
        self._weather_card: ft.Container | None = None

        # ── Controles: unidades de medida ─────────────────────────────────────
        _btn_style = ft.ButtonStyle(
            color="#FFFFFF",
            side=ft.BorderSide(color="#90CAF9", width=1),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )
        self._btn_temp_unit = ft.OutlinedButton(
            text=settings.temp_symbol(),
            on_click=self._toggle_temp,
            style=_btn_style,
            height=32,
        )
        self._btn_speed_unit = ft.OutlinedButton(
            text=settings.speed_symbol(),
            on_click=self._toggle_speed,
            style=_btn_style,
            height=32,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_dropdown(self, update: bool = False) -> None:
        df = get_cities(self.username)
        self._dropdown.options = [
            ft.dropdown.Option(str(row["ciudad"])) for _, row in df.iterrows()
        ]
        if update:
            self.page.update()

    def _on_dropdown_select(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self._city_input.value = e.control.value
            self.page.update()

    def _on_search(self, e: ft.ControlEvent) -> None:
        city = (self._city_input.value or "").strip()
        if not city:
            self._msg.value = "Escribe el nombre de una ciudad."
            self._msg.color = "#EF9A9A"
            self.page.update()
            return

        self._msg.value = "Buscando…"
        self._msg.color = "#90CAF9"
        self.page.update()

        options = search_cities(city, count=5)
        if not options:
            # Sin resultado: puede ser falta de internet → intentar cache
            cached = get_weather_cache(city, self.username)
            if cached is not None:
                self._show_offline_weather(cached)
                return
            self._msg.value = "Ciudad no encontrada o sin conexión a internet."
            self._msg.color = "#EF9A9A"
            self._weather_data = None
            self._weather_card.visible = False
            self._alert_banner.visible = False
            self._offline_banner.visible = False
            self._save_checkbox.disabled = True
            self.page.update()
            return

        if len(options) == 1:
            self._on_city_selected(options[0])
        else:
            self._show_city_options(options)

    def _show_offline_weather(self, cached: dict) -> None:
        """Muestra el último clima cacheado con un aviso de sin conexión."""
        self._weather_data = cached
        self._display_weather(cached)
        self._check_alert(cached)

        fecha = cached.get("ultima_consulta", "")
        try:
            dt = datetime.fromisoformat(str(fecha))
            fecha_str = dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            fecha_str = str(fecha)

        self._offline_text.value = (
            f"Sin internet · Último dato: {fecha_str}"
        )
        self._offline_banner.visible = True

        fav_df = get_cities(self.username)
        is_fav = not fav_df[fav_df["ciudad"].str.lower() == cached["ciudad"].lower()].empty
        self._save_checkbox.value = is_fav
        self._save_checkbox.disabled = True  # no se puede modificar sin conexión
        self._msg.value = ""
        self.page.update()

    def _display_weather(self, data: dict) -> None:
        self._weather_icon.src_base64 = _make_icon(data.get("icono", "unknown"))
        self._city_lbl.value = f"{data['ciudad']}, {data['pais']}"
        self._desc_lbl.value = data.get("descripcion", "")

        sym = settings.temp_symbol()
        spd = settings.speed_symbol()

        t  = settings.convert_temp(data.get("temperatura"))
        mx = settings.convert_temp(data.get("temp_max"))
        mn = settings.convert_temp(data.get("temp_min"))
        st = settings.convert_temp(data.get("sensacion_termica"))
        wi = settings.convert_speed(data.get("viento"))
        hu = data.get("humedad")

        self._temp_lbl.value = f"{t:.0f}{sym}" if t is not None else "—"
        self._max_lbl.value  = f"↑ {mx:.0f}{sym}" if mx is not None else ""
        self._min_lbl.value  = f"↓ {mn:.0f}{sym}" if mn is not None else ""
        self._sens_lbl.value = f"Sensación  {st:.0f}{sym}" if st is not None else ""
        self._wind_lbl.value = f"💨 {wi:.1f} {spd}" if wi is not None else ""
        self._hum_lbl.value  = f"💧 {hu}%"  if hu is not None else ""

        self._weather_card.visible = True

    def _check_alert(self, data: dict) -> None:
        fav_df = get_cities(self.username)
        match = fav_df[fav_df["ciudad"].str.lower() == data["ciudad"].lower()]
        if match.empty:
            self._alert_banner.visible = False
            return

        temp = data.get("temperatura")
        if temp is None:
            self._alert_banner.visible = False
            return

        row = match.iloc[0]
        max_t = row["alerta_max_temp"]
        min_t = row["alerta_min_temp"]

        sym  = settings.temp_symbol()
        unit = settings.get_temp_unit()

        msg = ""
        if pd.notna(max_t) and temp > float(max_t):
            disp_temp = settings.convert_temp(temp)
            if unit == "F":
                disp_max = (float(row["alerta_max_temp_f"])
                            if pd.notna(row.get("alerta_max_temp_f"))
                            else round(float(max_t) * 9 / 5 + 32, 1))
            else:
                disp_max = float(max_t)
            msg = f"Temperatura actual ({disp_temp:.0f}{sym}) supera el umbral máximo ({disp_max:.0f}{sym})"
        elif pd.notna(min_t) and temp < float(min_t):
            disp_temp = settings.convert_temp(temp)
            if unit == "F":
                disp_min = (float(row["alerta_min_temp_f"])
                            if pd.notna(row.get("alerta_min_temp_f"))
                            else round(float(min_t) * 9 / 5 + 32, 1))
            else:
                disp_min = float(min_t)
            msg = f"Temperatura actual ({disp_temp:.0f}{sym}) está bajo el umbral mínimo ({disp_min:.0f}{sym})"

        self._alert_text.value = msg
        self._alert_banner.visible = bool(msg)

    def _on_save_toggle(self, e: ft.ControlEvent) -> None:
        if self._weather_data is None:
            return
        if e.control.value:
            add_city(
                self.username,
                self._weather_data["ciudad"],
                self._weather_data["pais"],
                self._weather_data["latitud"],
                self._weather_data["longitud"],
            )
            self._refresh_dropdown(update=True)

    # ── Unidades de medida ─────────────────────────────────────────────────────

    def _toggle_temp(self, e: ft.ControlEvent) -> None:
        settings.set_temp_unit("F" if settings.get_temp_unit() == "C" else "C")
        self._btn_temp_unit.text = settings.temp_symbol()
        if self._weather_data:
            self._display_weather(self._weather_data)
        self.page.update()

    def _toggle_speed(self, e: ft.ControlEvent) -> None:
        settings.set_speed_unit("mph" if settings.get_speed_unit() == "kmh" else "kmh")
        self._btn_speed_unit.text = settings.speed_symbol()
        if self._weather_data:
            self._display_weather(self._weather_data)
        self.page.update()

    # ── Búsqueda con opciones múltiples ────────────────────────────────────────

    def _show_city_options(self, options: list[dict]) -> None:
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
                on_click=lambda e, o=opt: self._on_city_selected(o),
            )
            for opt in options
        ]
        self._dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Qué ciudad buscas?", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            bgcolor="#0D47A1",
            content=ft.Column(tight=True, controls=tiles, spacing=0, width=380),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._close_dialog(),
                    style=ft.ButtonStyle(color="#90CAF9"),
                ),
            ],
        )
        self._msg.value = ""
        self.page.open(self._dlg)

    def _on_city_selected(self, geo: dict) -> None:
        self._close_dialog()
        self._msg.value = "Consultando…"
        self._msg.color = "#90CAF9"
        self.page.update()

        data = get_current_weather_from_geo(geo)
        if data is None:
            # Sin conexión: intentar cache por nombre de ciudad
            cached = get_weather_cache(geo.get("name", ""), self.username)
            if cached is not None:
                self._show_offline_weather(cached)
                return
            self._msg.value = "Sin conexión a internet."
            self._msg.color = "#EF9A9A"
            self.page.update()
            return

        # Éxito: guardar en cache y ocultar banner offline
        save_weather_cache(data, self.username)
        self._offline_banner.visible = False
        self._weather_data = data
        self._msg.value = ""
        self._display_weather(data)
        self._check_alert(data)

        fav_df = get_cities(self.username)
        is_fav = not fav_df[fav_df["ciudad"].str.lower() == data["ciudad"].lower()].empty
        self._save_checkbox.value = is_fav
        self._save_checkbox.disabled = False
        self.page.update()

    def _close_dialog(self) -> None:
        if self._dlg is not None:
            self.page.close(self._dlg)

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._refresh_dropdown()

        self._weather_card = ft.Container(
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
                            self._weather_icon,
                            ft.Column(
                                spacing=4,
                                controls=[self._city_lbl, self._desc_lbl],
                            ),
                        ],
                    ),
                    self._temp_lbl,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=24,
                        controls=[self._max_lbl, self._min_lbl],
                    ),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=28,
                        controls=[self._sens_lbl, self._wind_lbl, self._hum_lbl],
                    ),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Text("Unidades:", size=12, color="#90CAF9"),
                            self._btn_temp_unit,
                            self._btn_speed_unit,
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
                        controls=[self._city_input, self._search_btn],
                    ),
                    self._dropdown,
                    self._save_checkbox,
                    self._msg,
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
                                self._offline_banner,
                                self._weather_card,
                                self._alert_banner,
                            ],
                        ),
                    ),
                ],
            ),
        )
