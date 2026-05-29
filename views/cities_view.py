# Valentina Rodriguez Sepulveda — 1125789977
# views/cities_view.py — Gestión de ciudades favoritas
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

from typing import Callable

import flet as ft

from utils.api_client import geocode_city
from utils.data_manager import add_city, delete_city, get_cities


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
        self._checkboxes: dict[int, ft.Checkbox] = {}

        # ── Controles: agregar ciudad ─────────────────────────────────────────

        self._new_city_input = ft.TextField(
            label="Nueva ciudad",
            hint_text="Ej: Tokio, Berlín, Cape Town…",
            prefix_icon=ft.Icons.ADD_LOCATION_ALT,
            border_color="#29B6F6",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            bgcolor="#0D47A1",
            border_radius=8,
            on_submit=self._on_add_city,
            expand=True,
        )

        self._add_btn = ft.ElevatedButton(
            text="Agregar",
            icon=ft.Icons.ADD,
            on_click=self._on_add_city,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self._msg = ft.Text("", size=13)

        # ── Controles: lista y conteo ─────────────────────────────────────────

        self._count_lbl = ft.Text("", size=14, color="#90CAF9", weight=ft.FontWeight.W_500)
        self._cities_column = ft.Column(spacing=8)

        self._delete_btn = ft.ElevatedButton(
            text="Eliminar seleccionadas",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=self._on_delete,
            visible=False,
            style=ft.ButtonStyle(
                bgcolor="#B71C1C",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        df = get_cities(self.username)
        self._checkboxes.clear()
        self._cities_column.controls.clear()

        count = len(df)
        noun = "ciudad" if count == 1 else "ciudades"
        self._count_lbl.value = f"{count} {noun} guardadas"
        self._delete_btn.visible = count > 0

        for _, row in df.iterrows():
            city_id = int(row["id"])
            cb = ft.Checkbox(
                label=f"{row['ciudad']},  {row['pais']}",
                value=False,
                label_style=ft.TextStyle(color="#FFFFFF", size=14),
            )
            self._checkboxes[city_id] = cb

            self._cities_column.controls.append(
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

    def _on_add_city(self, e: ft.ControlEvent) -> None:
        city_name = (self._new_city_input.value or "").strip()
        if not city_name:
            return

        self._msg.value = "Buscando ciudad…"
        self._msg.color = "#90CAF9"
        self.page.update()

        geo = geocode_city(city_name)
        if geo is None:
            self._msg.value = "Ciudad no encontrada o sin conexión a internet."
            self._msg.color = "#EF9A9A"
            self.page.update()
            return

        ok = add_city(self.username, geo["name"], geo["country"], geo["latitude"], geo["longitude"])
        if not ok:
            self._msg.value = f'"{geo["name"]}" ya está en tu lista.'
            self._msg.color = "#FFCC80"
        else:
            self._msg.value = f'"{geo["name"]}" agregada correctamente.'
            self._msg.color = "#A5D6A7"
            self._new_city_input.value = ""
            self._refresh_list()

        self.page.update()

    def _on_delete(self, e: ft.ControlEvent) -> None:
        ids_to_delete = [
            city_id for city_id, cb in self._checkboxes.items() if cb.value
        ]
        if not ids_to_delete:
            self._msg.value = "Selecciona al menos una ciudad para eliminar."
            self._msg.color = "#FFCC80"
            self.page.update()
            return

        for city_id in ids_to_delete:
            delete_city(self.username, city_id)

        n = len(ids_to_delete)
        self._msg.value = f"{n} {'ciudad eliminada' if n == 1 else 'ciudades eliminadas'}."
        self._msg.color = "#A5D6A7"
        self._refresh_list()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._refresh_list()

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
                    self._count_lbl,
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
                        controls=[self._new_city_input, self._add_btn],
                    ),
                    self._msg,
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
                    self._cities_column,
                    self._delete_btn,
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
