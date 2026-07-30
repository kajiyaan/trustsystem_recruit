"""各ページの共通パーツ（head メタ情報 / nav / footer）を全HTMLに同期する。

各HTMLファイル自体が原本。このスクリプトはページを生成し直すのではなく、
全ページで揃っているべき部分だけを上書きする。

    python sync.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = 'https://kajiyaan.github.io/trustsystem_recruit/'
TITLE_SUFFIX = ' | 株式会社トラストシステム 新卒採用'

# ページ名 -> (titleの先頭部分, meta description, navで強調するリンク先)
PAGES = {
    'index.html': (
        '新卒採用 特設サイト',
        '株式会社トラストシステム 新卒採用サイト。金融・通信インフラを支える独立系IT企業が、'
        '2027年新卒採用の募集要項・カルチャー・キャリアパス・社員インタビューを紹介します。',
        None,
    ),
    'about.html': (
        '会社について',
        '1985年創業、ミライト・ワングループの独立系IT企業「株式会社トラストシステム」の会社概要。'
        '事業内容・資本金・役員・所在地・主要取引先を紹介します。',
        'about.html',
    ),
    'business.html': (
        '事業内容',
        'コンサルティングから開発・運用保守まで一貫対応するトラストシステムの事業内容と'
        'プロジェクト事例を紹介。金融・通信インフラ分野での実績を掲載しています。',
        'business.html',
    ),
    'culture.html': (
        'カルチャー',
        '「人を大切にする」トラストシステムのカルチャーを紹介。'
        '新卒社員が安心して成長できる社風・チームの雰囲気について解説します。',
        'culture.html',
    ),
    'career.html': (
        'キャリアパス',
        '入社後のキャリアパスを紹介。若手社員がリーダーへ成長するまでの流れや、'
        'トラストシステムが用意する成長支援の仕組みを解説します。',
        'career.html',
    ),
    'welfare.html': (
        '福利厚生',
        'トラストシステムの福利厚生制度を紹介。住宅手当・資格取得支援など、'
        '新卒社員が安心して働ける制度を掲載しています。',
        'welfare.html',
    ),
    'interview.html': (
        '社員インタビュー',
        'トラストシステムで活躍する若手社員3名のインタビュー一覧。'
        '文系出身・IT未経験入社それぞれのキャリアストーリーを紹介します。',
        'interview.html',
    ),
    'interview_01.html': (
        'Interview 01 H・Sさん',
        '東京電機大学卒業後にトラストシステムへ入社し、6年目でリーダーに抜擢されたH・Sさんのインタビュー。',
        'interview.html',
    ),
    'interview_02.html': (
        'Interview 02 N・Tさん',
        '文系出身でエンジニアとしてトラストシステムに入社し、リーダーへの一歩を踏み出したN・Tさんのインタビュー。',
        'interview.html',
    ),
    'interview_03.html': (
        'Interview 03 T・Kさん',
        'IT未経験からトラストシステムに入社し、一つ一つの業務に真剣に取り組みながら'
        '成長を続けるT・Kさんのインタビュー。',
        'interview.html',
    ),
    'stories.html': (
        '社員の声・SNS',
        'Wantedlyに掲載中の社員ストーリーやSNS（X・Instagram）での最新情報をまとめて紹介。'
        'トラストシステムのリアルな日常を発信しています。',
        'stories.html',
    ),
    'recruit.html': (
        '募集要項',
        '2027年新卒採用の募集要項。応募資格・選考フロー・勤務地・給与など'
        'トラストシステムへのエントリーに必要な情報をまとめています。',
        'recruit.html',
    ),
    'entry.html': (
        'エントリー',
        'トラストシステム新卒採用へのエントリーページ。募集要項をご確認の上、こちらからご応募ください。',
        'entry.html',
    ),
}

NAV_ITEMS = [
    ('about.html', 'About'),
    ('business.html', 'Business'),
    ('culture.html', 'Culture'),
    ('career.html', 'Career'),
    ('welfare.html', 'Benefits'),
    ('interview.html', 'Interview'),
    ('stories.html', 'Stories'),
    ('recruit.html', '募集要項'),
]

ORGANIZATION = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    'name': '株式会社トラストシステム',
    'alternateName': 'Trust System Corporation',
    'url': SITE_URL,
    'logo': SITE_URL + 'img/logo_main.png',
    'foundingDate': '1985-01',
    'telephone': '+81-3-3253-0391',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': '外神田4-14-1 秋葉原UDX 北ウィング8F',
        'addressLocality': '千代田区',
        'addressRegion': '東京都',
        'postalCode': '101-0021',
        'addressCountry': 'JP',
    },
    'parentOrganization': {
        '@type': 'Organization',
        'name': 'ミライト・ワングループ',
    },
    'sameAs': [
        'https://www.trustsystem.co.jp/',
        'https://www.wantedly.com/companies/company_3952988',
    ],
}

# recruit.html の募集要項をそのまま構造化したもの
JOB_POSTING = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    'title': '開発エンジニア／インフラエンジニア（2027年新卒）',
    'description': (
        '<p>コンサルティングから企画・開発、運用・保守までシステムサイクル全般を手がける'
        '独立系IT企業の新卒採用です。金融・通信インフラなどミッションクリティカルな'
        'システム開発に携わります。</p>'
        '<ul>'
        '<li>対象：全学部・全学科（文理・IT経験不問）大学院生・大学生・短大生・高専生・専門学校生（2年制以上）</li>'
        '<li>採用予定人数：26〜30名</li>'
        '<li>初任給：専門2年卒 233,000円／月、四大卒 251,000円／月、院了 255,000円／月</li>'
        '<li>賞与：年2回（7月・12月）計5カ月分</li>'
        '<li>休日：年間126日／完全週休2日（土日祝）</li>'
        '<li>残業：月平均19時間（残業代1分単位で全額支給・固定残業制度なし）</li>'
        '<li>転居を伴う転勤なし</li>'
        '</ul>'
    ),
    'datePosted': '2026-07-30',
    'employmentType': 'FULL_TIME',
    'hiringOrganization': {
        '@type': 'Organization',
        'name': '株式会社トラストシステム',
        'sameAs': 'https://www.trustsystem.co.jp/',
        'logo': SITE_URL + 'img/logo_main.png',
    },
    'jobLocation': {
        '@type': 'Place',
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': '外神田4-14-1 秋葉原UDX 北ウィング8F',
            'addressLocality': '千代田区',
            'addressRegion': '東京都',
            'postalCode': '101-0021',
            'addressCountry': 'JP',
        },
    },
    'baseSalary': {
        '@type': 'MonetaryAmount',
        'currency': 'JPY',
        'value': {
            '@type': 'QuantitativeValue',
            'minValue': 233000,
            'maxValue': 255000,
            'unitText': 'MONTH',
        },
    },
    'workHours': '9:00〜17:30（実働7.5時間／昼休憩12:00〜13:00）',
    'qualifications': '全学部・全学科（文理・IT経験不問）。大学院生・大学生・短大生・高専生・専門学校生（2年制以上）',
    'industry': '情報サービス業',
    'jobBenefits': '賞与年2回（計5カ月分）／年間休日126日／完全週休2日（土日祝）／残業代1分単位で全額支給／転居を伴う転勤なし',
}

FOOTER = """<footer>
  <div>
    <a class="footer-logo" href="index.html"><img src="img/logo_main.png" alt="株式会社トラストシステム"></a>
    <p style="font-size:12px;color:var(--gray);margin-top:8px;">株式会社トラストシステム ／ ミライト・ワングループ</p>
  </div>
  <div class="footer-info">
    <p>〒101-0021 東京都千代田区外神田4-14-1</p>
    <p>秋葉原UDX 北ウィング8F</p>
    <p>TEL：03-3253-0391</p>
    <p style="margin-top:8px;color:rgba(138,155,176,0.5);">© 2026 Trust System Corporation. All rights reserved.</p>
  </div>
</footer>"""


def build_nav(active):
    accent = ' style="color:var(--accent);"'
    links = '\n'.join(
        f'    <li><a href="{href}"{accent if href == active else ""}>{label}</a></li>'
        for href, label in NAV_ITEMS
    )
    mobile = '\n'.join(f'  <a href="{href}">{label}</a>' for href, label in NAV_ITEMS)
    return f"""<nav>
  <a class="nav-logo" href="index.html">
    <img src="img/logo_main.png" alt="株式会社トラストシステム" class="nav-logo-img" onerror="this.style.display=&#39;none&#39;;this.nextElementSibling.style.display=&#39;flex&#39;;">
    <span style="display:none;font-family:&#39;Bebas Neue&#39;,sans-serif;font-size:18px;letter-spacing:3px;color:#0d1b2a;">TRUST<span style="color:#4a9eff;">SYSTEM</span></span>
    <div class="nav-logo-divider"></div>
    <div class="nav-logo-badge">
      <span class="nav-logo-badge-top">New Graduate</span>
      <span class="nav-logo-badge-bottom">RECRUITMENT 2027</span>
    </div>
  </a>
  <ul class="nav-links">
{links}
    <li><a href="entry.html" class="nav-entry">Entry</a></li>
  </ul>
  <button class="nav-hamburger" id="navHamburger" aria-label="メニュー">
    <span></span><span></span><span></span>
  </button>
</nav>
<div class="nav-mobile-overlay" id="navOverlay"></div>
<div class="nav-mobile-menu" id="navMobileMenu">
{mobile}
  <a href="entry.html" class="nav-entry-mobile">Entry</a>
</div>"""


NAV_RE = re.compile(
    r'<nav>.*?<div class="nav-mobile-menu" id="navMobileMenu">.*?</div>', re.S
)
FOOTER_RE = re.compile(r'<footer>.*?</footer>', re.S)
TITLE_RE = re.compile(r'<title>.*?</title>', re.S)
DESC_RE = re.compile(r'<meta\s+name="description"[^>]*>')
JSONLD_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)
OGP_RE = re.compile(r'<!-- OGP:START -->.*?<!-- OGP:END -->', re.S)


def page_url(name):
    return SITE_URL if name == 'index.html' else SITE_URL + name


def build_ogp(name, title, desc):
    url = page_url(name)
    og_type = 'article' if name.startswith('interview_') else 'website'
    full_title = title + TITLE_SUFFIX
    image = SITE_URL + 'img/ogp.jpg'
    return f"""<!-- OGP:START -->
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="株式会社トラストシステム 新卒採用">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{full_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<!-- OGP:END -->"""


def build_jsonld(name):
    data = [ORGANIZATION, JOB_POSTING] if name == 'recruit.html' else ORGANIZATION
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False, indent=2)
            + '\n</script>')


def sync(html, name, title, desc, active):
    html = TITLE_RE.sub(lambda m: f'<title>{title}{TITLE_SUFFIX}</title>', html, count=1)

    meta = f'<meta name="description" content="{desc}">'
    if DESC_RE.search(html):
        html = DESC_RE.sub(lambda m: meta, html, count=1)
    else:
        html = html.replace('</title>', '</title>\n' + meta, 1)

    ogp = build_ogp(name, title, desc)
    if OGP_RE.search(html):
        html = OGP_RE.sub(lambda m: ogp, html, count=1)
    else:
        html = html.replace(meta, meta + '\n' + ogp, 1)

    block = build_jsonld(name)
    if JSONLD_RE.search(html):
        html = JSONLD_RE.sub(lambda m: block, html, count=1)
    else:
        html = html.replace('</head>', block + '\n</head>', 1)

    html = NAV_RE.sub(lambda m: build_nav(active), html, count=1)
    html = FOOTER_RE.sub(lambda m: FOOTER, html, count=1)
    return html


def write_if_changed(path, content, label):
    if path.exists() and path.read_text(encoding='utf-8') == content:
        print(f'  unchanged  {label}')
    else:
        path.write_text(content, encoding='utf-8')
        print(f'  updated    {label}')


def build_sitemap():
    priority = {'index.html': '1.0', 'recruit.html': '0.9', 'entry.html': '0.9'}
    urls = []
    for name in PAGES:
        mtime = datetime.fromtimestamp((ROOT / name).stat().st_mtime).strftime('%Y-%m-%d')
        urls.append(
            '  <url>\n'
            f'    <loc>{page_url(name)}</loc>\n'
            f'    <lastmod>{mtime}</lastmod>\n'
            f'    <priority>{priority.get(name, "0.7")}</priority>\n'
            '  </url>'
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + '\n'.join(urls)
            + '\n</urlset>\n')


# 生成AI各社のクローラーを明示的に許可する（AIO対策）
ROBOTS = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {sitemap}
""".format(sitemap=SITE_URL + 'sitemap.xml')


def main():
    for name, (title, desc, active) in PAGES.items():
        path = ROOT / name
        original = path.read_text(encoding='utf-8')
        write_if_changed(path, sync(original, name, title, desc, active), name)

    write_if_changed(ROOT / 'sitemap.xml', build_sitemap(), 'sitemap.xml')
    write_if_changed(ROOT / 'robots.txt', ROBOTS, 'robots.txt')


if __name__ == '__main__':
    main()
