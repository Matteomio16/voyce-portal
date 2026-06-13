import easyocr
from pathlib import Path
reader = easyocr.Reader(['en'], gpu=False)
img = Path('Screenshot 2026-06-11 155728.png')
results = reader.readtext(str(img), detail=0)
print('blocks', len(results))
for i, r in enumerate([x for x in results if x.strip()][:50], 1):
    print(f'{i:02d}', r)
