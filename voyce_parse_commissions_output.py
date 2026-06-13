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

with open('commissions_parse.txt', 'w', encoding='utf-8') as out:
    def log(*args, end='\n'):
        line = ' '.join(str(a) for a in args) + end
        print(line, end='')
        out.write(line)

    for path in PAGES:
        url = urljoin(BASE, path)
        log('\n===', path, '===')
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        log('title:', soup.title.string if soup.title else 'NO TITLE')
        sections = []
        for header in soup.find_all(['h1','h2','h3','h4','h5','h6']):
            text = header.get_text(strip=True)
            if text:
                sections.append((header.name, text))
        for name, text in sections[:40]:
            log(name, text)
        log('--- names ---')
        names = set()
        for tag in soup.find_all(['h2','h3','h4','p','span','li']):
            text = tag.get_text(strip=True)
            if text and len(text.split()) <= 7 and text[0].isupper() and any(c.isalpha() for c in text):
                if text.count(' ') >= 1 and not any(word in text for word in ['The', 'Commission', 'Meet', 'Join', 'Team', 'About', 'This', 'Our', 'Policy', 'Future', 'Platform', 'Aerospace', 'Climate', 'Energy', 'Finance', 'Foreign', 'Immigration', 'Legal', 'Technology', 'European', 'Identity', 'Welcome', 'Where', 'We']):
                    names.add(text)
        for name in sorted(names):
            log('NAME', name)
