import flet as ft

print("Tabs module:", ft.Tabs.__module__)
print("Tabs dir:", dir(ft.Tabs))

try:
    t = ft.Tabs()
    print("Init empty success")
except Exception as e:
    print("Init empty failed:", e)

try:
    t = ft.Tabs(selected_index=0)
    t.tabs = [ft.Tab(label="A"), ft.Tab(label="B")]
    print("Assigned tabs property success")
except Exception as e:
    print("Assigned tabs property failed:", e)
