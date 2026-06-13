import requests
from bs4 import BeautifulSoup
BASE = 'https://voycecommunity.eu'
url = BASE + '/our-teams'
print('FETCH', url)
r = requests.get(url, timeout=20)
r.raise_for_status()
html = r.text
print('len html', len(html))
for word in ['Head of', 'Commissioner', 'Editor', 'Head of Community', 'Fellow', 'Member', 'Staff', 'Head of Operations', 'Head of Events', 'Head of Partnerships', 'Secretary General']:
    if word in html:
        print('FOUND', word)

soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4']):
    text = tag.get_text(separator=' ', strip=True)
    if text and any(x in text for x in ['Head of', 'Commissioner', 'Fellow', 'Editor', 'Head of', 'Deputy', 'Secretary General', 'Chief Press Officer']):
        print(tag.name, text[:300])
