import re

path = 'd:/san_doc/smart hospital/main_app.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def repl(match):
    name = match.group(1) # e.g. TEAL_600, RED, GREY_50
    return f'"{name.lower().replace("_", "")}"'

# Regex to match ft.colors.SOME_THING
new_content = re.sub(r'ft\.colors\.([A-Z0-9_]+)', repl, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed colors.")
