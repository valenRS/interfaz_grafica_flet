# Valentina Rodriguez Sepulveda — 1125789977
# views/login_view.py — Ventana de inicio de sesión y registro
# MeteoApp — Dashboard Meteorológico Personal

from __future__ import annotations

import hashlib
from typing import Callable

import flet as ft

from utils.data_manager import crear_usuario, obtener_usuario

# ── Helpers ───────────────────────────────────────────────────────────────────


def _codificar_contraseña(password: str) -> str:
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

        self._modo_radio = ft.RadioGroup(
            value="login",
            on_change=self._al_cambiar_modo,
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

        self._campo_usuario = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            **_field_style,
        )

        self._campo_contraseña = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            **_field_style,
        )

        self._mensaje_estado = ft.Text(
            value="",
            size=13,
            text_align=ft.TextAlign.CENTER,
            width=320,
        )

        self._boton_accion = ft.ElevatedButton(
            text="Ingresar",
            on_click=self._al_enviar_formulario,
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

    def _al_cambiar_modo(self, e: ft.ControlEvent) -> None:
        self._boton_accion.text = "Ingresar" if self._modo_radio.value == "login" else "Crear cuenta"
        self._mensaje_estado.value = ""
        self.page.update()

    def _al_enviar_formulario(self, e: ft.ControlEvent) -> None:
        username = self._campo_usuario.value.strip()
        password = self._campo_contraseña.value

        if not username or not password:
            self._mostrar_mensaje("Por favor completa todos los campos.", error=True)
            return
        if len(password) < 4:
            self._mostrar_mensaje("La contraseña debe tener al menos 4 caracteres.", error=True)
            return

        pwd_hash = _codificar_contraseña(password)

        if self._modo_radio.value == "login":
            user = obtener_usuario(username)
            if user is None:
                self._mostrar_mensaje("Usuario no encontrado.", error=True)
                return
            if user["password_hash"] != pwd_hash:
                self._mostrar_mensaje("Contraseña incorrecta.", error=True)
                return
            self.on_login_success(username)

        else:
            if not crear_usuario(username, pwd_hash):
                self._mostrar_mensaje("El nombre de usuario ya existe.", error=True)
                return
            self._mostrar_mensaje("¡Cuenta creada! Ahora puedes iniciar sesión.", error=False)
            self._modo_radio.value = "login"
            self._boton_accion.text = "Ingresar"
            self._campo_contraseña.value = ""
            self.page.update()

    def _mostrar_mensaje(self, text: str, *, error: bool) -> None:
        self._mensaje_estado.value = text
        self._mensaje_estado.color = "#EF9A9A" if error else "#A5D6A7"
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
                                self._modo_radio,
                                # ── Campos de texto ────────────────────────
                                self._campo_usuario,
                                self._campo_contraseña,
                                # ── Mensaje de estado ──────────────────────
                                self._mensaje_estado,
                                # ── Botón de acción ────────────────────────
                                self._boton_accion,
                            ],
                        ),
                    ),
                ],
            ),
        )
