import flet as ft
import inspect

print("Tabs init signature:", inspect.signature(ft.Tabs.__init__))
try:
    # Try positional
    t = ft.Tabs([ft.Tab(label="Test")])
    print("Accepted positional tabs")
except Exception as e:
    print("Positional failed:", e)

try:
    # Try controls
    t = ft.Tabs(controls=[ft.Tab(label="Test")])
    print("Accepted 'controls' kwarg")
except Exception as e:
    print("Controls kwarg failed:", e)
