import re

# Read the HTML file
with open(r'g:\HIT400 PROJECTS\Elizabeth\supplyinsights\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all variations of relative paths to assets
# Pattern: src="../../../assets/..." or href="../../../assets/..."
content = re.sub(r'(src|href)="\.\.(/\.\.)*(/assets/[^"]+)"', r'\1="{% static \'\3\' %}"', content)

# Write back to file
with open(r'g:\HIT400 PROJECTS\Elizabeth\supplyinsights\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated all static file references!")
