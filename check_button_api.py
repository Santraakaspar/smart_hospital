import flet as ft
try:
    b = ft.Button(text="Test", bgcolor="red", color="white")
    print("Button init success")
except Exception as e:
    print(f"Button init failed: {e}")
