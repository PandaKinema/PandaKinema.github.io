# サイトマップ(sitemap.xml)を作る:Google などの検索エンジンに「このサイトにはこのページがあります」と伝える一覧
# トップ・作品ページ(games/ にあるもの)・PLAY&TOOLS のツール(このサイトの中にあるもの)を載せます
# GitHub Actions が保存のたびに動かすので、作品やツールが増えても自動で追加されます
import os, subprocess, yaml
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = 'https://pandakinema.com/'

def load(n):
    with open(os.path.join(ROOT, 'content', n + '.yml'), encoding='utf-8') as f:
        return yaml.safe_load(f) or []

def lastmod(path):   # そのページを最後に更新した日(git の記録から)。わからなければ書かない
    try:
        d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return d or None
    except Exception:
        return None

pages = [('', 'index.html')]   # (URL のうしろ, もとのファイル)
games_dir = os.path.join(ROOT, 'games')
for key in sorted(os.listdir(games_dir)):
    if os.path.isfile(os.path.join(games_dir, key, 'index.html')):
        pages.append(('games/%s/' % key, 'games/%s/index.html' % key))
for t in load('tools'):   # ツールはこのサイトの中にあるものだけ
    u = (t.get('url') or '').strip()
    if u.startswith(SITE_URL):
        rel = u[len(SITE_URL):]
        f = rel + 'index.html' if (rel == '' or rel.endswith('/')) else rel
        if os.path.isfile(os.path.join(ROOT, f)) and all(p[0] != rel for p in pages):
            pages.append((rel, f))

lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for rel, f in pages:
    lm = lastmod(f)
    lines.append('  <url><loc>%s</loc>%s</url>' % (escape(SITE_URL + rel), '<lastmod>%s</lastmod>' % lm if lm else ''))
lines.append('</urlset>')
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('sitemap.xml', len(pages), 'pages')
