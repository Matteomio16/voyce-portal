import easyocr
from pathlib import Path
reader = easyocr.Reader(['en'], gpu=False)
imgs = sorted(Path('.').glob('Screenshot *.png'))[:3]
print('images', len(imgs))
for img in imgs:
    print('---', img.name)
    results = reader.readtext(str(img), detail=0)
    print('blocks', len(results))
    sample = [r for r in results if r.strip()]
    for i, r in enumerate(sample[:40], 1):
        print(f'{i:02d}', r)
    print()
