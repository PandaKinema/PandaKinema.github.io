# ニュースの共有カード:ニュースごとに、タイトルと日付が入ったチケット型の画像(1200×630)と、
# Xで共有するためのページ(news/<id>/)を作ります。post.html の「Xに投稿する」はこのページのURLを使うので、
# Xに投稿するとこのカードが出ます。ページを開いた人は、そのニュースのリンク先(なければトップのニュース)へ移動します。
# 一度作ったカードとページは消しません(すでにXに投稿したカードが消えないように)。
# タイトル・日付・カテゴリを直すと、新しいID(=新しい画像とページ)になります。
#   python build/news_cards.py          … ニュースのカードを作る(GitHub Actions が保存のたびに動かします)
#   python build/news_cards.py --tools  … ツールの共有カードを作り直す(手で動かすとき用)
import hashlib, html, json, os, re, sys
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = 'https://pandakinema.com/'
FONT_DIR = os.path.join(ROOT, 'build', 'fonts')
CARD_DIR = os.path.join(ROOT, 'img', 'share', 'news')
PAGE_DIR = os.path.join(ROOT, 'news')
VERSION = 'v1'   # カードのデザインを変えたら上げる(全部のカードが新しいIDで作り直される)

OUTER = '#0a0c0c'                    # チケットのまわり(キネマブラック)
DEFAULT = ('#fff5d7', '#1b2228')     # 作品に関係しないニュース:アイボリーのチケット
TICKET = {                           # 作品のニュース:作品の共有カードと同じ色(チケット, 文字)
    'trico': ('#664498', '#fdd000'),
    'ikatako': ('#00215d', '#ffffff'),
    'moko': ('#39278b', '#f19ebc'),
    'bibilu': ('#153e53', '#fff5d7'),
    'koikoi': ('#1b2228', '#ffffff'),
    'bash': ('#1b2228', '#ffffff'),
}

S = 2   # 2倍で描いて縮める(ふちをなめらかに)


def load(n):
    with open(os.path.join(ROOT, 'content', n + '.yml'), encoding='utf-8') as f:
        return yaml.safe_load(f) or []


def font(kind, size):
    names = {'jp': ['NotoSansCJKjp-Bold-subset.otf'], 'cn': ['texgyreheroscn-bold.otf']}[kind]
    for n in names:
        p = os.path.join(FONT_DIR, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, int(size * S))
    raise SystemExit('フォントが見つかりません: ' + ', '.join(names))


# ---------- ニュースの情報 ----------
def related_game(n, games):
    """リンク先が games/<key>/ か、タイトルに作品名が入っていれば、その作品"""
    link = str(n.get('link') or '')
    m = re.search(r'games/([\w-]+)/?', link)
    g = next((x for x in games if m and x['key'] == m.group(1)), None)
    if not g:
        t = str(n.get('text_ja') or '')
        g = next((x for x in games if x.get('name') and (x['name'] in t or x['name'].replace(' ', '') in t)), None)
    return g


def news_id(n):
    d = str(n.get('date') or '').strip().replace('/', '-').replace('.', '-')
    key = '|'.join([VERSION, d, str(n.get('cat_ja') or ''), str(n.get('text_ja') or '').strip()])
    return '%s-%s' % (d, hashlib.sha1(key.encode('utf-8')).hexdigest()[:6])


def news_url(n):
    return SITE_URL + 'news/%s/' % news_id(n)


def target_url(n):
    link = str(n.get('link') or '').strip()
    if link.startswith('http'):
        return link
    return SITE_URL + link.lstrip('/') if link else SITE_URL + '#news'


# ---------- 文字 ----------
def text_layer(parts, color):
    """parts = [(文字, フォント, 字間px), ...] を同じベースラインで横に並べ、インクの範囲で切り抜いた画像"""
    w = sum(sum(f.getlength(ch) for ch in t) + ls * S * len(t) for t, f, ls in parts) + 40 * S * len(parts)
    h = max(f.size for _, f, _ in parts) * 2
    img = Image.new('RGBA', (int(w) + 20, int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, base = 10, int(h * .7)
    for i, (t, f, ls) in enumerate(parts):
        for ch in t:
            d.text((x, base), ch, font=f, fill=color, anchor='ls')
            x += f.getlength(ch) + ls * S
        x -= ls * S
        if i < len(parts) - 1:
            x += 16 * S
    return img.crop(img.getchannel('A').getbbox())


NO_START = set('、。，．,.・：:；;？?！!ー）)」』】〕｝}〉》ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ…‥々')
NO_END = set('（(「『【〔｛{〈《')
PARTICLES = set('をがにでとへもやはのね')


def kind(ch):
    o = ord(ch)
    if 0x3040 <= o <= 0x309f:
        return 'h'
    if 0x30a0 <= o <= 0x30ff or ch == 'ー':
        return 'k'
    if 0x4e00 <= o <= 0x9fff or ch == '々':
        return 'c'
    if ch.isascii() and (ch.isalnum() or ch in "&'-"):
        return 'a'
    return 'p'


def phrases(t):
    """改行してよいところで区切る(助詞のあと・句読点のあと・カッコの外)"""
    out, cur, depth = [], '', 0
    for i, ch in enumerate(t):
        if ch in NO_END:
            if cur and depth == 0 and ch in '『「【' and kind(cur[-1]) in 'hp' and cur[-1] not in NO_END:
                out.append(cur); cur = ''
            depth += 1
        cur += ch
        if ch in '）)」』】〕｝}〉》':
            depth = max(0, depth - 1)
        nxt = t[i + 1] if i + 1 < len(t) else ''
        if not nxt or depth:
            continue
        brk = False
        if ch in '、。，,!！?？' and nxt not in NO_START:
            brk = True
        elif ch in '）)」』】' and nxt not in NO_START and kind(nxt) != 'h':
            brk = True
        elif ch in PARTICLES and i > 0 and kind(t[i - 1]) != 'h' and kind(nxt) in 'cka':
            brk = True
        if brk:
            out.append(cur); cur = ''
    if cur:
        out.append(cur)
    merged = []   # 1文字だけのかたまり(「お」など)は次とつなげる
    for p in out:
        if merged and len(merged[-1]) == 1:
            merged[-1] += p
        else:
            merged.append(p)
    return merged


def width(t, f):
    return sum(f.getlength(ch) for ch in t)


def split_chars(p, f, maxw):
    """長すぎるかたまりを文字で分ける(行頭禁止の文字は前の行にぶら下げる)"""
    lines, cur = [], ''
    for ch in p:
        if cur and width(cur + ch, f) > maxw and ch not in NO_START:
            lines.append(cur); cur = ''
        cur += ch
    return lines + ([cur] if cur else [])


def best_lines(t, f, maxw, maxlines):
    maxw = maxw * S
    ps = []
    for p in phrases(t):
        ps += split_chars(p, f, maxw) if width(p, f) > maxw else [p]
    n = len(ps)
    for k in range(1, maxlines + 1):
        if k > n:
            break
        # ps を k 行に分けて、いちばん長い行が短くなる分け方
        best = None
        def rec(start, k, acc):
            nonlocal best
            if k == 1:
                line = ''.join(ps[start:])
                cand = acc + [line]
                m = max(width(x, f) for x in cand)
                if best is None or m < best[0]:
                    best = (m, cand)
                return
            for j in range(start + 1, n - k + 2):
                rec(j, k - 1, acc + [''.join(ps[start:j])])
        rec(0, k, [])
        if best and best[0] <= maxw:
            return best[1]
    return None


def title_layer(t, color, maxw):
    for size, maxlines in ((64, 1), (58, 1), (64, 2), (58, 2), (52, 3), (46, 3), (40, 4)):   # 1行に入るなら1行で
        f = font('jp', size)
        lines = best_lines(t, f, maxw, maxlines)
        if lines:
            break
    else:
        f, size = font('jp', 40), 40
        lines = split_chars(t, f, maxw * S)[:4]
    lh = int(size * 1.42 * S)
    pad = size * S
    img = Image.new('RGBA', (int(maxw * S * 1.2) + pad, lh * len(lines) + size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = pad - (size * S // 2 if line[:1] in '『「（【〔' else 0)   # 行頭のカッコは半分ぶら下げて、左をそろえる
        d.text((x, int(size * S * 1.05) + i * lh), line, font=f, fill=color, anchor='ls')
    return img.crop(img.getchannel('A').getbbox())


def icon(color, px):
    m = Image.open(os.path.join(ROOT, 'img', 'site', 'logo_icon.png')).convert('RGBA').getchannel('A')
    m = m.resize((px * S, px * S), Image.LANCZOS)
    img = Image.new('RGBA', m.size, color)
    img.putalpha(m)
    return img


def tinted(path, color, maxw, maxh):
    m = Image.open(path).convert('RGBA')
    m = m.crop(m.getchannel('A').getbbox())
    r = min(maxw * S / m.width, maxh * S / m.height)
    a = m.getchannel('A').resize((int(m.width * r), int(m.height * r)), Image.LANCZOS)
    img = Image.new('RGBA', a.size, color)
    img.putalpha(a)
    return img


# ---------- チケット ----------
def ticket(bg, ink, block, stub):
    """block: 左の文字のかたまり(画像)、stub: 半券に置く [(画像, インクの上端y)] """
    W, H = 1200 * S, 630 * S
    img = Image.new('RGBA', (W, H), OUTER)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40 * S, 40 * S, 1160 * S - 1, 590 * S - 1), radius=22 * S, fill=bg)
    for y in (40, 590):
        d.ellipse(((880 - 22) * S, (y - 22) * S, (880 + 22) * S, (y + 22) * S), fill=OUTER)
    y = 70
    while y < 560:
        d.rectangle((878 * S, y * S, 883 * S - 1, min(y + 10, 560) * S - 1), fill=ink)
        y += 15
    # 左のかたまり:チケットの左端〜ミシン目のまん中、上下もまん中
    bx = int((40 + 880) / 2 * S - block.width / 2)
    by = int((40 + 590) / 2 * S - block.height / 2)
    img.alpha_composite(block, (bx, by))
    for el, top in stub:
        img.alpha_composite(el, (int(1019.5 * S - el.width / 2), int(top * S)))
    return img.convert('RGB').resize((1200, 630), Image.LANCZOS)


def stub_head(ink):
    return [(text_layer([('ADMIT ONE', font('cn', 36), 36 * .08)], ink), 99),
            (text_layer([('入場券', font('jp', 22), 22 * .4)], ink), 141)]


def label(en, ja, ink):
    parts = [(en, font('cn', 30), 30 * .16)]
    if ja:
        parts.append((ja, font('jp', 22), 22 * .2))
    return text_layer(parts, ink)


def stack(layers, gaps):
    w = max(l.width for l in layers)
    h = sum(l.height for l in layers) + sum(g * S for g in gaps)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    y = 0
    for i, l in enumerate(layers):
        img.alpha_composite(l, (0, y))
        y += l.height + (gaps[i] * S if i < len(gaps) else 0)
    return img


def news_card(n, games):
    g = related_game(n, games)
    bg, ink = TICKET.get(g['key'], (g.get('main'), g.get('accent'))) if g else DEFAULT
    cat_en = str(n.get('cat_en') or 'News').upper()
    block = stack([label('NEWS', str(n.get('cat_ja') or ''), ink),
                   title_layer(str(n.get('text_ja') or '').strip(), ink, 680)], [34])
    d = str(n.get('date') or '').strip().replace('-', '.').replace('/', '.')
    ym, day = (d[:7], d[8:10]) if len(d) >= 10 else (d, '')
    stub = stub_head(ink) + [
        (text_layer([(ym, font('cn', 26), 26 * .16)], ink), 222),
        (text_layer([(day, font('cn', 150), 0)], ink), 269),
        (icon(ink, 64), 430),
        (text_layer([('PandaKinema.com', font('cn', 24), 24 * .06)], ink), 515)]
    return ticket(bg, ink, block, stub)


def tool_card(name, logo, sub, bg, ink):
    title = tinted(logo, ink, 680, 120) if logo else title_layer(name, ink, 680)
    layers, gaps = [label('PLAY & TOOLS', '', ink), title], [34]
    if sub:
        layers.append(text_layer([(sub, font('jp', 24), 0)], ink)); gaps.append(30)
    stub = stub_head(ink) + [(icon(ink, 112), 279),
                             (text_layer([('PandaKinema.com', font('cn', 26), 26 * .06)], ink), 513)]
    return ticket(bg, ink, stack(layers, gaps), stub)


# ---------- 共有ページ ----------
def page(n):
    e = lambda v: html.escape(str(v or ''), quote=True)
    nid, to = news_id(n), target_url(n)
    title = str(n.get('text_ja') or '').strip()
    desc = str(n.get('body_ja') or '').strip() or title
    img = SITE_URL + 'img/share/news/%s.png' % nid
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | パンダキネマ</title>
<meta name="robots" content="noindex">
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="パンダキネマ">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(news_url(n))}">
<meta property="og:image" content="{e(img)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{e(to)}">
<meta http-equiv="refresh" content="0; url={e(to)}">
<script>location.replace({json.dumps(to)})</script>
<link rel="icon" href="/favicon.ico" sizes="any">
</head><body style="margin:0;background:#1b2228;color:#f3f2ee;font-family:sans-serif"><p style="padding:24px"><a href="{e(to)}" style="color:#fff5d7">{e(title)}</a></p></body></html>
'''


def build_news():
    news, games = load('news'), load('games')
    os.makedirs(CARD_DIR, exist_ok=True)
    made = 0
    for n in news:
        if not str(n.get('text_ja') or '').strip():
            continue
        nid = news_id(n)
        png = os.path.join(CARD_DIR, nid + '.png')
        if not os.path.exists(png):
            news_card(n, games).save(png, optimize=True)
            made += 1
        d = os.path.join(PAGE_DIR, nid)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(n))
    print('ニュースの共有カード:', len(news), '件(新しく作った画像', made, '枚)')


def build_tools():
    share = os.path.join(ROOT, 'img', 'share')
    for t in load('tools'):
        if t['key'] == 'moji':
            out = 'ogp_bibilu-moji_ticket.png'
        elif t['key'] == 'mockmaker':
            out = 'ogp_card-mock-maker_ticket.png'
        else:
            continue
        logo = os.path.join(ROOT, t['title_image']) if t.get('title_image') else None
        tool_card(t['name'], logo, t.get('intro_ja'), t.get('main') or DEFAULT[0], t.get('accent') or DEFAULT[1]).save(os.path.join(share, out), optimize=True)
        print(out)


if __name__ == '__main__':
    if '--tools' in sys.argv:
        build_tools()
    else:
        build_news()
