import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = ['/immigration', '/legal-affairs', '/technology']

for path in PAGES:
    print('\n===', path, '===')
    r = requests.get(urljoin(BASE, path), timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # find the main content area if possible
    body = soup.body
    for i, tag in enumerate(body.find_all(['h2','h3','h4','p','li','span','blockquote'], limit=120)):
        text = tag.get_text(separator=' ', strip=True)
        if not text:
            continue
        if i < 120:
            print(i, tag.name, repr(text[:200]))
