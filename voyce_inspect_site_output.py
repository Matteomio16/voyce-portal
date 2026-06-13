import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://voycecommunity.eu'
PAGES = [
    '/our-teams',
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
    '/our-work-1',
    '/home',
    '/join-us',
    '/where-we-are-from',
]

with open('site_inspect_results.txt', 'w', encoding='utf-8') as out:
    def log(*args, **kwargs):
        print(*args, **kwargs)
        out.write(' '.join(str(a) for a in args) + (kwargs.get('end','\n')))
    for path in PAGES:
        url = urljoin(BASE, path)
        log('\n=== PAGE', path, '===')
        r = requests.get(url, timeout=30)
        log('status', r.status_code, 'len', len(r.text))
        text = r.text
        if 'Team' in text or 'Commissioner' in text or 'Fellow' in text or 'Head of' in text or 'Officer' in text or 'Secretary General' in text:
            log('contains team terms')
        if 'Carlo Casabona' in text:
            log('contains Carlo Casabona')
        for keyword in ['Head of', 'Commissioner', 'Fellow', 'Editor', 'Chief', 'Officer', 'Secretary General', 'Deputy', 'Partner', 'Member']:
            if keyword in text:
                log('  keyword:', keyword)
        # print title if exists
        soup = BeautifulSoup(text, 'html.parser')
        title = soup.title.string.strip() if soup.title else 'NO TITLE'
        log('title:', title)
        headers = [h.get_text(strip=True) for h in soup.find_all(['h1','h2','h3','h4'])]
        log('headers sample:', headers[:10])

    log('\n=== checking article items ===')
    resp = requests.get(BASE + '/home/f.json', timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for item in data.get('items', [])[:10]:
        title = item.get('title')
        link = item.get('link') or item.get('link')
        log('\n-- article', title)
        if not link:
            log('  no link')
            continue
        r = requests.get(link, timeout=30)
        log('  status', r.status_code, 'len', len(r.text))
        soup = BeautifulSoup(r.text, 'html.parser')
        log('  title meta:', soup.title.string if soup.title else 'NONE')
        for meta_name in ['author', 'description', 'keywords']:
            meta = soup.find('meta', attrs={'name': meta_name})
            if meta:
                log('  meta', meta_name, meta.get('content'))
        for sel in ['.post-author', '.author', 'a[href*="author"]', '.blog-author']:
            found = soup.select(sel)
            if found:
                log('  selector', sel, 'matches', len(found))
                for f in found[:3]:
                    log('   ', f.get_text(strip=True)[:150])
        text = soup.get_text(separator=' ', strip=True)
        if 'By' in text[:300] or 'by ' in text[:300].lower():
            log('  preview', text[:300])
