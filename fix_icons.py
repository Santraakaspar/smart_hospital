import re

path = 'd:/san_doc/smart hospital/main_app.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def repl(match):
    name = match.group(1) # e.g. PERSON, LOCAL_HOSPITAL
    return f'"{name.lower()}"'

# Regex to match ft.icons.SOME_THING
# We need to be careful not to match things that aren't icons if strict, but ft.icons.XXX is pretty specific.
new_content = re.sub(r'ft\.icons\.([A-Z0-9_]+)', repl, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed icons.")
