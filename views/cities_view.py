# Valentina Rodriguez Sepulveda — 1125789977
# views/cities_view.py — Gestión de ciudades favoritas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from typing import Callable

import flet as ft

import utils.settings as settings
from utils.api_client import geocodificar_ciudad
from utils.data_manager import agregar_ciudad, eliminar_ciudad, obtener_ciudades


class CitiesView:
    """
    Permite ver, agregar y eliminar ciudades de la lista de favoritas.
    Las ciudades guardadas quedan disponibles en el dropdown de toda la app.
    """

    def __init__(self, page: ft.Page, username: str, on_go_home: Callable) -> None:
        self.page = page
        self.username = username
        self.on_go_home = on_go_home

        # city_id → Checkbox
        self._casillas_verificacion: dict[int, ft.Checkbox] = {}

        # ── Controles: agregar ciudad ─────────────────────────────────────────

        self._entrada_nueva_ciudad = ft.TextField(
            label="Nueva ciudad",
            hint_text="Ej: Tokio, Berlín, Cape Town…",
            prefix_icon=ft.Icons.ADD_LOCATION_ALT,
            border_color="#29B6F6",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#0D47A1",
            border_radius=8,
            on_submit=self._al_agregar_ciudad,
            expand=True,
        )

        self._boton_agregar = ft.ElevatedButton(
            text="Agregar",
            icon=ft.Icons.ADD,
            on_click=self._al_agregar_ciudad,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._mensaje_estado = ft.Text("", size=13)

        # ── Controles: lista y conteo ─────────────────────────────────────────

        self._etiqueta_conteo = ft.Text("", size=14, color="#90CAF9", weight=ft.FontWeight.W_500)
        self._columna_lista_ciudades = ft.Column(spacing=8)

        self._boton_eliminar = ft.ElevatedButton(
            text="Eliminar seleccionadas",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=self._al_eliminar_ciudades,
            visible=False,
            style=ft.ButtonStyle(
                bgcolor="#B71C1C",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

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
        self.page.update()

    def _cambiar_unidad_velocidad(self, e: ft.ControlEvent) -> None:
        settings.establecer_unidad_velocidad("mph" if settings.obtener_unidad_velocidad() == "kmh" else "kmh")
        self._boton_cabecera_unidad_vel.text = settings.simbolo_velocidad()
        self.page.update()

    def _actualizar_lista_ciudades(self) -> None:
        df = obtener_ciudades(self.username)
        self._casillas_verificacion.clear()
        self._columna_lista_ciudades.controls.clear()

        count = len(df)
        noun = "ciudad" if count == 1 else "ciudades"
        self._etiqueta_conteo.value = f"{count} {noun} guardadas"
        self._boton_eliminar.visible = count > 0

        for _, row in df.iterrows():
            city_id = int(row["id"])
            cb = ft.Checkbox(
                label=f"{row['ciudad']},  {row['pais']}",
                value=False,
                label_style=ft.TextStyle(color="#FFFFFF", size=14),
            )
            self._casillas_verificacion[city_id] = cb

            self._columna_lista_ciudades.controls.append(
                ft.Container(
                    bgcolor="#0D47A1",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, color="#29B6F6", size=20),
                            cb,
                        ],
                    ),
                )
            )

        self.page.update()

    def _al_agregar_ciudad(self, e: ft.ControlEvent) -> None:
        city_name = (self._entrada_nueva_ciudad.value or "").strip()
        if not city_name:
            return

        self._mensaje_estado.value = "Buscando ciudad…"
        self._mensaje_estado.color = "#90CAF9"
        self.page.update()

        geo = geocodificar_ciudad(city_name)
        if geo is None:
            self._mensaje_estado.value = "Ciudad no encontrada o sin conexión a internet."
            self._mensaje_estado.color = "#EF9A9A"
            self.page.update()
            return

        ok = agregar_ciudad(self.username, geo["name"], geo["country"], geo["latitude"], geo["longitude"])
        if not ok:
            self._mensaje_estado.value = f'"{geo["name"]}" ya está en tu lista.'
            self._mensaje_estado.color = "#FFCC80"
        else:
            self._mensaje_estado.value = f'"{geo["name"]}" agregada correctamente.'
            self._mensaje_estado.color = "#A5D6A7"
            self._entrada_nueva_ciudad.value = ""
            self._actualizar_lista_ciudades()

        self.page.update()

    def _al_eliminar_ciudades(self, e: ft.ControlEvent) -> None:
        ids_to_delete = [
            city_id for city_id, cb in self._casillas_verificacion.items() if cb.value
        ]
        if not ids_to_delete:
            self._mensaje_estado.value = "Selecciona al menos una ciudad para eliminar."
            self._mensaje_estado.color = "#FFCC80"
            self.page.update()
            return

        for city_id in ids_to_delete:
            eliminar_ciudad(self.username, city_id)

        n = len(ids_to_delete)
        self._mensaje_estado.value = f"{n} {'ciudad eliminada' if n == 1 else 'ciudades eliminadas'}."
        self._mensaje_estado.color = "#A5D6A7"
        self._actualizar_lista_ciudades()

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
                    ft.Icon(ft.Icons.LOCATION_CITY, color="#29B6F6", size=24),
                    ft.Text(
                        "Ciudades Favoritas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    ft.Container(expand=True),
                    self._boton_cabecera_unidad_temp,
                    self._boton_cabecera_unidad_vel,
                    self._etiqueta_conteo,
                ],
            ),
        )

        add_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Agregar ciudad",
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color="#FFFFFF",
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[self._entrada_nueva_ciudad, self._boton_agregar],
                    ),
                    self._mensaje_estado,
                ],
            ),
        )

        list_panel = ft.Container(
            bgcolor="#1565C0",
            border_radius=12,
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Mis ciudades",
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color="#FFFFFF",
                    ),
                    self._columna_lista_ciudades,
                    self._boton_eliminar,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor="#29B6F6",
            content=ft.Column(
                spacing=0,
                controls=[
                    header,
                    ft.Container(
                        expand=True,
                        bgcolor="#1976D2",
                        padding=ft.padding.all(20),
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            spacing=20,
                            controls=[add_panel, list_panel],
                        ),
                    ),
                ],
            ),
        )
