import flet as ft
import inspect

try:
    print("Tab init signature:", inspect.signature(ft.Tab.__init__))
except Exception as e:
    print("Error inspecting Tab:", e)
