import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = [
    ('Aerospace & Defence', '/aerospace-%26-defence'),
    ('Climate Change', '/climate-change'),
    ('Economic Affairs', '/economic-affairs'),
    ('Energy', '/energy'),
    ('European Identity', '/european-identity'),
    ('Finance & Capital Markets', '/finance-%26-capital-markets'),
    ('Foreign Policy', '/foreign-policy'),
    ('Immigration', '/immigration'),
    ('Legal Affairs', '/legal-affairs'),
    ('Technology', '/technology'),
]

rows = []

for commission_name, path in PAGES:
    url = urljoin(BASE, path)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    state = None
    for tag in soup.find_all(['h2', 'h3', 'h4']):
        text = tag.get_text(separator=' ', strip=True)
        if not text:
            continue
        low = text.lower()
        if 'meet the commissioner' in low or 'meet the commissioner:' in low or 'meet the commissioner' in low:
            state = 'Commissioner'
            continue
        if 'meet the fellows' in low or 'meet the team' in low or 'meet the team:' in low:
            state = 'Fellow'
            continue
        if text.startswith('Meet ') or text.startswith('The '):
            continue
        if tag.name == 'h4' and state is not None:
            if len(text.split()) >= 2 and all(word[0].isupper() or word[0] in "'ÀÂÄÇÉÈÊËÎÏÔŒÙÛÜŸáàâäãçéèêëíìîïóòôöõúùûüñýÿ" for word in text.split()):
                rows.append({
                    'commission': commission_name,
                    'role': state,
                    'name': text,
                    'source': 'website',
                })

with open('voyce_commission_members.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['commission', 'role', 'name', 'source'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print('wrote', len(rows), 'rows')
