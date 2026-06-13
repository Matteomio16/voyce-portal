import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
path = '/immigration'
url = urljoin(BASE, path)
r = requests.get(url, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, 'html.parser')
for h4 in soup.find_all('h4')[:40]:
    txt = h4.get_text(strip=True)
    if not txt:
        continue
    print('H4:', repr(txt[:120]))
    parents = []
    parent = h4
    for depth in range(6):
        if parent is None:
            break
        name = parent.name
        cls = parent.get('class')
        ids = parent.get('id')
        parents.append(f'{name} class={cls} id={ids}')
        parent = parent.parent
    print('  parents:', ' > '.join(parents))
    print()