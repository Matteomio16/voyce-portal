import re
import unicodedata
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd

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

BOARD_PATH = '/the-board'


def normalize_text(text: str) -> str:
    return unicodedata.normalize('NFC', str(text) or '').strip()


def is_person_name(text: str) -> bool:
    if not text:
        return False
    words = text.strip().split()
    if len(words) < 2 or len(words) > 7:
        return False
    text = normalize_text(text)
    if re.search(r"\b(this website uses cookies|meet the|our|what we do|commission|fellows|team|events|contact|home|blog)\b",
                 text, flags=re.I):
        return False
    return bool(re.match(r"^[A-ZÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+( [A-Za-zÀ-ÖØ-öø-ÿ'’\-]+){1,6}$", text))


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
    try:
        page.goto(url, timeout=120000, wait_until='domcontentloaded')
        try:
            page.wait_for_selector('h4', timeout=30000)
        except Exception:
            pass
        return page.content()
    except Exception as error:
        print(f'warning: failed to load {url}: {error}')
        raise


def fetch_pages() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for commission, path in PAGES:
            url = BASE + path
            html = fetch_content(page, url)
            for name, bio in extract_member_entries(html):
                results.append({'source': 'commission', 'commission': commission, 'name': name, 'bio': bio})
        board_html = fetch_content(page, BASE + BOARD_PATH)
        for name, bio in extract_member_entries(board_html):
            results.append({'source': 'board', 'commission': 'Board', 'name': name, 'bio': bio})
        browser.close()
    return results


def main() -> None:
    rows = fetch_pages()
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit('No rows extracted')
    unique = df.drop_duplicates(subset=['source', 'name', 'bio']).sort_values(['source', 'name'])
    unique.to_csv(Path('voyce_playwright_members.csv'), index=False)
    print('saved voyce_playwright_members.csv')
    print('rows extracted:', len(df))
    print('unique rows:', len(unique))
    print('commission rows:', (unique['source'] == 'commission').sum())
    print('board rows:', (unique['source'] == 'board').sum())


if __name__ == '__main__':
    main()
