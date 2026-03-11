from telegram.ext import filters
print(f"TEXT: {hasattr(filters, 'TEXT')}")
print(f"COMMAND: {hasattr(filters, 'COMMAND')}")
print(f"LOCATION: {hasattr(filters, 'LOCATION')}")
print(f"STICKER: {hasattr(filters, 'STICKER')}")
print(f"Sticker: {hasattr(filters, 'Sticker')}")
if hasattr(filters, 'Sticker'):
    print(f"Sticker.ALL: {hasattr(filters.Sticker, 'ALL')}")
