import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
path = '/immigration'
url = urljoin(BASE, path)
r = requests.get(url, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, 'html.parser')
with open('h4_parents.txt', 'w', encoding='utf-8') as out:
    def log(*args, end='\n'):
        line = ' '.join(str(a) for a in args) + end
        print(line, end='')
        out.write(line)
    for h4 in soup.find_all('h4')[:40]:
        txt = h4.get_text(strip=True)
        if not txt:
            continue
        log('H4:', repr(txt[:120]))
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
        log('  parents:', ' > '.join(parents))
        log()