# Valentina Rodriguez Sepulveda — 1125789977
# views/alerts_view.py — Configuración de alertas de temperatura
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from typing import Callable

import flet as ft
import pandas as pd

import utils.settings as settings
from utils.data_manager import get_cities, update_alert


class AlertsView:
    """
    Permite configurar umbrales de temperatura para alertas visuales por ciudad.
    Si al consultar el clima actual se supera el umbral, HomeView muestra un aviso.
    """

    def __init__(self, page: ft.Page, username: str, on_go_home: Callable) -> None:
        self.page = page
        self.username = username
        self.on_go_home = on_go_home

        self._selected_city_id: int | None = None
        self._max_val: float = 35.0
        self._min_val: float = 5.0

        # ── Controles: selector de ciudad ─────────────────────────────────────

        self._city_dropdown = ft.Dropdown(
            label="Ciudad favorita",
            hint_text="Seleccionar ciudad",
            options=[],
            on_change=self._on_city_select,
            border_radius=8,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            width=300,
        )

        # ── Controles: sliders ────────────────────────────────────────────────

        _sym = settings.temp_symbol()
        self._max_val_lbl = ft.Text(
            f"{settings.convert_temp(self._max_val):.0f}{_sym}",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="#FFCC80",
        )
        self._min_val_lbl = ft.Text(
            f"{settings.convert_temp(self._min_val):.0f}{_sym}",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="#80D8FF",
        )

        self._max_slider = ft.Slider(
            min=-20,
            max=50,
            value=self._max_val,
            divisions=70,
            on_change=self._on_max_change,
            active_color="#FF7043",
            inactive_color="#1565C0",
            expand=True,
            disabled=True,
        )

        self._min_slider = ft.Slider(
            min=-20,
            max=50,
            value=self._min_val,
            divisions=70,
            on_change=self._on_min_change,
            active_color="#29B6F6",
            inactive_color="#1565C0",
            expand=True,
            disabled=True,
        )

        # ── Controles: checkbox y botón ───────────────────────────────────────

        self._active_checkbox = ft.Checkbox(
            label="Activar alerta para esta ciudad",
            value=False,
            label_style=ft.TextStyle(color="#FFFFFF", size=14),
        )

        self._save_btn = ft.ElevatedButton(
            text="Guardar configuración",
            icon=ft.Icons.SAVE,
            on_click=self._on_save,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._msg = ft.Text("", size=13)

        # ── Controles: resumen de alertas activas ─────────────────────────────

        self._summary_column = ft.Column(spacing=8)

        _btn_style = ft.ButtonStyle(
            color="#FFFFFF",
            side=ft.BorderSide(color="#90CAF9", width=1),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )
        self._hdr_btn_temp_unit = ft.OutlinedButton(
            text=settings.temp_symbol(),
            on_click=self._toggle_temp,
            style=_btn_style,
            height=28,
        )
        self._hdr_btn_speed_unit = ft.OutlinedButton(
            text=settings.speed_symbol(),
            on_click=self._toggle_speed,
            style=_btn_style,
            height=28,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _toggle_temp(self, e: ft.ControlEvent) -> None:
        settings.set_temp_unit("F" if settings.get_temp_unit() == "C" else "C")
        self._hdr_btn_temp_unit.text = settings.temp_symbol()
        sym = settings.temp_symbol()
        self._max_val_lbl.value = f"{settings.convert_temp(self._max_val):.0f}{sym}"
        self._min_val_lbl.value = f"{settings.convert_temp(self._min_val):.0f}{sym}"
        self._refresh_summary()
        self.page.update()

    def _toggle_speed(self, e: ft.ControlEvent) -> None:
        settings.set_speed_unit("mph" if settings.get_speed_unit() == "kmh" else "kmh")
        self._hdr_btn_speed_unit.text = settings.speed_symbol()
        self.page.update()

    def _refresh_dropdown(self) -> None:
        df = get_cities(self.username)
        self._city_dropdown.options = [
            ft.dropdown.Option(str(row["ciudad"])) for _, row in df.iterrows()
        ]

    def _on_city_select(self, e: ft.ControlEvent) -> None:
        city_name = e.control.value
        if not city_name:
            self._max_slider.disabled = True
            self._min_slider.disabled = True
            self.page.update()
            return

        df = get_cities(self.username)
        match = df[df["ciudad"] == city_name]
        if match.empty:
            return

        row = match.iloc[0]
        self._selected_city_id = int(row["id"])

        max_t = row["alerta_max_temp"]
        min_t = row["alerta_min_temp"]
        has_alert = pd.notna(max_t) and pd.notna(min_t)

        self._active_checkbox.value = has_alert

        if has_alert:
            self._max_val = float(max_t)
            self._min_val = float(min_t)
        else:
            self._max_val = 35.0
            self._min_val = 5.0

        self._max_slider.value = self._max_val
        self._min_slider.value = self._min_val
        self._max_slider.disabled = False
        self._min_slider.disabled = False
        sym = settings.temp_symbol()
        self._max_val_lbl.value = f"{settings.convert_temp(self._max_val):.0f}{sym}"
        self._min_val_lbl.value = f"{settings.convert_temp(self._min_val):.0f}{sym}"
        self._msg.value = ""
        self.page.update()

    def _on_max_change(self, e: ft.ControlEvent) -> None:
        self._max_val = float(e.control.value)
        # Forzar que máximo no sea menor al mínimo
        if self._max_val <= self._min_val:
            self._max_val = self._min_val + 1
            self._max_slider.value = self._max_val
        self._max_val_lbl.value = f"{settings.convert_temp(self._max_val):.0f}{settings.temp_symbol()}"
        self.page.update()

    def _on_min_change(self, e: ft.ControlEvent) -> None:
        self._min_val = float(e.control.value)
        # Forzar que mínimo no sea mayor al máximo
        if self._min_val >= self._max_val:
            self._min_val = self._max_val - 1
            self._min_slider.value = self._min_val
        self._min_val_lbl.value = f"{settings.convert_temp(self._min_val):.0f}{settings.temp_symbol()}"
        self.page.update()

    def _on_save(self, e: ft.ControlEvent) -> None:
        if self._selected_city_id is None:
            self._msg.value = "Selecciona primero una ciudad."
            self._msg.color = "#FFCC80"
            self.page.update()
            return

        if self._active_checkbox.value:
            update_alert(self._selected_city_id, self._max_val, self._min_val)
            self._msg.value = "Alertas guardadas correctamente."
            self._msg.color = "#A5D6A7"
        else:
            update_alert(self._selected_city_id, None, None)
            self._msg.value = "Alerta desactivada para esta ciudad."
            self._msg.color = "#90CAF9"

        self._refresh_summary()
        self.page.update()

    def _refresh_summary(self) -> None:
        df = get_cities(self.username)
        active = df[pd.notna(df["alerta_max_temp"]) & pd.notna(df["alerta_min_temp"])]
        self._summary_column.controls.clear()

        unit = settings.get_temp_unit()
        sym  = settings.temp_symbol()

        if active.empty:
            self._summary_column.controls.append(
                ft.Text("Sin alertas activas.", size=13, color="#90CAF9")
            )
        else:
            for _, row in active.iterrows():
                # Leer columna pre-calculada; si aún no existe (CSV antiguo) calcular
                if unit == "F":
                    max_v = (float(row["alerta_max_temp_f"])
                             if pd.notna(row.get("alerta_max_temp_f"))
                             else round(float(row["alerta_max_temp"]) * 9 / 5 + 32, 1))
                    min_v = (float(row["alerta_min_temp_f"])
                             if pd.notna(row.get("alerta_min_temp_f"))
                             else round(float(row["alerta_min_temp"]) * 9 / 5 + 32, 1))
                else:
                    max_v = float(row["alerta_max_temp"])
                    min_v = float(row["alerta_min_temp"])

                self._summary_column.controls.append(
                    ft.Container(
                        bgcolor="#0D47A1",
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        content=ft.Row(
                            spacing=12,
                            controls=[
                                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="#FFA726", size=20),
                                ft.Text(
                                    f"{row['ciudad']}",
                                    color="#FFFFFF",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"↑{max_v:.0f}{sym}",
                                    color="#FFCC80",
                                    size=13,
                                ),
                                ft.Text(
                                    f"↓{min_v:.0f}{sym}",
                                    color="#80D8FF",
                                    size=13,
                                ),
                            ],
                        ),
                    )
                )

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._refresh_dropdown()
        self._refresh_summary()

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
                    ft.Icon(ft.Icons.NOTIFICATIONS, color="#FFA726", size=24),
                    ft.Text(
                        "Alertas de Temperatura",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    ft.Container(expand=True),
                    self._hdr_btn_temp_unit,
                    self._hdr_btn_speed_unit,
                ],
            ),
        )

        config_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Text(
                        "Configurar alerta",
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color="#FFFFFF",
                    ),
                    self._city_dropdown,
                    # Slider temperatura máxima
                    ft.Container(
                        bgcolor="#0D47A1",
                        border_radius=10,
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.THERMOSTAT, color="#FF7043", size=20),
                                        ft.Text(
                                            "Temperatura máxima de alerta",
                                            size=14,
                                            color="#FFFFFF",
                                            expand=True,
                                        ),
                                        self._max_val_lbl,
                                    ],
                                    spacing=8,
                                ),
                                ft.Row(controls=[self._max_slider]),
                            ],
                        ),
                    ),
                    # Slider temperatura mínima
                    ft.Container(
                        bgcolor="#0D47A1",
                        border_radius=10,
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.AC_UNIT, color="#29B6F6", size=20),
                                        ft.Text(
                                            "Temperatura mínima de alerta",
                                            size=14,
                                            color="#FFFFFF",
                                            expand=True,
                                        ),
                                        self._min_val_lbl,
                                    ],
                                    spacing=8,
                                ),
                                ft.Row(controls=[self._min_slider]),
                            ],
                        ),
                    ),
                    self._active_checkbox,
                    ft.Row(
                        spacing=16,
                        controls=[self._save_btn, self._msg],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
            ),
        )

        summary_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="#FFA726", size=22),
                            ft.Text(
                                "Alertas activas",
                                size=15,
                                weight=ft.FontWeight.W_600,
                                color="#FFFFFF",
                            ),
                        ],
                    ),
                    self._summary_column,
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
                            scroll=ft.ScrollMode.AUTO,
                            spacing=20,
                            controls=[config_panel, summary_panel],
                        ),
                    ),
                ],
            ),
        )
