import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = ['/immigration', '/legal-affairs', '/technology']

with open('member_structure.txt', 'w', encoding='utf-8') as out:
    def log(*args, end='\n'):
        line = ' '.join(str(a) for a in args) + end
        print(line, end='')
        out.write(line)
    for path in PAGES:
        log('\n===', path, '===')
        r = requests.get(urljoin(BASE, path), timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.body
        for i, tag in enumerate(body.find_all(['h2','h3','h4','p','li','span','blockquote'], limit=140)):
            text = tag.get_text(separator=' ', strip=True)
            if not text:
                continue
            log(i, tag.name, repr(text[:200]))
