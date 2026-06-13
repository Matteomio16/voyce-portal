import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = ['/immigration', '/legal-affairs', '/technology']

for path in PAGES:
    url = urljoin(BASE, path)
    print('\n===', path, '===')
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    main = soup.find('main') or soup.body
    if main is None:
        main = soup
    h1 = main.find('h1')
    print('h1:', h1.get_text(strip=True) if h1 else 'NO H1')
    current = h1
    for i in range(1, 60):
        if current is None:
            break
        current = current.find_next_sibling()
        if current is None:
            break
        txt = current.get_text(separator=' ', strip=True)
        print(i, current.name, repr(txt[:180]))
        if 'This website uses cookies' in txt:
            break
