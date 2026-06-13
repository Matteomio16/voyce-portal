import requests
from bs4 import BeautifulSoup

BASE = 'https://voycecommunity.eu'

def fetch(path):
    url = BASE + path
    print('FETCH', url)
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

html = fetch('/our-teams')
soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
    text = tag.get_text(strip=True)
    if not text:
        continue
    if any(k in text.lower() for k in ['commission', 'team', 'head of', 'director', 'officer', 'editor', 'member', 'fellow', 'commander', 'contact', 'our team']):
        print(tag.name, text)

print('---')
feed = requests.get(BASE + '/home/f.json', timeout=20).json()
print('feed entries', len(feed.get('items', [])))
for item in feed.get('items', [])[:20]:
    print(item.get('title'))
    print('  author', item.get('author'))
    print('  categories', item.get('categories'))
    print('  link', item.get('link'))
    print('---')
