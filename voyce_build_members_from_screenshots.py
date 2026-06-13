import csv
import difflib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import requests

def normalize_text(text: str) -> str:
    return unicodedata.normalize('NFC', str(text) or '').strip()


def canonical_name(name: str) -> str:
    name = normalize_text(name)
    name = name.replace('  ', ' ')
    name = re.sub(r"['‘’`]+", "'", name)
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(ch for ch in name if not unicodedata.combining(ch))
    name = re.sub(r'[^A-Za-z0-9\'\- ]+', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip().casefold()
    return name


def extract_bio_from_name_line(line: str, name: str) -> str:
    text = normalize_text(line)
    if text == name:
        return ''
    if text.lower().startswith(name.lower()):
        remainder = text[len(name):].strip()
        return remainder.strip(' ,:-–—()')
    regex = re.compile(re.escape(name) + r"(?:\s+is|\s*,|\s+–|\s+—|\s+-|\s+\(|\s+was|\s+has|\s+with|\s+and)\s*(.+)", flags=re.I)
    m = regex.search(text)
    if m:
        return m.group(1).strip(' ,:-–—()')
    return ''


def line_is_name_candidate(block: str, known_items: list[tuple[str, dict[str, str]]]) -> bool:
    bnorm = canonical_name(block)
    return any(know_norm in bnorm for know_norm, _ in known_items)


def parse_profiles_from_blocks(blocks: list[str], known_name_norms: dict[str, str]) -> list[dict[str, str]]:
    normalized = [normalize_text(b) for b in blocks]
    known_items = sorted(known_name_norms.items(), key=lambda item: -len(item[0]))
    candidates: list[tuple[int, str, str]] = []
    for idx, block in enumerate(normalized):
        if not block:
            continue
        bnorm = canonical_name(block)
        for know_norm, know_info in known_items:
            know_name = know_info['name']
            if know_norm in bnorm:
                candidates.append((idx, know_norm, know_name))
                break
    if not candidates:
        return []
    profiles: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, (start, norm, name) in enumerate(candidates):
        if norm in seen:
            continue
        block = normalized[start]
        next_is_candidate = (start + 1 < len(normalized) and line_is_name_candidate(normalized[start + 1], known_items))
        first_bio = extract_bio_from_name_line(blocks[start], name)
        if not first_bio and next_is_candidate:
            continue
        seen.add(norm)
        end = candidates[i + 1][0] if i + 1 < len(candidates) else len(normalized)
        bio_lines: list[str] = []
        if first_bio:
            bio_lines.append(first_bio)
        for line in blocks[start + 1:end]:
            cleaned = line.strip()
            if re.fullmatch(r'(?i)(show less|show more|meet the fellows:|meet the commissioner:|meet the team:|meet the commissioner|info|questions|contact|email|website|shov less)', cleaned):
                continue
            if canonical_name(cleaned) in known_name_norms and canonical_name(cleaned) != norm:
                break
            bio_lines.append(cleaned)
        bio = ' '.join(l for l in bio_lines if l).strip()
        if bio:
            profiles.append({'name': name, 'bio': bio})
    return profiles


def load_screenshot_profiles(path: Path, known_name_norms: dict[str, str]) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    result = []
    for rec in data:
        profiles = parse_profiles_from_blocks(rec['blocks'], known_name_norms)
        if not profiles and rec['blocks']:
            result.append({'name': '', 'bio': ' '.join(rec['blocks'])})
        else:
            result.extend(profiles)
    return result


def load_member_csv(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows = []
    with path.open('r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    name_map: dict[str, dict[str, str]] = {}
    for row in rows:
        name = normalize_text(row.get('name', ''))
        if not name:
            continue
        norm = canonical_name(name)
        if norm not in name_map or (row.get('role') and row['role'].strip().lower() not in ('fellow', '')):
            name_map[norm] = {'name': name, 'commission': row.get('commission', '').strip(), 'role': row.get('role', '').strip()}
    return rows, name_map


def extract_where_from(bio: str) -> str:
    patterns = [
        r'\bfrom\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)',
        r'\bbased in\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)',
    ]
    for pat in patterns:
        m = re.search(pat, bio)
        if m:
            return m.group(1).strip()
    nationalities = ['Italian', 'French', 'German', 'Spanish', 'Portuguese', 'Dutch', 'Belgian', 'Austrian', 'Swiss', 'British', 'American', 'Canadian', 'Indian', 'Chinese', 'Japanese', 'Korean', 'Greek', 'Polish', 'Swedish', 'Norwegian', 'Danish', 'Finnish', 'Irish', 'Croatian', 'Serbian', 'Romanian', 'Bulgarian', 'Czech', 'Hungarian', 'Slovak', 'Slovenian', 'Estonian', 'Latvian', 'Lithuanian', 'Maltese', 'Luxembourgish']
    for nat in nationalities:
        if re.search(r'\b' + re.escape(nat) + r'\b', bio, flags=re.I):
            return nat
    return ''


def extract_uni(bio: str) -> str:
    patterns = [
        r'at\s+([A-Z][A-Za-z& ]+(?:University|College|Institute|School|Politecnico|Faculty|Academy))',
        r'from\s+([A-Z][A-Za-z& ]+(?:University|College|Institute|School|Politecnico|Faculty|Academy))',
        r'([A-Z][A-Za-z& ]+(?:University|College|Institute|School|Politecnico|Faculty|Academy))',
    ]
    for pat in patterns:
        m = re.search(pat, bio)
        if m:
            return m.group(1).strip().replace('  ', ' ')
    return ''


def extract_interests(bio: str) -> str:
    matches = re.findall(r'(?i)(?:interested in|passionate about|focus(?:es)? on|interests? (?:lie|is|are) in|specialis(?:es|ing) in|aims to work on|strong interest in)\s+([^\.:;]+)', bio)
    cleaned = [m.strip(' :;,.') for m in matches]
    return '; '.join(dict.fromkeys(cleaned))


def load_article_titles(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    article_map: dict[str, str] = {}
    with path.open('r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = normalize_text(row.get('name', ''))
            if not name:
                continue
            norm = canonical_name(name)
            titles = row.get('article_titles', '').strip()
            if titles:
                article_map[norm] = titles
    return article_map


def parse_author_articles(names: list[str]) -> dict[str, set[str]]:
    name_map = {canonical_name(n): n for n in names if n}
    try:
        resp = requests.get('https://voycecommunity.eu/home/f.json', timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return {}
    author_articles: dict[str, set[str]] = defaultdict(set)
    for item in data.get('items', []):
        title = normalize_text(item.get('title', '')).strip()
        html = item.get('html_content', '') or ''
        raw = None
        m = re.search(r'<p[^>]*>(?:By|by)\s+(.+?)(?:</p>|\n|$)', html, re.DOTALL)
        if m:
            raw = m.group(1).strip()
        if not raw:
            summary = item.get('summary', '') or ''
            m = re.match(r'(?:By|by)\s+(.+)', summary)
            if m:
                raw = m.group(1).strip()
        if not raw:
            continue
        parts = re.split(r'\s*[,;]\s*|\s+and\s+|\s*&\s*', re.sub(r'\s+', ' ', raw))
        for part in parts:
            if len(part.split()) < 2:
                continue
            norm = canonical_name(part)
            if norm in name_map:
                author_articles[norm].add(title)
            else:
                close = difflib.get_close_matches(norm, list(name_map.keys()), n=1, cutoff=0.85)
                if close:
                    author_articles[close[0]].add(title)
    return author_articles


def main() -> None:
    csv_path = Path('voyce_commission_members.csv')
    if not csv_path.exists():
        raise SystemExit('voyce_commission_members.csv not found')
    _, name_map = load_member_csv(csv_path)
    known_name_norms = name_map
    screenshot_path = Path('screenshot_ocr_results.json')
    if not screenshot_path.exists():
        raise SystemExit('screenshot_ocr_results.json not found')
    profiles = load_screenshot_profiles(screenshot_path, known_name_norms)
    rows = []
    for profile in profiles:
        name = profile['name']
        norm = canonical_name(name)
        match = name_map.get(norm)
        if match is None:
            # try fuzzy match if OCR name variant exists
            close = difflib.get_close_matches(norm, list(name_map.keys()), n=1, cutoff=0.82)
            if close:
                match = name_map[close[0]]
        row = {
            'name': name,
            'canonical_name': norm,
            'commission': match['commission'] if match else '',
            'role': match['role'] if match else '',
            'bio': profile['bio'],
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df['where_from'] = df['bio'].apply(extract_where_from)
    df['uni'] = df['bio'].apply(extract_uni)
    df['interests'] = df['bio'].apply(extract_interests)
    article_titles_map = load_article_titles(Path('voyce_commission_members_unique.csv'))
    article_titles_map.update(load_article_titles(Path('voyce_commission_members.csv')))
    if not article_titles_map:
        all_names = [n for n in df['name'].tolist() if n]
        author_articles = parse_author_articles(all_names)
        article_titles_map = {k: '; '.join(sorted(v)) for k, v in author_articles.items()}
    df['article_titles'] = df['canonical_name'].apply(lambda n: article_titles_map.get(n, ''))
    df = df.drop_duplicates(subset=['canonical_name']).sort_values('name').reset_index(drop=True)
    out_csv = Path('voyce_members_from_screenshots.csv')
    out_xlsx = Path('voyce_members_from_screenshots.xlsx')
    df.to_csv(out_csv, index=False, encoding='utf-8')
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Members')
    print('saved', out_csv)
    print('saved', out_xlsx)
    print('profiles', len(df))
    print('missing commission count', (df['commission'] == '').sum())
    print('missing role count', (df['role'] == '').sum())
    print('missing articles count', (df['article_titles'].astype(str).str.strip() == '').sum())


if __name__ == '__main__':
    main()
