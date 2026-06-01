import sys
import flet as ft
from views.history_view import HistoryView
import utils.settings as settings

settings.establecer_unidad_temperatura("F")

class FakePage:
    def update(self): pass
    overlay = []

hv = HistoryView(FakePage(), "Valen", lambda: None)
hv._lista_ciudades.value = "Tokio"
hv._cargar_datos_historial("Tokio")
