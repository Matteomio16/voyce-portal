import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE = 'https://voycecommunity.eu'
START = 'https://voycecommunity.eu/home'

resp = requests.get(START, timeout=20)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, 'html.parser')
print('title:', soup.title.string if soup.title else 'NO TITLE')

links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if not href:
        continue
    if href.startswith('#'):
        continue
    full = urljoin(BASE, href)
    parsed = urlparse(full)
    if parsed.netloc != urlparse(BASE).netloc:
        continue
    if full not in links:
        links.append(full)

print('total internal links:', len(links))
for i, link in enumerate(sorted(links)):
    print(i+1, link)

print('--- sample page text ---')
print(resp.text[:2000])
