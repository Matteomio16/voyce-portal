import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = [
    '/aerospace-%26-defence',
    '/climate-change',
    '/economic-affairs',
    '/energy',
    '/european-identity',
    '/finance-%26-capital-markets',
    '/foreign-policy',
    '/immigration',
    '/legal-affairs',
    '/technology',
]

for path in PAGES:
    url = urljoin(BASE, path)
    print('\n===', path, '===')
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    print('title:', soup.title.string if soup.title else 'NO TITLE')
    sections = []
    for header in soup.find_all(['h1','h2','h3','h4','h5','h6']):
        text = header.get_text(strip=True)
        if text:
            sections.append((header.name, text))
    for name, text in sections[:40]:
        print(name, text)
    print('--- names ---')
    names = set()
    for tag in soup.find_all(['h2','h3','h4','p','span','li']):
        text = tag.get_text(strip=True)
        # filter by likely personal names: contain space and uppercase first letters
        if text and len(text.split()) <= 5 and text[0].isupper() and any(c.isalpha() for c in text):
            if text.count(' ') >= 1 and not any(word in text for word in ['The', 'Commission', 'Meet', 'Join', 'Team', 'About', 'This', 'Our', 'Policy', 'Future', 'Platform']):
                if text not in ['Aerospace & Defence', 'The Aerospace & Defence Commission', 'This website uses cookies.']:
                    names.add(text)
    for name in sorted(names):
        if any(word in name for word in ['Commission', 'Team', 'The', 'This', 'Our', 'Where', 'Welcome']):
            continue
        print('NAME', name)
