import re

# Read the HTML file
with open(r'g:\HIT400 PROJECTS\Elizabeth\supplyinsights\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the escaped quotes - replace \' with just '
content = content.replace("\\'", "'")

# Write back to file
with open(r'g:\HIT400 PROJECTS\Elizabeth\supplyinsights\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully fixed escaped quotes in static file references!")
