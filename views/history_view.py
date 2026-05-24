# Valentina Rodriguez Sepulveda — 1121789977
# views/history_view.py — Historial meteorológico y gráficas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import base64
import threading
from datetime import datetime, timedelta
from typing import Callable

import flet as ft
import pandas as pd

import utils.settings as settings
from utils.api_client import get_historical
from utils.chart_generator import chart_precipitacion, chart_temperatura
from utils.data_manager import get_cities, get_history, save_history

# ── Helper ────────────────────────────────────────────────────────────────────


def _file_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── Vista ─────────────────────────────────────────────────────────────────────


class HistoryView:
    """
    Muestra el historial meteorológico de una ciudad favorita en un rango de fechas.
    Genera y muestra dos gráficas (temperatura y precipitación) con matplotlib.
    Usa la cache local (historial_clima.csv) antes de llamar a la API.
    """

    def __init__(self, page: ft.Page, username: str, on_go_home: Callable) -> None:
        self.page = page
        self.username = username
        self.on_go_home = on_go_home

        self._start_date: datetime = datetime.today() - timedelta(days=30)
        self._days: int = 30

        # ── Controles: selección ─────────────────────────────────────────────

        self._city_dropdown = ft.Dropdown(
            label="Ciudad",
            hint_text="Seleccionar ciudad favorita",
            options=[],
            border_radius=8,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            width=260,
        )

        self._date_btn = ft.ElevatedButton(
            text=self._start_date.strftime("%d/%m/%Y"),
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._open_date_picker,
            style=ft.ButtonStyle(
                bgcolor="#0D47A1",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._days_lbl = ft.Text(f"{self._days} días", color="#FFFFFF", size=14,
                                 weight=ft.FontWeight.W_500)

        self._slider = ft.Slider(
            min=7,
            max=90,
            value=self._days,
            divisions=83,
            on_change=self._on_slider_change,
            active_color="#29B6F6",
            inactive_color="#1565C0",
            expand=True,
        )

        self._consult_btn = ft.ElevatedButton(
            text="Consultar historial",
            icon=ft.Icons.SEARCH,
            on_click=self._on_consult,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._loading = ft.ProgressRing(width=30, height=30, stroke_width=4, visible=False)
        self._msg = ft.Text("", size=13, color="#EF9A9A")

        # ── Controles: gráficas ───────────────────────────────────────────────

        self._chart_temp = ft.Image(
            height=250,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            expand=True,
        )
        self._chart_prec = ft.Image(
            height=250,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            expand=True,
        )
        self._chart_label_temp = ft.Text(
            "Temperatura (°C)", size=13, color="#90CAF9",
            weight=ft.FontWeight.W_500, visible=False,
        )
        self._chart_label_prec = ft.Text(
            "Precipitación acumulada (mm)", size=13, color="#90CAF9",
            weight=ft.FontWeight.W_500, visible=False,
        )

        # ── Controles: estadísticas ──────────────────────────────────────────

        self._stat_avg_max    = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#EF5350")
        self._stat_avg_min    = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#42A5F5")
        self._stat_avg_prec   = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#29B6F6")
        self._stat_total_prec = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#0288D1")

        self._stats_temp_panel = ft.Container(
            visible=False,
            bgcolor="#0D47A1",
            border_radius=12,
            padding=ft.padding.all(16),
            width=162,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text("Estadísticas", size=12, weight=ft.FontWeight.W_600, color="#90CAF9"),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Prom. máxima", size=11, color="#FFCC80"),
                            self._stat_avg_max,
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Prom. mínima", size=11, color="#80D8FF"),
                            self._stat_avg_min,
                        ],
                    ),
                ],
            ),
        )

        self._stats_prec_panel = ft.Container(
            visible=False,
            bgcolor="#0D47A1",
            border_radius=12,
            padding=ft.padding.all(16),
            width=162,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text("Estadísticas", size=12, weight=ft.FontWeight.W_600, color="#90CAF9"),
                    ft.Divider(color="#1565C0", height=1),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Prom. diaria", size=11, color="#90CAF9"),
                            self._stat_avg_prec,
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Total período", size=11, color="#90CAF9"),
                            self._stat_total_prec,
                        ],
                    ),
                ],
            ),
        )

        # DatePicker — rango limitado a 91 días atrás (tope del endpoint de forecast)
        self._date_picker = ft.DatePicker(
            first_date=datetime.today() - timedelta(days=91),
            last_date=datetime.today() - timedelta(days=1),
            on_change=self._on_date_change,
        )
        page.overlay.append(self._date_picker)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_dropdown(self) -> None:
        df = get_cities()
        self._city_dropdown.options = [
            ft.dropdown.Option(str(row["ciudad"])) for _, row in df.iterrows()
        ]

    def _open_date_picker(self, e: ft.ControlEvent) -> None:
        self._date_picker.open = True
        self.page.update()

    def _on_date_change(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self._start_date = e.control.value
            self._date_btn.text = self._start_date.strftime("%d/%m/%Y")
            self.page.update()

    def _on_slider_change(self, e: ft.ControlEvent) -> None:
        self._days = int(e.control.value)
        self._days_lbl.value = f"{self._days} días"
        self.page.update()

    def _on_consult(self, e: ft.ControlEvent) -> None:
        city = self._city_dropdown.value
        if not city:
            self._msg.value = "Selecciona una ciudad."
            self.page.update()
            return
        self._msg.value = ""
        self._show_loading(True)
        threading.Thread(target=self._load_data, args=(city,), daemon=True).start()

    def _load_data(self, city: str) -> None:
        try:
            yesterday = datetime.today() - timedelta(days=1)
            fin_dt = min(self._start_date + timedelta(days=self._days - 1), yesterday)
            inicio_str = self._start_date.strftime("%Y-%m-%d")
            fin_str    = fin_dt.strftime("%Y-%m-%d")
            expected   = (fin_dt - self._start_date).days + 1

            # Intentar cache local primero
            cached = get_history(city, inicio_str, fin_str)
            if not cached.empty and len(cached) >= int(expected * 0.9):
                df = cached
            else:
                cities_df = get_cities()
                match = cities_df[cities_df["ciudad"].str.lower() == city.lower()]
                if match.empty:
                    self._msg.value = "Coordenadas no encontradas. Agrega la ciudad a favoritas primero."
                    self._show_loading(False)
                    return

                row = match.iloc[0]
                df = get_historical(
                    city,
                    float(row["latitud"]),
                    float(row["longitud"]),
                    inicio_str,
                    fin_str,
                )
                if df is None or df.empty:
                    self._msg.value = "No se encontraron datos para ese período."
                    self._show_loading(False)
                    return
                save_history(df)

            # Generar gráficas
            path_temp = chart_temperatura(df, city)
            path_prec = chart_precipitacion(df, city)

            self._chart_temp.src_base64 = _file_to_b64(path_temp)
            self._chart_prec.src_base64 = _file_to_b64(path_prec)
            self._chart_temp.visible = True
            self._chart_prec.visible = True
            self._chart_label_temp.visible = True
            self._chart_label_prec.visible = True

            # Calcular estadísticas del período
            sym      = settings.temp_symbol()
            avg_max  = df["temp_max"].astype(float).mean()
            avg_min  = df["temp_min"].astype(float).mean()
            prec     = df["precipitacion"].astype(float).fillna(0)

            self._stat_avg_max.value    = f"{settings.convert_temp(avg_max):.1f}{sym}"
            self._stat_avg_min.value    = f"{settings.convert_temp(avg_min):.1f}{sym}"
            self._stat_avg_prec.value   = f"{prec.mean():.1f} mm"
            self._stat_total_prec.value = f"{prec.sum():.1f} mm"
            self._stats_temp_panel.visible = True
            self._stats_prec_panel.visible = True

            self._msg.value = f"Mostrando {len(df)} días para {city}."
            self._msg.color = "#A5D6A7"

        except Exception as exc:  # noqa: BLE001
            self._msg.value = f"Error al cargar datos: {exc}"
            self._msg.color = "#EF9A9A"

        finally:
            self._show_loading(False)

    def _show_loading(self, val: bool) -> None:
        self._loading.visible = val
        self._consult_btn.disabled = val
        self.page.update()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._refresh_dropdown()

        header = ft.Container(
            bgcolor="#0D47A1",
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="#FFFFFF",
                        tooltip="Volver al inicio",
                        on_click=lambda _: self.on_go_home(),
                    ),
                    ft.Icon(ft.Icons.BAR_CHART, color="#29B6F6", size=24),
                    ft.Text(
                        "Historial Meteorológico",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                ],
            ),
        )

        controls_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        wrap=True,
                        spacing=20,
                        controls=[
                            self._city_dropdown,
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Fecha de inicio", size=12, color="#90CAF9"),
                                    self._date_btn,
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text("Días a consultar:", size=13, color="#90CAF9"),
                            self._days_lbl,
                        ],
                    ),
                    ft.Row(controls=[self._slider]),
                    ft.Row(
                        spacing=16,
                        controls=[self._consult_btn, self._loading],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self._msg,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor="#1565C0",
            content=ft.Column(
                spacing=0,
                controls=[
                    header,
                    ft.Container(
                        expand=True,
                        padding=ft.padding.all(20),
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            spacing=20,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                controls_panel,
                                self._chart_label_temp,
                                ft.Row(
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Container(
                                            content=self._chart_temp,
                                            bgcolor="#0D47A1",
                                            border_radius=12,
                                            padding=ft.padding.all(12),
                                            shadow=ft.BoxShadow(blur_radius=12, color="black12",
                                                                offset=ft.Offset(0, 4)),
                                            expand=True,
                                        ),
                                        self._stats_temp_panel,
                                    ],
                                ),
                                self._chart_label_prec,
                                ft.Row(
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Container(
                                            content=self._chart_prec,
                                            bgcolor="#0D47A1",
                                            border_radius=12,
                                            padding=ft.padding.all(12),
                                            shadow=ft.BoxShadow(blur_radius=12, color="black12",
                                                                offset=ft.Offset(0, 4)),
                                            expand=True,
                                        ),
                                        self._stats_prec_panel,
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
