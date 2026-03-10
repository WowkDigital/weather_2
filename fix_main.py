import re

with open('main.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Wykres odczuwalnej\"" in line or "Wykres odczuwalnej\"," in line:
        lines[i] = "        InlineKeyboardButton(\"📈 Wykres odczuwalnej\", callback_data=f\"chart_{city}\"),\n"
    elif "Odśwież\"" in line or "Odśwież\"," in line:
        lines[i] = "        InlineKeyboardButton(\"🔄 Odśwież\", callback_data=f\"refresh_{city}\")\n"

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
