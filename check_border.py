import flet as ft
print("Flet imported")
try:
    print(ft.border.BorderSide(5, "red"))
except Exception as e:
    print(e)

print(hasattr(ft.Container, "border_left"))
print(hasattr(ft.Container, "border"))
print(ft.Border(left=ft.BorderSide(5, "red")))
