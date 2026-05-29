# Valentina Rodriguez Sepulveda — 1125789977
# views/login_view.py — Ventana de inicio de sesión y registro
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import hashlib
from typing import Callable

import flet as ft

from utils.data_manager import create_user, get_user

# ── Helpers ───────────────────────────────────────────────────────────────────


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Vista ─────────────────────────────────────────────────────────────────────


class LoginView:
    """
    Primera ventana de la app. Permite iniciar sesión o registrar una cuenta
    nueva. Al autenticarse correctamente, invoca `on_login_success(username)`.
    """

    def __init__(self, page: ft.Page, on_login_success: Callable[[str], None]) -> None:
        self.page = page
        self.on_login_success = on_login_success

        # ── Controles ─────────────────────────────────────────────────────────

        self._mode = ft.RadioGroup(
            value="login",
            on_change=self._on_mode_change,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=28,
                controls=[
                    ft.Radio(value="login",    label="Iniciar sesión",
                             label_style=ft.TextStyle(color="#FFFFFF", size=14)),
                    ft.Radio(value="registro", label="Registrarse",
                             label_style=ft.TextStyle(color="#FFFFFF", size=14)),
                ],
            ),
        )

        _field_style = dict(
            border_color="#42A5F5",
            focused_border_color="#FFFFFF",
            label_style=ft.TextStyle(color="#90CAF9"),
            color="#FFFFFF",
            cursor_color="#FFFFFF",
            bgcolor="#1976D2",
            border_radius=8,
            width=320,
        )

        self._username = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            **_field_style,
        )

        self._password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            **_field_style,
        )

        self._message = ft.Text(
            value="",
            size=13,
            text_align=ft.TextAlign.CENTER,
            width=320,
        )

        self._btn = ft.ElevatedButton(
            text="Ingresar",
            on_click=self._on_submit,
            width=320,
            height=46,
            style=ft.ButtonStyle(
                bgcolor="#29B6F6",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=4,
            ),
        )

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_mode_change(self, e: ft.ControlEvent) -> None:
        self._btn.text = "Ingresar" if self._mode.value == "login" else "Crear cuenta"
        self._message.value = ""
        self.page.update()

    def _on_submit(self, e: ft.ControlEvent) -> None:
        username = self._username.value.strip()
        password = self._password.value

        if not username or not password:
            self._show_message("Por favor completa todos los campos.", error=True)
            return
        if len(password) < 4:
            self._show_message("La contraseña debe tener al menos 4 caracteres.", error=True)
            return

        pwd_hash = _hash_password(password)

        if self._mode.value == "login":
            user = get_user(username)
            if user is None:
                self._show_message("Usuario no encontrado.", error=True)
                return
            if user["password_hash"] != pwd_hash:
                self._show_message("Contraseña incorrecta.", error=True)
                return
            self.on_login_success(username)

        else:
            if not create_user(username, pwd_hash):
                self._show_message("El nombre de usuario ya existe.", error=True)
                return
            self._show_message("¡Cuenta creada! Ahora puedes iniciar sesión.", error=False)
            self._mode.value = "login"
            self._btn.text = "Ingresar"
            self._password.value = ""
            self.page.update()

    def _show_message(self, text: str, *, error: bool) -> None:
        self._message.value = text
        self._message.color = "#EF9A9A" if error else "#A5D6A7"
        self.page.update()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor="#1565C0",
            alignment=ft.alignment.center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        bgcolor="#0D47A1",
                        border_radius=16,
                        padding=ft.padding.symmetric(horizontal=44, vertical=40),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=28,
                            color="#44000000",
                            offset=ft.Offset(0, 8),
                        ),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                            controls=[
                                # ── Logo + título ──────────────────────────
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.CLOUD, color="#29B6F6", size=42),
                                        ft.Text(
                                            "MeteoApp",
                                            size=32,
                                            weight=ft.FontWeight.BOLD,
                                            color="#FFFFFF",
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    "Dashboard Meteorológico Personal",
                                    size=13,
                                    color="#90CAF9",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Divider(color="#1565C0", height=4),
                                # ── Radio buttons ──────────────────────────
                                self._mode,
                                # ── Campos de texto ────────────────────────
                                self._username,
                                self._password,
                                # ── Mensaje de estado ──────────────────────
                                self._message,
                                # ── Botón de acción ────────────────────────
                                self._btn,
                            ],
                        ),
                    ),
                ],
            ),
        )
