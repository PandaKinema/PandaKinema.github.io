# 遊び方説明書(WEB版)を作る
#   content/rules/<key>/meta.yml  … 色・ロゴ・人数・表紙の文(表紙と目次の材料)
#   content/rules/<key>/body.html … 章(<section class="panel" id="...">)を並べたもの。動画・更新履歴・目次は自動
#   content/rules/<key>/extra.css … その作品の図だけで使う見た目
#   content/pages/<key>.yml の rules_history … 更新履歴(編集画面の「作品ページ」から足せる)
#   build/rules/common.css, shell.html … 全作品共通の見た目と枠
# 画像は {{img:parts/bc_7.webp}} のように img/ からの道のりで書く。
#
#   python build/rules.py                 → games/<key>/rules/index.html と rules/index.html(一覧)
#   python build/rules.py --preview DIR   → 確認用(画像ごと DIR に書き出す)
import hashlib, html as H, os, re, shutil, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = 'https://pandakinema.com/'
TPL = os.path.join(ROOT, 'build', 'rules')
SRC = os.path.join(ROOT, 'content', 'rules')
IMG = os.path.join(ROOT, 'img')

try:   # 日本語の改行を文節の切れ目で(BudouX)。入っていなければ改行の調整なしで作る
    import budoux
    PARSER = budoux.load_default_japanese_parser()
except ImportError:
    PARSER = None
    print('budoux がないので、改行の調整なしで作ります(pip install budoux)')

JA = re.compile(r'[぀-ヿ㐀-鿿]')
TAG = re.compile(r'<(/?)([a-zA-Z0-9]+)\b[^>]*?(/?)>')
VOID = {'br', 'img', 'wbr', 'meta', 'link', 'input', 'hr', 'source'}
NOBREAK = ['遊び方', '捨て札', '手札', '山札', '場札', 'ダミー山札', 'ダミープレイヤー', '天罰マーク', '順位処理', '数字カード', 'トゥーパ トークン',
           '遊び方説明書', 'ラウンド勝利マーカー', 'リードプレイヤー', 'トリコマーカー', 'リードプレイヤーマーカー', '仮想プレイヤー']
WARN_ICON = ('<svg viewBox="0 0 22 20" aria-hidden="true"><path d="M11 1.2 21 18.8H1z" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'
             '<path d="M11 6.6v6.2" stroke="var(--head)" stroke-width="2.4" stroke-linecap="round"/><circle cx="11" cy="15.6" r="1.4" fill="var(--head)"/></svg>')
MARKS = {'rule': ('ルール変更', 'Rule change'), 'errata': ('訂正', 'Correction')}


def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def read(path, default=''):
    return open(path, encoding='utf-8').read() if os.path.isfile(path) else default


# ---------- 改行(文節の切れ目に <wbr>) ----------
def close_of(s, name, start):
    depth = 1
    for m in TAG.finditer(s, start):
        if m.group(2).lower() != name or name in VOID:
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.start(), m.end()
    raise ValueError('閉じタグがない: ' + name)


def phrase(inner, nobreak):
    if PARSER is None or not JA.search(re.sub(r'<[^>]+>', '', inner)):
        return inner
    out = PARSER.translate_html_string(inner)
    out = out.replace('<span style="word-break: keep-all; overflow-wrap: anywhere;">', '<span class="bx">', 1)
    out = out.replace('​', '<wbr>')
    out = re.sub(r'<wbr>(?=(?:</?(?:em|b|span)[^>]*>)*[!?！？)）」』、。・…ー〜~])', '', out)   # 閉じかっこ・句読点の前では折り返さない
    out = re.sub(r'(?<=[(（「『〔])((?:<[^>]+>)*)<wbr>', r'\1', out)                                 # 開きかっこのあとでも
    for w in sorted(nobreak, key=len, reverse=True):   # ゲームの用語は途中で折り返さない
        out = re.sub('(?:<wbr>)?'.join(map(re.escape, w)), w, out)
    return out


def phrase_all(src, nobreak):
    """class="ja" の要素(と ul.ja / ol.ja / dl.ja の中)の中身に <wbr> を入れる。目次は除く"""
    start = src.index('<body>')
    toc0 = src.find('<nav class="toc"'); toc1 = src.find('</nav>', toc0) if toc0 >= 0 else -1
    spans = []
    for m in TAG.finditer(src, start):
        if m.group(1) or m.group(3):
            continue
        name = m.group(2).lower()
        if name in ('script', 'style'):
            continue
        cls = re.search(r'class="([^"]*)"', m.group(0))
        if not cls or 'ja' not in cls.group(1).split() or (toc0 >= 0 and toc0 <= m.start() <= toc1):
            continue
        c0, _ = close_of(src, name, m.end())
        if name in ('ul', 'ol', 'dl'):
            for li in re.finditer(r'<(li|dt|dd)\b[^>]*>', src[m.end():c0]):
                a = m.end() + li.end(); b, _ = close_of(src, li.group(1), a)
                spans.append((a, b))
        else:
            spans.append((m.end(), c0))
    spans.sort()
    out, last = [], 0
    for a, b in spans:
        if a < last:
            continue
        out.append(src[last:a]); out.append(phrase(src[a:b], nobreak)); last = b
    out.append(src[last:])
    return ''.join(out)


# ---------- 目次 ----------
def make_toc(body):
    items, plain = [], []
    secs = list(re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>', body))
    for i, m in enumerate(secs):
        end = secs[i + 1].start() if i + 1 < len(secs) else len(body)
        chunk = body[m.start():end]
        t = re.search(r'data-toc="([^"]*)"', m.group(0))
        if t:
            ja, _, en = t.group(1).partition('|')
            label = '<span class="ja">%s</span><span class="en">%s</span>' % (ja, en or ja)
        else:
            h = re.search(r'<h2\b[^>]*>(.*?)</h2>', chunk, re.S) or re.search(r'class="warn-t"[^>]*>(.*?)</p>', chunk, re.S)
            label = re.sub(r'<svg.*?</svg>', '', h.group(1), flags=re.S).strip()
            ja = re.sub(r'<[^>]+>', '', re.search(r'<span class="ja">(.*?)</span>', label).group(1)) if 'class="ja"' in label else re.sub(r'<[^>]+>', '', label)
        plain.append(ja)
        sub = ''
        steps = re.findall(r'<li class="step[^"]*" id="([^"]+)"[^>]*>.*?<span class="snum"[^>]*><b>([^<]+)</b>', chunk, re.S)
        if steps:
            sub = '\n          <div class="sub" aria-label="手順">' + ''.join('<a href="#%s">%s</a>' % s for s in steps) + '</div>'
        items.append('        <li><a href="#%s">%s</a>%s</li>' % (m.group(1), label, sub))
    return items, plain


# ---------- 更新履歴(作品ページの編集画面の rules_history。なければ meta.yml の history) ----------
def history_of(key, meta):
    page = load(os.path.join(ROOT, 'content', 'pages', key + '.yml')) if os.path.isfile(os.path.join(ROOT, 'content', 'pages', key + '.yml')) else {}
    rows = []
    for h in page.get('rules_history') or []:
        if not h or not h.get('date') or not h.get('text_ja'):
            continue
        rows.append(dict(date=str(h['date'])[:10].replace('-', '.'), mark=h.get('mark') or '', ja=str(h['text_ja']).strip(), en=str(h.get('text_en') or '').strip()))
    if not rows:
        for h in meta.get('history') or []:
            rows.append(dict(date=str(h['date']).replace('-', '.'), mark='errata' if h.get('errata') else 'rule' if h.get('rule_change') else '', ja=h['ja'], en=h.get('en') or ''))
    return rows


def history_html(rows):
    out = []
    for h in rows:
        mk = MARKS.get(h['mark'])
        badge = '<span class="chg"><span class="ja">%s</span><span class="en">%s</span></span>' % mk if mk else ''
        out.append('          <li><time datetime="%s">%s</time><span>%s<span class="ja">%s</span><span class="en">%s</span></span></li>' % (
            h['date'].replace('.', '-'), h['date'], badge, H.escape(h['ja']), H.escape(h['en'] or h['ja'])))
    return '\n'.join(out)


# ---------- 画像 ----------
def img_file(path):
    p = os.path.join(IMG, path)
    if not os.path.isfile(p):
        raise FileNotFoundError('画像がない: img/' + path)
    return p


_md5 = {}
def bust(path):
    f = img_file(path)
    if f not in _md5:
        _md5[f] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
    return path + '?v=' + _md5[f]


def fill_imgs(p, prefix, used):
    def rep(m):
        path = m.group(1)
        used.add(path)
        return prefix + bust(path)
    return re.sub(r'\{\{img:([^}]+)\}\}', rep, p)


# ---------- 1作品 ----------
def keys():
    order = [g['key'] for g in (load(os.path.join(ROOT, 'content', 'games.yml')) or [])]
    have = [k for k in os.listdir(SRC) if os.path.isfile(os.path.join(SRC, k, 'meta.yml'))] if os.path.isdir(SRC) else []
    return [k for k in order if k in have] + sorted(k for k in have if k not in order)


def build_page(key):
    d = os.path.join(SRC, key)
    meta = load(os.path.join(d, 'meta.yml'))
    body = read(os.path.join(d, 'body.html')).replace('{{warn_icon}}', WARN_ICON)
    extra = read(os.path.join(d, 'extra.css'))
    shell = read(os.path.join(TPL, 'shell.html'))
    common = read(os.path.join(TPL, 'common.css'))
    page_yml = load(os.path.join(ROOT, 'content', 'pages', key + '.yml')) if os.path.isfile(os.path.join(ROOT, 'content', 'pages', key + '.yml')) else {}

    toc_items, toc_plain = make_toc(body)
    toc_items.append('        <li><a href="#history"><span class="ja">更新履歴</span><span class="en">Updates</span></a></li>')
    hist = history_of(key, meta)

    # 遊び方動画:youtube を入れた作品だけ「動画で見る」を出す(準備中の作品は章ごと出さない)
    yt = meta.get('youtube')
    video = ''
    if yt:
        toc_items.insert(0, '        <li><a href="#video"><span class="ja">動画で見る</span><span class="en">Video</span></a></li>')
        video = ('      <section class="panel" id="video" aria-labelledby="h-video">\n'
                 '        <h2 id="h-video"><span class="ja">動画で見る</span><span class="en">Watch the Video</span></h2>\n'
                 '        <div class="screen"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s 遊び方動画" '
                 'allow="encrypted-media; picture-in-picture" allowfullscreen loading="lazy" style="position:absolute;inset:0;width:100%%;height:100%%;border:0"></iframe></div>\n'
                 '      </section>\n') % (H.escape(yt), H.escape(meta['title_ja']))

    th = dict(meta['theme'])
    try:   # 帯があれば、本文の上下に帯ぶんの余白(18px + 帯 + 18px)
        bh = int(str(th.get('band-h', '0')).replace('px', '')) if th.get('band') not in (None, '', 'none') else 0
    except ValueError:
        bh = 0
    th['band-space'] = '%dpx' % (bh + 36 if bh else 0)
    th.setdefault('film-icon', 'url({{img:page/mt_film.svg}})')
    theme = '\n'.join('    --%s:%s;' % (k, v) for k, v in th.items())
    fonts = ''
    if meta.get('fonts'):
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&amp;display=swap">') % '&amp;'.join('family=' + f for f in meta['fonts'])
    og = page_yml.get('ogp_image') or ''
    og = (SITE_URL + 'img/' + og.split('img/', 1)[-1]) if og else ''

    rep = {
        'common_css': common, 'theme': theme, 'extra_css': extra, 'fonts': fonts,
        'toc': '\n'.join(toc_items), 'toc_text': '、'.join(['内容物'] + [t for t in toc_plain if t != '内容物'][:6] + ['更新履歴']),
        'body': body, 'video': video, 'history': history_html(hist),
        'updated': max((h['date'] for h in hist), default=''),
        'logo': '{{img:%s}}' % meta['logo'],
        'series': ('        <p class="series">%s</p>\n' % H.escape(meta['series'])) if meta.get('series') else '',
        'og_image': og, 'page_url': SITE_URL + 'games/%s/rules/' % key,
    }
    for k in ('title_ja', 'title_en', 'logo_alt', 'players_ja', 'players_en', 'time_ja', 'time_en', 'age_ja', 'age_en',
              'printed_ja', 'printed_en', 'catch_ja', 'catch_en', 'story_ja', 'story_en', 'booth'):
        rep[k] = meta[k]
    p = shell
    for k, v in rep.items():
        p = p.replace('{{%s}}' % k, str(v))
    if not og:
        p = re.sub(r'<meta property="og:image"[^>]*>\n', '', p)
    p = phrase_all(p, NOBREAK + (meta.get('nobreak') or []))
    p = p.replace('{{wbr}}', '<wbr>')   # 本文で折り返してよい位置を手で指定するとき
    return meta, hist, p


def finish(p, root, game_page, rules_index, img_prefix, used, preview=False):
    p = p.replace('{{root}}', root).replace('{{game_page}}', game_page).replace('{{rules_index}}', rules_index)
    if not preview:
        p = p.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    p = fill_imgs(p, img_prefix, used)
    assert '{{' not in p, re.findall(r'\{\{[^}]*\}\}', p)[:3]
    return p


# ---------- 一覧(rules/) ----------
def index_page(items, root, link, img_prefix, used, preview=False):
    t = read(os.path.join(TPL, 'index.html'))
    games = {g['key']: g for g in (load(os.path.join(ROOT, 'content', 'games.yml')) or [])}
    cards = []
    for key, meta, hist in items:
        g = games.get(key, {})
        front = str(g.get('front') or '').split('img/', 1)[-1]
        face = ('<img src="{{img:%s}}" alt="%s" loading="lazy">' % (front, H.escape(meta['title_ja']))) if front else '<span class="noimg">%s</span>' % H.escape(meta['title_ja'])
        upd = max((h['date'] for h in hist), default='')
        fix = any(h['mark'] == 'errata' for h in hist)
        cards.append(
            '      <li><a class="rb" href="%s">\n        <span class="face">%s</span>\n'
            '        <span class="meta"><span class="nm">%s</span><span class="up"><span class="ja">最終更新 %s</span><span class="en">Updated %s</span></span>%s</span>\n      </a></li>' % (
                link(key), face, H.escape(meta['title_ja']), upd, upd,
                '<span class="fix"><span class="ja">説明書の訂正あり</span><span class="en">Includes corrections</span></span>' if fix else ''))
    site = load(os.path.join(ROOT, 'content', 'site.yml'))
    og = str(site.get('ogp_image') or '')
    og = (SITE_URL + 'img/' + og.split('img/', 1)[-1]) if og else ''
    p = t.replace('{{cards}}', '\n'.join(cards)).replace('{{root}}', root).replace('{{og_image}}', og)
    if not og:
        p = re.sub(r'<meta property="og:image"[^>]*>\n', '', p)
    p = phrase_all(p, NOBREAK)
    if not preview:
        p = p.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    p = fill_imgs(p, img_prefix, used)
    assert '{{' not in p, re.findall(r'\{\{[^}]*\}\}', p)[:3]
    return p


PREVIEW_BACK = '''<a class="pv-back" href="../index.html">← 一覧へ</a>
<style>
  .pv-back{position:fixed;left:calc(12px + env(safe-area-inset-left,0px));bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:70;
    padding:10px 16px;border-radius:999px;background:#000;color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.35),0 0 0 1.5px rgba(255,255,255,.55);
    font:800 14px/1 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;text-decoration:none}
  .pv-back:focus-visible{outline:2px solid #fff;outline-offset:3px}
</style>'''


def main():
    args = sys.argv[1:]
    preview = None
    if args[:1] == ['--preview']:
        preview = os.path.abspath(args[1])
    items = []
    for key in keys():
        meta, hist, page = build_page(key)
        items.append((key, meta, hist))
        used = set()
        if preview:
            out = finish(page, SITE_URL, SITE_URL + 'games/%s/' % key, '../index.html', '../img/', used, preview=True)
            out = out.replace('</body>', PREVIEW_BACK + '\n</body>', 1)
            dst = os.path.join(preview, key, 'index.html')
        else:
            out = finish(page, '../../../', '../', '../../../rules/', '../../../img/', used)
            dst = os.path.join(ROOT, 'games', key, 'rules', 'index.html')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(out)
        if preview:
            for u in used:
                t = os.path.join(preview, 'img', u); os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copyfile(img_file(u), t)
        print('games/%s/rules/ 画像%d' % (key, len(used)))
    used = set()
    if preview:
        out = index_page(items, SITE_URL, lambda k: '%s/index.html' % k, 'img/', used, preview=True)
        dst = os.path.join(preview, 'index.html')
    else:
        out = index_page(items, '../', lambda k: '../games/%s/rules/' % k, '../img/', used)
        dst = os.path.join(ROOT, 'rules', 'index.html')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8').write(out)
    if preview:
        for u in used:
            t = os.path.join(preview, 'img', u); os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copyfile(img_file(u), t)
    print('rules/(一覧)%d作品' % len(items))


if __name__ == '__main__':
    main()
