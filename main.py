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
    _active_date_picker: list[ft.DatePicker] = []

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clear_page() -> None:
        """Limpia controles y el overlay del DatePicker si hay uno activo."""
        if _active_date_picker:
            dp = _active_date_picker.pop()
            try:
                page.overlay.remove(dp)
            except ValueError:
                pass
        page.controls.clear()

    # ── Vistas ────────────────────────────────────────────────────────────────

    def show_login() -> None:
        _clear_page()
        view = LoginView(page, on_login_success=show_home)
        page.add(view.build())

    def show_home(username: str) -> None:
        _clear_page()
        view = HomeView(
            page,
            username,
            on_go_history=lambda: show_history(username),
            on_go_cities=lambda: show_cities(username),
            on_go_alerts=lambda: show_alerts(username),
            on_logout=show_login,
        )
        page.add(view.build())

    def show_history(username: str) -> None:
        _clear_page()
        view = HistoryView(
            page,
            username,
            on_go_home=lambda: show_home(username),
        )
        # HistoryView agrega su DatePicker al overlay en __init__;
        # lo registramos para poder limpiarlo al navegar.
        if page.overlay:
            for ctrl in reversed(page.overlay):
                if isinstance(ctrl, ft.DatePicker):
                    _active_date_picker.append(ctrl)
                    break
        page.add(view.build())

    def show_cities(username: str) -> None:
        _clear_page()
        view = CitiesView(
            page,
            username,
            on_go_home=lambda: show_home(username),
        )
        page.add(view.build())

    def show_alerts(username: str) -> None:
        _clear_page()
        view = AlertsView(
            page,
            username,
            on_go_home=lambda: show_home(username),
        )
        page.add(view.build())

    # ── Inicio ────────────────────────────────────────────────────────────────
    show_login()


if __name__ == "__main__":
    ft.app(target=main)
