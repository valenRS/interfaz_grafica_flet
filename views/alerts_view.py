# Valentina Rodriguez Sepulveda — 1125789977
# views/alerts_view.py — Configuración de alertas de temperatura
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from typing import Callable

import flet as ft
import pandas as pd

import utils.settings as settings
from utils.data_manager import obtener_ciudades, actualizar_alerta


class AlertsView:
    """
    Permite configurar umbrales de temperatura para alertas visuales por ciudad.
    Si al consultar el clima actual se supera el umbral, HomeView muestra un aviso.
    """

    def __init__(self, page: ft.Page, username: str, on_go_home: Callable) -> None:
        self.page = page
        self.username = username
        self.on_go_home = on_go_home

        self._id_ciudad_seleccionada: int | None = None
        self._valor_umbral_max: float = 35.0
        self._valor_umbral_min: float = 5.0

        # ── Controles: selector de ciudad ─────────────────────────────────────

        self._lista_ciudades = ft.Dropdown(
            label="Ciudad favorita",
            hint_text="Seleccionar ciudad",
            options=[],
            on_change=self._al_seleccionar_ciudad_alerta,
            border_radius=8,
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#1565C0",
            width=300,
        )

        # ── Controles: sliders ────────────────────────────────────────────────

        _sym = settings.simbolo_temperatura()
        self._etiqueta_umbral_max = ft.Text(
            f"{settings.convertir_temperatura(self._valor_umbral_max):.0f}{_sym}",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="#FFCC80",
        )
        self._etiqueta_umbral_min = ft.Text(
            f"{settings.convertir_temperatura(self._valor_umbral_min):.0f}{_sym}",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="#80D8FF",
        )

        self._deslizador_umbral_max = ft.Slider(
            min=-20,
            max=50,
            value=self._valor_umbral_max,
            divisions=70,
            on_change=self._al_cambiar_umbral_max,
            active_color="#FF7043",
            inactive_color="#1565C0",
            expand=True,
            disabled=True,
        )

        self._deslizador_umbral_min = ft.Slider(
            min=-20,
            max=50,
            value=self._valor_umbral_min,
            divisions=70,
            on_change=self._al_cambiar_umbral_min,
            active_color="#29B6F6",
            inactive_color="#1565C0",
            expand=True,
            disabled=True,
        )

        # ── Controles: checkbox y botón ───────────────────────────────────────

        self._casilla_alerta_activa = ft.Checkbox(
            label="Activar alerta para esta ciudad",
            value=False,
            label_style=ft.TextStyle(color="#FFFFFF", size=14),
        )

        self._boton_guardar = ft.ElevatedButton(
            text="Guardar configuración",
            icon=ft.Icons.SAVE,
            on_click=self._al_guardar_alerta,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._mensaje_estado = ft.Text("", size=13)

        # ── Controles: resumen de alertas activas ─────────────────────────────

        self._columna_resumen = ft.Column(spacing=8)

        _btn_style = ft.ButtonStyle(
            color="#FFFFFF",
            side=ft.BorderSide(color="#90CAF9", width=1),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )
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

    def _cambiar_unidad_temperatura(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_temperatura("F" if settings.obtener_unidad_temperatura() == "C" else "C")
        self._boton_cabecera_unidad_temp.text = settings.simbolo_temperatura()
        sym = settings.simbolo_temperatura()
        self._etiqueta_umbral_max.value = f"{settings.convertir_temperatura(self._valor_umbral_max):.0f}{sym}"
        self._etiqueta_umbral_min.value = f"{settings.convertir_temperatura(self._valor_umbral_min):.0f}{sym}"
        self._actualizar_resumen_alertas()
        self.page.update()

    def _cambiar_unidad_velocidad(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_velocidad("mph" if settings.obtener_unidad_velocidad() == "kmh" else "kmh")
        self._boton_cabecera_unidad_vel.text = settings.simbolo_velocidad()
        self.page.update()

    def _actualizar_lista_ciudades(self) -> None:
        df = obtener_ciudades(self.username)
        self._lista_ciudades.options = [
            ft.dropdown.Option(str(row["ciudad"])) for _, row in df.iterrows()
        ]

    def _al_seleccionar_ciudad_alerta(self, e: ft.ControlEvent) -> None:
        city_name = e.control.value
        if not city_name:
            self._deslizador_umbral_max.disabled = True
            self._deslizador_umbral_min.disabled = True
            self.page.update()
            return

        df = obtener_ciudades(self.username)
        match = df[df["ciudad"] == city_name]
        if match.empty:
            return

        row = match.iloc[0]
        self._id_ciudad_seleccionada = int(row["id"])

        max_t = row["alerta_max_temp"]
        min_t = row["alerta_min_temp"]
        has_alert = pd.notna(max_t) and pd.notna(min_t)

        self._casilla_alerta_activa.value = has_alert

        if has_alert:
            self._valor_umbral_max = float(max_t)
            self._valor_umbral_min = float(min_t)
        else:
            self._valor_umbral_max = 35.0
            self._valor_umbral_min = 5.0

        self._deslizador_umbral_max.value = self._valor_umbral_max
        self._deslizador_umbral_min.value = self._valor_umbral_min
        self._deslizador_umbral_max.disabled = False
        self._deslizador_umbral_min.disabled = False
        sym = settings.simbolo_temperatura()
        self._etiqueta_umbral_max.value = f"{settings.convertir_temperatura(self._valor_umbral_max):.0f}{sym}"
        self._etiqueta_umbral_min.value = f"{settings.convertir_temperatura(self._valor_umbral_min):.0f}{sym}"
        self._mensaje_estado.value = ""
        self.page.update()

    def _al_cambiar_umbral_max(self, e: ft.ControlEvent) -> None:
        self._valor_umbral_max = float(e.control.value)
        # Forzar que máximo no sea menor al mínimo
        if self._valor_umbral_max <= self._valor_umbral_min:
            self._valor_umbral_max = self._valor_umbral_min + 1
            self._deslizador_umbral_max.value = self._valor_umbral_max
        self._etiqueta_umbral_max.value = f"{settings.convertir_temperatura(self._valor_umbral_max):.0f}{settings.simbolo_temperatura()}"
        self.page.update()

    def _al_cambiar_umbral_min(self, e: ft.ControlEvent) -> None:
        self._valor_umbral_min = float(e.control.value)
        # Forzar que mínimo no sea mayor al máximo
        if self._valor_umbral_min >= self._valor_umbral_max:
            self._valor_umbral_min = self._valor_umbral_max - 1
            self._deslizador_umbral_min.value = self._valor_umbral_min
        self._etiqueta_umbral_min.value = f"{settings.convertir_temperatura(self._valor_umbral_min):.0f}{settings.simbolo_temperatura()}"
        self.page.update()

    def _al_guardar_alerta(self, e: ft.ControlEvent) -> None:
        if self._id_ciudad_seleccionada is None:
            self._mensaje_estado.value = "Selecciona primero una ciudad."
            self._mensaje_estado.color = "#FFCC80"
            self.page.update()
            return

        if self._casilla_alerta_activa.value:
            actualizar_alerta(self._id_ciudad_seleccionada, self._valor_umbral_max, self._valor_umbral_min)
            self._mensaje_estado.value = "Alertas guardadas correctamente."
            self._mensaje_estado.color = "#A5D6A7"
        else:
            actualizar_alerta(self._id_ciudad_seleccionada, None, None)
            self._mensaje_estado.value = "Alerta desactivada para esta ciudad."
            self._mensaje_estado.color = "#90CAF9"

        self._actualizar_resumen_alertas()
        self.page.update()

    def _actualizar_resumen_alertas(self) -> None:
        df = obtener_ciudades(self.username)
        active = df[pd.notna(df["alerta_max_temp"]) & pd.notna(df["alerta_min_temp"])]
        self._columna_resumen.controls.clear()

        unit = settings.obtener_unidad_temperatura()
        sym  = settings.simbolo_temperatura()

        if active.empty:
            self._columna_resumen.controls.append(
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

                self._columna_resumen.controls.append(
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
        self._actualizar_lista_ciudades()
        self._actualizar_resumen_alertas()

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
                    self._boton_cabecera_unidad_temp,
                    self._boton_cabecera_unidad_vel,
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
                    self._lista_ciudades,
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
                                        self._etiqueta_umbral_max,
                                    ],
                                    spacing=8,
                                ),
                                ft.Row(controls=[self._deslizador_umbral_max]),
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
                                        self._etiqueta_umbral_min,
                                    ],
                                    spacing=8,
                                ),
                                ft.Row(controls=[self._deslizador_umbral_min]),
                            ],
                        ),
                    ),
                    self._casilla_alerta_activa,
                    ft.Row(
                        spacing=16,
                        controls=[self._boton_guardar, self._mensaje_estado],
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
                    self._columna_resumen,
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
