import flet as ft
try:
    b = ft.FilledButton(text="Test", style=ft.ButtonStyle(bgcolor="red"))
    print("FilledButton init success")
except Exception as e:
    print(f"FilledButton init failed: {e}")
