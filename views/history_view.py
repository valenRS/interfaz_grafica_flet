# Valentina Rodriguez Sepulveda — 1125789977
# views/history_view.py — Historial meteorológico y gráficas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import base64
import math
import threading
from datetime import datetime, timedelta
from typing import Callable

import flet as ft
import pandas as pd

import utils.settings as settings
from utils.api_client import obtener_historial
from utils.chart_generator import chart_precipitacion, chart_temperatura
from utils.data_manager import obtener_ciudades, obtener_historial_cache, guardar_historial

# ── Helper ────────────────────────────────────────────────────────────────────


def _archivo_a_base64(path: str) -> str:
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

        self._fecha_inicio: datetime = datetime.today() - timedelta(days=30)
        self._dias_consulta: int = 30

        # ── Controles: selección ─────────────────────────────────────────────

        self._lista_ciudades = ft.Dropdown(
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

        self._boton_fecha = ft.ElevatedButton(
            text=self._fecha_inicio.strftime("%d/%m/%Y"),
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._abrir_selector_fecha,
            style=ft.ButtonStyle(
                bgcolor="#0D47A1",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._etiqueta_dias = ft.Text(f"{self._dias_consulta} días", color="#FFFFFF", size=14,
                                 weight=ft.FontWeight.W_500)

        self._deslizador_dias = ft.Slider(
            min=7,
            max=90,
            value=self._dias_consulta,
            divisions=83,
            on_change=self._al_mover_deslizador_dias,
            active_color="#29B6F6",
            inactive_color="#1565C0",
            expand=True,
        )

        self._boton_consultar = ft.ElevatedButton(
            text="Consultar historial",
            icon=ft.Icons.SEARCH,
            on_click=self._al_consultar_historial,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._indicador_carga = ft.ProgressRing(width=30, height=30, stroke_width=4, visible=False)
        self._mensaje_estado = ft.Text("", size=13, color="#EF9A9A")

        # ── Controles: gráficas ───────────────────────────────────────────────

        self._imagen_grafica_temp = ft.Image(
            height=250,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            expand=True,
        )
        self._imagen_grafica_precip = ft.Image(
            height=250,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            expand=True,
        )
        self._etiqueta_grafica_temp = ft.Text(
            "Temperatura (°C)", size=13, color="#90CAF9",
            weight=ft.FontWeight.W_500, visible=False,
        )
        self._etiqueta_grafica_precip = ft.Text(
            "Precipitación acumulada (mm)", size=13, color="#90CAF9",
            weight=ft.FontWeight.W_500, visible=False,
        )

        # ── Controles: estadísticas ──────────────────────────────────────────

        self._est_promedio_max    = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#EF5350")
        self._est_promedio_min    = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#42A5F5")
        self._est_promedio_lluvia   = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#29B6F6")
        self._est_total_lluvia = ft.Text("—", size=20, weight=ft.FontWeight.BOLD, color="#0288D1")

        self._panel_estadisticas_temp = ft.Container(
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
                            self._est_promedio_max,
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Prom. mínima", size=11, color="#80D8FF"),
                            self._est_promedio_min,
                        ],
                    ),
                ],
            ),
        )

        self._panel_estadisticas_lluvia = ft.Container(
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
                            self._est_promedio_lluvia,
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("Total período", size=11, color="#90CAF9"),
                            self._est_total_lluvia,
                        ],
                    ),
                ],
            ),
        )

        # DatePicker — rango limitado a 91 días atrás (tope del endpoint de forecast)
        self._selector_fecha = ft.DatePicker(
            first_date=datetime.today() - timedelta(days=91),
            last_date=datetime.today() - timedelta(days=1),
            on_change=self._al_cambiar_fecha,
        )
        page.overlay.append(self._selector_fecha)

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

        self._promedio_max_actual: float | None = None
        self._promedio_min_actual: float | None = None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _cambiar_unidad_temperatura(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_temperatura("F" if settings.obtener_unidad_temperatura() == "C" else "C")
        self._boton_cabecera_unidad_temp.text = settings.simbolo_temperatura()

        # Update stats if loaded
        if self._promedio_max_actual is not None and self._promedio_min_actual is not None:
            sym = settings.simbolo_temperatura()
            def _formatear_temperatura(val: float) -> str:
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    return "—"
                converted = settings.convertir_temperatura(val)
                if converted is None or (isinstance(converted, float) and math.isnan(converted)):
                    return "—"
                return f"{converted:.1f}{sym}"
            
            self._est_promedio_max.value = _formatear_temperatura(self._promedio_max_actual)
            self._est_promedio_min.value = _formatear_temperatura(self._promedio_min_actual)

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

    def _abrir_selector_fecha(self, e: ft.ControlEvent) -> None:
        self._selector_fecha.open = True
        self.page.update()

    def _al_cambiar_fecha(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self._fecha_inicio = e.control.value
            self._boton_fecha.text = self._fecha_inicio.strftime("%d/%m/%Y")
            self.page.update()

    def _al_mover_deslizador_dias(self, e: ft.ControlEvent) -> None:
        self._dias_consulta = int(e.control.value)
        self._etiqueta_dias.value = f"{self._dias_consulta} días"
        self.page.update()

    def _al_consultar_historial(self, e: ft.ControlEvent) -> None:
        city = self._lista_ciudades.value
        if not city:
            self._mensaje_estado.value = "Selecciona una ciudad."
            self.page.update()
            return
        self._mensaje_estado.value = ""
        self._mostrar_cargando(True)
        threading.Thread(target=self._cargar_datos_historial, args=(city,), daemon=True).start()

    def _cargar_datos_historial(self, city: str) -> None:
        try:
            yesterday = datetime.today() - timedelta(days=1)
            fin_dt = min(self._fecha_inicio + timedelta(days=self._dias_consulta - 1), yesterday)
            inicio_str = self._fecha_inicio.strftime("%Y-%m-%d")
            fin_str    = fin_dt.strftime("%Y-%m-%d")
            expected   = (fin_dt - self._fecha_inicio).days + 1

            # Intentar cache local primero
            cached = obtener_historial_cache(city, inicio_str, fin_str)
            if not cached.empty and len(cached) >= int(expected * 0.9):
                df = cached
            else:
                cities_df = obtener_ciudades(self.username)
                match = cities_df[cities_df["ciudad"].str.lower() == city.lower()]
                if match.empty:
                    self._mensaje_estado.value = "Coordenadas no encontradas. Agrega la ciudad a favoritas primero."
                    self._mostrar_cargando(False)
                    return

                row = match.iloc[0]
                df = obtener_historial(
                    city,
                    float(row["latitud"]),
                    float(row["longitud"]),
                    inicio_str,
                    fin_str,
                )
                if df is None or df.empty:
                    self._mensaje_estado.value = "No se encontraron datos para ese período."
                    self._mostrar_cargando(False)
                    return
                guardar_historial(df)

            # Generar gráficas
            path_temp = chart_temperatura(df, city)
            path_prec = chart_precipitacion(df, city)

            self._imagen_grafica_temp.src_base64 = _archivo_a_base64(path_temp)
            self._imagen_grafica_precip.src_base64 = _archivo_a_base64(path_prec)
            self._imagen_grafica_temp.visible = True
            self._imagen_grafica_precip.visible = True
            self._etiqueta_grafica_temp.visible = True
            self._etiqueta_grafica_precip.visible = True

            # Calcular estadísticas del período
            sym      = settings.simbolo_temperatura()
            avg_max  = df["temp_max"].astype(float).mean()
            avg_min  = df["temp_min"].astype(float).mean()
            prec     = df["precipitacion"].astype(float).fillna(0)

            def _formatear_temperatura(val: float) -> str:
                """Convierte y formatea una temperatura; devuelve '—' si es NaN/None."""
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    return "—"
                converted = settings.convertir_temperatura(val)
                if converted is None or (isinstance(converted, float) and math.isnan(converted)):
                    return "—"
                return f"{converted:.1f}{sym}"

            self._promedio_max_actual = avg_max
            self._promedio_min_actual = avg_min
            self._est_promedio_max.value    = _formatear_temperatura(avg_max)
            self._est_promedio_min.value    = _formatear_temperatura(avg_min)
            self._est_promedio_lluvia.value   = f"{prec.mean():.1f} mm"
            self._est_total_lluvia.value = f"{prec.sum():.1f} mm"
            self._panel_estadisticas_temp.visible = True
            self._panel_estadisticas_lluvia.visible = True

            self._mensaje_estado.value = f"Mostrando {len(df)} días para {city}."
            self._mensaje_estado.color = "#A5D6A7"

        except Exception as exc:  # noqa: BLE001
            import traceback
            with open("error_log.txt", "a") as f:
                f.write(traceback.format_exc() + "\\n")
            self._mensaje_estado.value = f"Error al cargar datos: {exc}"
            self._mensaje_estado.color = "#EF9A9A"

        finally:
            self._mostrar_cargando(False)

    def _mostrar_cargando(self, val: bool) -> None:
        self._indicador_carga.visible = val
        self._boton_consultar.disabled = val
        self.page.update()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._actualizar_lista_ciudades()

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
                    ft.Container(expand=True),
                    self._boton_cabecera_unidad_temp,
                    self._boton_cabecera_unidad_vel,
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
                            self._lista_ciudades,
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Fecha de inicio", size=12, color="#90CAF9"),
                                    self._boton_fecha,
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text("Días a consultar:", size=13, color="#90CAF9"),
                            self._etiqueta_dias,
                        ],
                    ),
                    ft.Row(controls=[self._deslizador_dias]),
                    ft.Row(
                        spacing=16,
                        controls=[self._boton_consultar, self._indicador_carga],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self._mensaje_estado,
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
                                self._etiqueta_grafica_temp,
                                ft.Row(
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Container(
                                            content=self._imagen_grafica_temp,
                                            bgcolor="#0D47A1",
                                            border_radius=12,
                                            padding=ft.padding.all(12),
                                            shadow=ft.BoxShadow(blur_radius=12, color="black12",
                                                                offset=ft.Offset(0, 4)),
                                            expand=True,
                                        ),
                                        self._panel_estadisticas_temp,
                                    ],
                                ),
                                self._etiqueta_grafica_precip,
                                ft.Row(
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Container(
                                            content=self._imagen_grafica_precip,
                                            bgcolor="#0D47A1",
                                            border_radius=12,
                                            padding=ft.padding.all(12),
                                            shadow=ft.BoxShadow(blur_radius=12, color="black12",
                                                                offset=ft.Offset(0, 4)),
                                            expand=True,
                                        ),
                                        self._panel_estadisticas_lluvia,
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
