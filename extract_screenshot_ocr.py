import json
import easyocr
from pathlib import Path
reader = easyocr.Reader(['en'], gpu=False)
imgs = sorted(Path('.').glob('Screenshot *.png'))
results = []
for img in imgs:
    blocks = reader.readtext(str(img), detail=0)
    results.append({'image': img.name, 'blocks': [b for b in blocks if b.strip()]})
with open('screenshot_ocr_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('saved screenshot_ocr_results.json with', len(results), 'images')
