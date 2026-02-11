import flet as ft
import inspect

print("Dir Tab:", dir(ft.Tab))
print("Tab init sig:", inspect.signature(ft.Tab.__init__))
try:
    t = ft.Tab(label="Test")
    print("Tab instance content attr:", hasattr(t, 'content'))
    t.content = ft.Text("Content")
    print("Assigned content successfully")
except Exception as e:
    print("Error experimenting with Tab:", e)
