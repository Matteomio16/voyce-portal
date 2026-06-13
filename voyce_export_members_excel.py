import re
import unicodedata
from pathlib import Path
from typing import Iterable
import fitz
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import difflib
from playwright.sync_api import sync_playwright

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


def normalize_text(text: str) -> str:
    return unicodedata.normalize('NFC', str(text) or '').strip()


def normalize_name(text: str) -> str:
    text = normalize_text(text).casefold()
    text = re.sub(r"['\u2019\u2018`]+", "'", text)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9'\- ]+", ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def canonical_name(text: str) -> str:
    return normalize_name(text)


def is_person_name(text: str) -> bool:
    if not text or len(text.split()) < 2 or len(text.split()) > 7:
        return False
    text = normalize_text(text)
    if re.search(r'\b(this website uses cookies|meet the|our|what we do|commission|fellows|team|events|contact|home|blog)\b', text, flags=re.I):
        return False
    return bool(re.match(r"^[A-Z\u00C0-\u024F][A-Za-z\u00C0-\u024F'\-]+( [A-Za-z\u00C0-\u024F'\-]+){1,6}$", text))


def extract_member_entries(html: str) -> Iterable[tuple[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    for h4 in soup.find_all('h4'):
        name = normalize_text(h4.get_text(' ', strip=True))
        if not is_person_name(name):
            continue
        bio = ''
        for sib in h4.next_siblings:
            if getattr(sib, 'name', None) == 'h4':
                break
            if getattr(sib, 'name', None) in {'p', 'div', 'span'}:
                candidate = normalize_text(sib.get_text(' ', strip=True))
                if len(candidate) > 40:
                    bio = candidate
                    break
        yield name, bio


def fetch_content(page, url: str) -> str:
    page.goto(url, timeout=120000, wait_until='domcontentloaded')
    try:
        page.wait_for_selector('h4', timeout=30000)
    except Exception:
        pass
    return page.content()


def fetch_all_members() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # roles from existing CSV
        role_map: dict[str, str] = {}
        try:
            df_csv = pd.read_csv('voyce_commission_members.csv')
            df_csv = df_csv.drop_duplicates(subset=['commission', 'role', 'name'])
            for _, r in df_csv.iterrows():
                key = canonical_name(r['name'])
                role_map[key] = r['role']
        except Exception:
            pass

        for commission, path in PAGES:
            url = urljoin(BASE, path)
            html = fetch_content(page, url)
            for name, bio in extract_member_entries(html):
                results.append({
                    'source': 'commission',
                    'commission': commission,
                    'name': name,
                    'bio': bio,
                    'role': role_map.get(canonical_name(name), 'Fellow'),
                })

        board_html = fetch_content(page, urljoin(BASE, '/the-board'))
        for name, bio in extract_member_entries(board_html):
            results.append({
                'source': 'board',
                'commission': 'Board',
                'name': name,
                'bio': bio,
                'role': '',
            })

        browser.close()
    return results


def clean_author_list(text: str) -> list[str]:
    text = normalize_text(text)
    text = re.sub(r'^(by\s+)', '', text, flags=re.I)
    text = text.replace(' & ', ', ').replace(' and ', ', ')
    parts = [part.strip() for part in re.split(r'[;,/]+', text) if part.strip()]
    return [normalize_text(part) for part in parts]


def match_author(author: str, name_map: dict[str, str]) -> str | None:
    lookup = normalize_name(author)
    if lookup in name_map:
        return name_map[lookup]
    close = difflib.get_close_matches(lookup, list(name_map.keys()), n=1, cutoff=0.78)
    if close:
        return name_map[close[0]]
    return None


def parse_article_authors(all_names: list[str]) -> dict[str, set[str]]:
    author_articles: dict[str, set[str]] = {}
    name_map = {canonical_name(name): name for name in all_names}

    resp = requests.get(urljoin(BASE, '/home/f.json'), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for item in data.get('items', []):
        title = normalize_text(item.get('title', ''))
        html_content = item.get('html_content', '')

        raw = None
        m = re.search(r'<p[^>]*>(By|by)\s+(.*?)(?:</p>|\n|$)', html_content, re.DOTALL)
        if m:
            raw = m.group(2).strip()

        if not raw:
            summary = item.get('summary', '')
            sum_m = re.match(r'(?:By|by)\s+(.+)', summary)
            if sum_m:
                raw = sum_m.group(1).split('\n')[0].strip()

        if not raw:
            continue

        raw = re.sub(r'\s+', ' ', raw)
        parts = re.split(r'\s*[,;]\s*|\s+and\s+|\s*&\s*', raw)
        for author in parts:
            author = author.strip()
            if not author or len(author.split()) < 2:
                continue
            member = match_author(author, name_map)
            if member:
                author_articles.setdefault(canonical_name(member), set()).add(title)
    return author_articles


def get_org_chart_names(pdf_path: str | Path) -> list[str]:
    with fitz.open(str(pdf_path)) as doc:
        text = ''.join(page.get_text() for page in doc)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = []
    skip_roles = {'Head', 'Commissioner', 'Deputy', 'Team', 'Officer', 'Director',
                  'Chief', 'Secretary', 'Partner', 'Counsel', 'General'}
    for line in lines:
        if len(line) > 120:
            continue
        if re.search(r'\b(' + '|'.join(skip_roles) + r')\b', line):
            continue
        words = line.split()
        if 2 <= len(words) <= 6 and all(
            re.match(r"^[A-Z\u00C0-\u017F][a-z\u00E0-\u017F'\-]*$", w) for w in words if w
        ):
            candidates.append(line)
    exclude = {
        'President', 'Board', 'General Counsel', 'Video Creation Team',
        'Head of Website Technology', 'Head of Finance & Accounting',
        'Capital Markets Union', 'Climate Change', 'Economic Affairs',
        'Energy Fellows', 'Foreign Policy', 'Legal Affairs', 'Vice President'
    }
    return sorted(set(n for n in candidates if n not in exclude))


def extract_profile_field(bio: str, patterns: list[str]) -> str:
    """Extract a field from bio text (origin, university, interest, etc.)"""
    if not bio:
        return ''
    text = bio
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ''


def extract_where_from(bio: str) -> str:
    patterns = [
        (r'\b(?:from|based in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 1),
        (r'\b(?:is an?\s+)(Italian|French|German|Spanish|Portuguese|Dutch|Belgian|Austrian|Swiss|British|American|Canadian|Indian|Chinese|Japanese|Korean|Greek|Polish|Swedish|Norwegian|Danish|Finnish|Irish|Croatian|Serbian|Romanian|Bulgarian|Czech|Hungarian|Slovak|Slovenian|Estonian|Latvian|Lithuanian|Maltese|Luxembourgish|French-Italian|Italian-Canadian)\s+', 1),
    ]
    for pat, group in patterns:
        m = re.search(pat, bio, re.IGNORECASE)
        if m:
            return m.group(group).strip()
    # direct check for nationality adjectives
    nationalities = [
        'Italian', 'French', 'German', 'Spanish', 'Portuguese', 'Dutch', 'Belgian',
        'Austrian', 'Swiss', 'British', 'American', 'Canadian', 'Indian', 'Chinese',
        'Japanese', 'Korean', 'Greek', 'Polish', 'Swedish', 'Norwegian', 'Danish',
        'Finnish', 'Irish', 'Croatian', 'Serbian', 'Romanian', 'Bulgarian', 'Czech',
        'Hungarian', 'Slovak', 'Slovenian', 'Estonian', 'Latvian', 'Lithuanian',
        'Maltese', 'Luxembourgish', 'French-Italian', 'Italian-Canadian',
    ]
    for nat in nationalities:
        if nat.lower() in bio.lower():
            return nat
    return ''


def extract_uni(bio: str) -> str:
    patterns = [
        r'(?:pursuing|studying|studies in|degree in|Bachelor|Master|PhD|BSc|MSc|BA|MA)\s+(?:.*?)\s+(?:at|from)\s+([A-Z][A-Za-z\s]+(?:University|College|Institute|School|Politecnico))',
        r'\b(?:student at|alumnus of|alumna of|graduate of)\s+([A-Z][A-Za-z\s]+(?:University|College|Institute|School|Politecnico))',
        r'(?:at|from)\s+([A-Z][A-Za-z\s]+(?:University|College|Institute|School|Politecnico))',
    ]
    for pat in patterns:
        m = re.search(pat, bio, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ''


def extract_interests(bio: str) -> str:
    patterns = [
        r'(?:interested in|passionate about|passionated about|focus(?:es)? on)\s+([^.!?]+(?:\.))',
        r'(?:main interest|particular interest|strong interest)\s+(?:lies in|is)\s+([^.!?]+(?:\.))',
    ]
    interests = []
    for pat in patterns:
        for m in re.finditer(pat, bio, re.IGNORECASE):
            interests.append(m.group(1).strip())
    return '; '.join(interests) if interests else ''


def main() -> None:
    # 1) Fetch all members via Playwright (browser-rendered data)
    print('Fetching members via Playwright...')
    members = fetch_all_members()
    df = pd.DataFrame(members)
    if df.empty:
        raise SystemExit('No members fetched')

    # Deduplicate: keep first occurrence per (commission, name)
    df = df.drop_duplicates(subset=['commission', 'name']).sort_values(['commission', 'name']).reset_index(drop=True)

    # 2) Parse articles from the blog feed
    all_names: list[str] = list(df['name'].dropna().astype(str).unique())
    org_names = get_org_chart_names(Path('VOYCE Organisational Structure.pdf'))
    author_articles = parse_article_authors(all_names + org_names)

    df['article_titles'] = df['name'].apply(
        lambda n: '; '.join(sorted(author_articles.get(canonical_name(n), [])))
    ).fillna('')

    # 3) Extract profile fields from bios
    df['where_from'] = df['bio'].apply(lambda b: extract_where_from(str(b)))
    df['uni'] = df['bio'].apply(lambda b: extract_uni(str(b)))
    df['interests'] = df['bio'].apply(lambda b: extract_interests(str(b)))

    # 4) Fill empty bios with fallback commission description
    commission_desc: dict[str, str] = {}
    for commission, path in PAGES:
        url = urljoin(BASE, path)
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            headers = [h.get_text(' ', strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4'])]
            desc = ''
            for text in headers:
                if len(text) > 60 and 'meet the' not in text.lower() and 'commission' in text.lower():
                    desc = text
                    break
            if not desc:
                for text in headers:
                    if len(text) > 40 and 'meet the' not in text.lower():
                        desc = text
                        break
            commission_desc[commission] = desc
        except Exception:
            commission_desc[commission] = ''

    for idx, row in df.iterrows():
        if not str(row.get('bio', '')).strip() or len(str(row.get('bio', '')).strip()) < 50:
            desc = commission_desc.get(row['commission'], '')
            if desc:
                df.at[idx, 'bio'] = f"Member of the {row['commission']} Commission. {desc}"
            else:
                df.at[idx, 'bio'] = f"Member of the {row['commission']} Commission."

    # 5) Export
    csv_path = Path('voyce_members_complete.csv')
    df.to_csv(csv_path, index=False)

    excel_path = Path('voyce_members.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='AllMembers')
        df_org = pd.DataFrame({'name': org_names, 'source': 'org-chart'})
        df_org.to_excel(writer, index=False, sheet_name='OrgChartMembers')

    # Summary
    real_bios = df['bio'].apply(lambda b: len(str(b)) > 80).sum()
    blank_articles = (df['article_titles'].astype(str).str.strip() == '').sum()
    blank_where = (df['where_from'].astype(str).str.strip() == '').sum()
    blank_uni = (df['uni'].astype(str).str.strip() == '').sum()
    blank_interests = (df['interests'].astype(str).str.strip() == '').sum()

    print()
    print('saved', csv_path)
    print('saved', excel_path)
    print('total members:', len(df))
    print('members with real bios (>80 chars):', real_bios)
    print('members with articles:', len(df) - blank_articles)
    print('where_from blank:', blank_where)
    print('uni blank:', blank_uni)
    print('interests blank:', blank_interests)
    print('columns:', list(df.columns))
    print('both blank:', ((df_comm['bio'].astype(str).str.strip() == '') & (df_comm['article_titles'].astype(str).str.strip() == '')).sum())


if __name__ == '__main__':
    main()
