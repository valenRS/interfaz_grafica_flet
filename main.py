# Valentina Rodriguez Sepulveda — 1125789977
# main.py — Punto de entrada y controlador de navegación
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import flet as ft

from views.login_view import LoginView
from views.home_view import HomeView
from views.history_view import HistoryView
from views.cities_view import CitiesView
from views.alerts_view import AlertsView


def main(page: ft.Page) -> None:
    page.title = "MeteoApp — Dashboard Meteorológico Personal"
    page.window_width = 960
    page.window_height = 680
    page.window_min_width = 800
    page.window_min_height = 580
    page.bgcolor = "#1565C0"
    page.padding = 0
    page.fonts = {"Roboto": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5WZLCzYlKw.ttf"}
    page.theme = ft.Theme(font_family="Roboto")

    # Referencia al DatePicker activo de HistoryView (para limpiarlo al navegar)
    _selector_fecha_activo: list[ft.DatePicker] = []

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _limpiar_pagina() -> None:
        """Limpia controles y el overlay del DatePicker si hay uno activo."""
        if _selector_fecha_activo:
            dp = _selector_fecha_activo.pop()
            try:
                page.overlay.remove(dp)
            except ValueError:
                pass
        page.controls.clear()

    # ── Vistas ────────────────────────────────────────────────────────────────

    def mostrar_inicio_sesion() -> None:
        _limpiar_pagina()
        view = LoginView(page, on_login_success=mostrar_inicio)
        page.add(view.build())

    def mostrar_inicio(username: str) -> None:
        _limpiar_pagina()
        view = HomeView(
            page,
            username,
            on_go_history=lambda: mostrar_historial(username),
            on_go_cities=lambda: mostrar_ciudades(username),
            on_go_alerts=lambda: mostrar_alertas(username),
            on_logout=mostrar_inicio_sesion,
        )
        page.add(view.build())

    def mostrar_historial(username: str) -> None:
        _limpiar_pagina()
        view = HistoryView(
            page,
            username,
            on_go_home=lambda: mostrar_inicio(username),
        )
        # HistoryView agrega su DatePicker al overlay en __init__;
        # lo registramos para poder limpiarlo al navegar.
        if page.overlay:
            for ctrl in reversed(page.overlay):
                if isinstance(ctrl, ft.DatePicker):
                    _selector_fecha_activo.append(ctrl)
                    break
        page.add(view.build())

    def mostrar_ciudades(username: str) -> None:
        _limpiar_pagina()
        view = CitiesView(
            page,
            username,
            on_go_home=lambda: mostrar_inicio(username),
        )
        page.add(view.build())

    def mostrar_alertas(username: str) -> None:
        _limpiar_pagina()
        view = AlertsView(
            page,
            username,
            on_go_home=lambda: mostrar_inicio(username),
        )
        page.add(view.build())

    # ── Inicio ────────────────────────────────────────────────────────────────
    mostrar_inicio_sesion()


if __name__ == "__main__":
    ft.app(target=main)
