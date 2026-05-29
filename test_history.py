import sys
import flet as ft
from views.history_view import HistoryView
import utils.settings as settings

settings.set_temp_unit("F")

class FakePage:
    def update(self): pass
    overlay = []

hv = HistoryView(FakePage(), "Valen", lambda: None)
hv._city_dropdown.value = "Tokio"
hv._load_data("Tokio")
