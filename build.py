import re, base64, os

SRC = 'C:/Users/kajiy/Downloads/新卒採用 特設サイト _ 株式会社トラストシステム.html'
OUT = 'C:/Users/kajiy/Downloads/trustsystem_recruit'

with open(SRC, 'r', encoding='utf-8') as f:
    raw = f.read()

# --- Extract & replace base64 images ---
img_pattern = r'src="data:(image/(\w+));base64,([^"]+)"'
img_matches = list(re.finditer(img_pattern, raw))
img_map = {}  # original full match -> new src attribute
for i, m in enumerate(img_matches):
    ext = m.group(2)
    fname = f'img_{i}.{ext}'
    fpath = os.path.join(OUT, 'img', fname)
    if not os.path.exists(fpath):
        with open(fpath, 'wb') as f:
            f.write(base64.b64decode(m.group(3)))
    img_map[m.group(0)] = f'src="img/{fname}"'

# Replace all base64 src in raw
clean_raw = raw
for orig, new in img_map.items():
    clean_raw = clean_raw.replace(orig, new)

# --- Extract CSS ---
HAMBURGER_CSS = """
  /* ===== HAMBURGER MENU ===== */
  .nav-hamburger {
    display: none;
    flex-direction: column;
    justify-content: center;
    gap: 5px;
    cursor: pointer;
    padding: 8px;
    background: none;
    border: none;
    z-index: 200;
  }
  .nav-hamburger span {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--white);
    transition: all 0.3s ease;
    border-radius: 1px;
  }
  .nav-hamburger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
  .nav-hamburger.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
  .nav-hamburger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

  .nav-mobile-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 150;
    backdrop-filter: blur(2px);
  }
  .nav-mobile-overlay.open { display: block; }

  .nav-mobile-menu {
    position: fixed;
    top: 0; right: 0; bottom: 0;
    width: 280px;
    background: var(--dark);
    border-left: 1px solid rgba(74,158,255,0.15);
    z-index: 160;
    transform: translateX(100%);
    transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
    padding: 88px 40px 40px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
  .nav-mobile-menu.open { transform: translateX(0); }
  .nav-mobile-menu a {
    color: var(--gray);
    text-decoration: none;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 18px 0;
    border-bottom: 1px solid rgba(74,158,255,0.08);
    transition: color 0.3s;
    display: block;
  }
  .nav-mobile-menu a:hover { color: var(--accent); }
  .nav-mobile-menu .nav-entry-mobile {
    margin-top: 28px;
    background: var(--accent);
    color: var(--black) !important;
    text-align: center;
    padding: 14px 0;
    border-radius: 2px;
    font-weight: 700;
    border-bottom: none;
    letter-spacing: 2px;
  }
  .nav-mobile-menu .nav-entry-mobile:hover { background: #6bb3ff; }

  @media (max-width: 768px) {
    .nav-hamburger { display: flex; }
  }
"""

css_match = re.search(r'<style>(.*?)</style>', clean_raw, re.DOTALL)
if css_match:
    css_path = os.path.join(OUT, 'css', 'style.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_match.group(1) + HAMBURGER_CSS)
    print('style.css saved')

# --- Extract sections ---
markers = ['NAV','HERO','MARQUEE','ABOUT','CLIENTS','NUMBERS','BUSINESS','PROJECTS',
           'CULTURE','CAREER PATH','WELFARE','WANTEDLY STORIES','SNS','X',
           'RECRUIT INFO','ENTRY','FOOTER']
positions = {}
for m in markers:
    pat = r'<!--\s*' + re.escape(m) + r'\s*-->'
    match = re.search(pat, clean_raw)
    if match:
        positions[m] = match.start()

sorted_m = sorted(positions.items(), key=lambda x: x[1])
sections = {}
for i, (name, pos) in enumerate(sorted_m):
    end = sorted_m[i+1][1] if i+1 < len(sorted_m) else len(clean_raw)
    sections[name] = clean_raw[pos:end].strip()

# --- Build clean NAV ---
nav_html = sections['NAV']
anchor_map = {
    'about': 'about.html', 'numbers': 'about.html',
    'business': 'business.html', 'projects': 'business.html',
    'culture': 'culture.html', 'career': 'career.html',
    'stories': 'stories.html', 'welfare': 'welfare.html',
    'recruit': 'recruit.html', 'entry': 'entry.html',
    'sns': 'stories.html',
}
# Replace absolute URLs with anchor → page link
def replace_href(m):
    anchor = m.group(1)
    return 'href="' + anchor_map.get(anchor, '#') + '"'
nav_html = re.sub(r'href="https?://[^"]*#([a-z]+)"', replace_href, nav_html)
# Replace remaining anchor-only hrefs
for anchor, page in anchor_map.items():
    nav_html = nav_html.replace(f'href="#{anchor}"', f'href="{page}"')
nav_html = re.sub(r'href="https?://[^"]*#?"', 'href="index.html"', nav_html)
# Fix logo link: strip href, add index.html
nav_html = re.sub(r'(<a\s+href="[^"]*")(\s+class="nav-logo")', r'<a\2', nav_html)
nav_html = nav_html.replace('class="nav-logo"', 'class="nav-logo" href="index.html"')
# Remove nav items merged into other pages
nav_html = re.sub(r'\s*<li><a href="about\.html">Numbers</a></li>', '', nav_html)
nav_html = re.sub(r'\s*<li><a href="stories\.html">SNS</a></li>', '', nav_html)
nav_html = re.sub(r'\s*<li><a href="business\.html">Projects</a></li>', '', nav_html)
# Add Benefits link before Stories if not already present
if 'href="welfare.html">Benefits' not in nav_html:
    nav_html = nav_html.replace(
        '<li><a href="stories.html">Stories</a></li>',
        '<li><a href="welfare.html">Benefits</a></li>\n    <li><a href="interview.html">Interview</a></li>\n    <li><a href="stories.html">Stories</a></li>'
    )
# Add hamburger button + mobile menu
nav_html = nav_html.replace('</nav>', """  <button class="nav-hamburger" id="navHamburger" aria-label="メニュー">
    <span></span><span></span><span></span>
  </button>
</nav>
<div class="nav-mobile-overlay" id="navOverlay"></div>
<div class="nav-mobile-menu" id="navMobileMenu">
  <a href="about.html">About</a>
  <a href="business.html">Business</a>
  <a href="culture.html">Culture</a>
  <a href="career.html">Career</a>
  <a href="welfare.html">Benefits</a>
  <a href="interview.html">Interview</a>
  <a href="stories.html">Stories</a>
  <a href="recruit.html">募集要項</a>
  <a href="entry.html" class="nav-entry-mobile">Entry</a>
</div>""")

# --- Build clean FOOTER ---
footer_html = sections['FOOTER']
footer_match = re.search(r'<footer>.*?</footer>', footer_html, re.DOTALL)
footer_only = footer_match.group(0) if footer_match else footer_html

# --- Common JS ---
js = """<script>
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.number-card,.biz-card,.culture-card,.welfare-item,.fork-card,.project-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
  const nav = document.querySelector('nav');
  window.addEventListener('scroll', () => {
    nav.style.background = window.scrollY > 50 ? 'rgba(10,10,15,0.97)' : 'rgba(10,10,15,0.85)';
  });
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a:not(.nav-entry)').forEach(a => {
    if (a.getAttribute('href') === currentPage) a.style.color = 'var(--accent)';
  });
  const hamburger = document.getElementById('navHamburger');
  const overlay = document.getElementById('navOverlay');
  const mobileMenu = document.getElementById('navMobileMenu');
  function toggleMenu(open) {
    hamburger.classList.toggle('open', open);
    overlay.classList.toggle('open', open);
    mobileMenu.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  }
  hamburger.addEventListener('click', () => toggleMenu(!mobileMenu.classList.contains('open')));
  overlay.addEventListener('click', () => toggleMenu(false));
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => toggleMenu(false)));
</script>"""

NAV_SPACER = '<div style="height:80px;"></div>'

def make_page(title, body):
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ja">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + title + ' | 株式会社トラストシステム 新卒採用</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Bebas+Neue&family=Cormorant+Garamond:wght@300;400;600&display=swap" rel="stylesheet">\n'
        '<link rel="stylesheet" href="css/style.css">\n'
        '<link rel="icon" type="image/png" href="img/favicon.png">\n'
        '</head>\n'
        '<body>\n'
        + nav_html + '\n'
        + body + '\n'
        + footer_only + '\n'
        + js + '\n'
        '</body>\n'
        '</html>'
    )

# ============================================================
# index.html  (Hero + Marquee + Numbers)
# ============================================================
hero = sections['HERO']
hero = re.sub(r'href="https?://[^"]*#([a-z]+)"', replace_href, hero)
for anchor, page in anchor_map.items():
    hero = hero.replace(f'href="#{anchor}"', f'href="{page}"')
index_body = hero + '\n' + sections['MARQUEE'] + '\n' + sections['NUMBERS']
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('新卒採用 特設サイト', index_body))
print('index.html done')

# ============================================================
# about.html  (About + Clients)
# ============================================================
about_body = NAV_SPACER + '\n' + sections['ABOUT'] + '\n' + sections['CLIENTS']
with open(os.path.join(OUT, 'about.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('会社について', about_body))
print('about.html done')

# ============================================================
# business.html  (Business + Projects)
# ============================================================
biz_body = NAV_SPACER + '\n' + sections['BUSINESS'] + '\n' + sections['PROJECTS']
with open(os.path.join(OUT, 'business.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('事業内容', biz_body))
print('business.html done')

# ============================================================
# culture.html
# ============================================================
culture_body = NAV_SPACER + '\n' + sections['CULTURE']
with open(os.path.join(OUT, 'culture.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('カルチャー', culture_body))
print('culture.html done')

# ============================================================
# career.html
# ============================================================
career_body = NAV_SPACER + '\n' + sections['CAREER PATH']
with open(os.path.join(OUT, 'career.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('キャリアパス', career_body))
print('career.html done')

# ============================================================
# welfare.html
# ============================================================
welfare_body = NAV_SPACER + '\n' + sections['WELFARE']
with open(os.path.join(OUT, 'welfare.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('福利厚生', welfare_body))
print('welfare.html done')

# ============================================================
# stories.html  (Wantedly + SNS + X/Instagram)
# ============================================================
stories_body = NAV_SPACER + '\n' + sections['WANTEDLY STORIES'] + '\n' + sections['SNS'] + '\n' + sections['X']
with open(os.path.join(OUT, 'stories.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('社員の声・SNS', stories_body))
print('stories.html done')

# ============================================================
# recruit.html
# ============================================================
recruit_body = NAV_SPACER + '\n' + sections['RECRUIT INFO']
with open(os.path.join(OUT, 'recruit.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('募集要項', recruit_body))
print('recruit.html done')

# ============================================================
# entry.html
# ============================================================
entry_body = NAV_SPACER + '\n' + sections['ENTRY']
with open(os.path.join(OUT, 'entry.html'), 'w', encoding='utf-8') as f:
    f.write(make_page('エントリー', entry_body))
print('entry.html done')

print('\nAll pages created!')
