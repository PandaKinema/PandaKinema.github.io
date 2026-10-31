# パンダキネマ トップページを組み立てる
# content/*.yml(ニュース・作品・動画など)と build/top_template.html から index.html を作ります。
# GitHub に保存すると .github/workflows/build.yml がこれを自動で動かします。
# 手元で動かすとき:  pip install pyyaml pillow  →  python build/build.py
import html as H, os, re, sys
import news_cards   # ニュースの共有カード(build/news_cards.py)
import yaml
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import media

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = ROOT          # サイトの一番上(2026-10 に new/ から移動)
IMG_DIR = os.path.join(OUT_DIR, 'img')
SITE_URL = 'https://pandakinema.com/'
e = H.escape

def load(name):
    with open(os.path.join(ROOT, 'content', name + '.yml'), encoding='utf-8') as f:
        return yaml.safe_load(f) or []

def L(ja, en):
    ja = ja or ''; en = en or ja
    return '{{L:%s|%s}}' % (ja, en)

def T(ja, en):   # 編集画面で入れた文。改行をそのまま反映する
    br = lambda t: e(str(t or '')).strip().replace('\r\n', '\n').replace('\n', '<br>')
    ja = br(ja); en = br(en) or ja
    return '<span lang="ja">%s</span><span lang="en">%s</span>' % (ja, en)

def img(v):
    """画像の欄の値(img/trico/foo.png、foo.png など)を img からの場所に(フォルダが違っても名前で見つける)"""
    return media.path(v)

def size(v):
    with Image.open(os.path.join(IMG_DIR, img(v))) as im:
        return im.size

def bust(html, dirs):
    """画像のURLに中身から作った番号(?v=…)を付ける。同じ名前で差し替えても、ブラウザが古い画像を出さない"""
    import hashlib
    cache = {}
    def v(m):
        f = os.path.join(dirs[m.group(1)], m.group(2))
        if f not in cache:
            cache[f] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8] if os.path.isfile(f) else ''
        return m.group(0) + ('?v=' + cache[f] if cache[f] else '')
    pre = '|'.join(re.escape(k) for k in sorted(dirs, key=len, reverse=True))
    return re.sub(r'(?<![\w/.])(%s)([\w.\-/]+\.(?:png|webp|jpg|jpeg|gif|svg|mp4))(?![?\w])' % pre, v, html)

def ext(u):
    return ' target="_blank" rel="noopener"' if (u or '').startswith('http') else ''

TRI = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='92' height='160'%3E%3Crect width='92' height='160' fill='%23fbc500'/%3E%3Cpolygon points='0,80 46,0 92,80' fill='%23fdd000'/%3E%3Cpolygon points='-46,160 0,80 46,160' fill='%23fdd000'/%3E%3Cpolygon points='46,160 92,80 138,160' fill='%23fdd000'/%3E%3C/svg%3E\") center/92px 160px"
AR = '<b class="ar" aria-hidden="true">▶︎</b>'

SITE = load('site')
GAMES = load('games')
NEWS = load('news')
VIDEOS = load('videos')
TOOLS = load('tools')
BANNERS = [b if isinstance(b, dict) else {'key': b} for b in load('banners')]
CAT_EN = {c['name']: c.get('name_en') for c in (load('categories') or []) if c.get('name')}
GAME_NAME = {g['key']: g['name'] for g in GAMES}

COLOR_NAMES = {'main': 'メインカラー', 'accent': 'アクセントカラー', 'white': '白', 'black': '黒', 'original': 'ロゴ画像の色のまま'}
def col(g, sel, default='accent'):
    """色の欄(メイン・アクセント・白・黒)を色コードに。'original' は空(画像の色のまま)"""
    sel = str(sel or default).strip()
    if sel.startswith('#'):
        return sel
    return {'main': g.get('main') or '#163f53', 'accent': g.get('accent') or '#ffffff',
            'white': '#ffffff', 'black': '#000000', 'original': ''}.get(sel, g.get('accent')) or ''
def lum(c):
    c = str(c).lstrip('#'); f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, gg, b = (f(int(c[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return .2126 * r + .7152 * gg + .0722 * b
def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)
def MAIN(g):   # カード・バナーの背景(編集画面の「背景の色」。空ならメインカラー)
    return col(g, g.get('bg') or 'main')
def ACC(g):    # 帯・人数〜年齢の下地・文字:背景がメインならアクセント、アクセントならメイン、白・黒なら読みやすい方
    sel = str(g.get('bg') or 'main')
    if sel in ('main', 'accent'):
        return col(g, 'accent' if sel == 'main' else 'main')
    bg = MAIN(g)
    return max((col(g, 'main'), col(g, 'accent')), key=lambda c: contrast(c, bg))

def spec(g):
    return (str(g.get('players', '')), str(g.get('time', '')), str(g.get('age', '')))
def spec_pill(s, bg, fg):
    return '<span class="pill" style="--pc:%s;--pt:%s">%s{{L:人| players}} / %s{{L:分| min}} / %s{{L:歳から|+}}</span>' % (bg, fg, s[0], s[1], s[2])
def spec_line(s):
    return '%s{{L:人| players}} / %s{{L:分| min}} / %s{{L:歳から|+}}' % s
def tlogo(g, cls, lc=None):   # ロゴを好きな色に塗る(マスク)。色が空ならロゴ画像の色のまま
    if not g.get('logo'):   # ロゴがない(ツールでタイトル画像もない)ときは名前を文字で
        return '<span class="%s tool-name">%s</span>' % (cls, e(g['name']))
    w, h = size(g['logo'])
    lc = col(g, g.get('logo_color'), 'accent') if lc is None else lc
    if not lc:
        return '<img class="%s" src="img/%s" alt="%s" width="%d" height="%d">' % (cls, img(g['logo']), e(g['name']), w, h)
    return '<span class="%s" role="img" aria-label="%s" style="--lg:url(img/%s);aspect-ratio:%d/%d;--lc:%s"></span>' % (cls, e(g['name']), img(g['logo']), w, h, lc)
def btns(g, card=False):
    """▶見る ▶BOOTHで購入。作品ページが空なら、バナーではカードを開き、カードでは薄く表示。BOOTHが空ならサークルのBOOTH"""
    b = ''
    if g.get('page'):
        b += '<a class="wb" href="%s"%s>%s%s</a>' % (e(g['page']), ext(g['page']), AR, L('見る', 'View'))
    elif card:
        b += '<span class="wb off" title="準備中">%s%s</span>' % (AR, L('見る', 'View'))
    else:
        b += '<label class="wb" for="c-%s">%s%s</label>' % (g['key'], AR, L('見る', 'View'))
    booth = g.get('booth') or SITE['booth']
    b += '<a class="wb" href="%s" target="_blank" rel="noopener">%s%s</a>' % (e(booth), AR, L('BOOTHで購入', 'Buy on BOOTH'))
    return b
def meta(g):   # バナー用:「2〜3人・10〜15分・6歳から」の次の行に「ジャンル:〜」
    s = spec(g)
    return '<span class="m-spec">%s{{L:人| players}}・%s{{L:分| min}}・%s{{L:歳から|+}}</span><span class="m-gen">%s%s</span>' % (
        s[0], s[1], s[2], L('ジャンル：', 'Genre: '), T(g.get('genre_ja'), g.get('genre_en')))
def date(v):
    return str(v or '').strip().replace('-', '.').replace('/', '.')
def genre(g):
    return L('ジャンル:', 'Genre: ') + T(g.get('genre_ja'), g.get('genre_en'))

def yt_id(v):   # YouTube のURLでもIDでもOK
    v = str(v or '').strip()
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})', v)
    return m.group(1) if m else v
def secs(v):   # 秒数の欄:30 / 1:05 / 空
    v = str(v if v is not None else '').strip()
    if not v:
        return None
    try:
        p = [float(x) for x in v.split(':')]
    except ValueError:
        return None
    return p[0] * 60 + p[1] if len(p) == 2 else p[0]
def span(b, yt=None):   # 動画の流す範囲(開始・終了の秒)。YouTube の URL の ?t=30 も開始として読む
    st, en = secs(b.get('start')), secs(b.get('end'))
    if st is None and yt:
        m = re.search(r'[?&#](?:t|start)=(\d+)', str(yt))
        st = float(m.group(1)) if m else None
    return st, en
def vid(v, yt=None, b=None):   # バナーで流す動画(音なし・くり返し)。mp4 か YouTube。b = 開始・終了の秒が入った欄
    st, en = span(b or {}, yt if not v else None)
    rng = ''.join(' data-%s="%g"' % (k, x) for k, x in (('start', st), ('end', en)) if x is not None)
    if v:
        return '<video class="b-vid" src="img/%s" muted loop playsinline autoplay preload="metadata" aria-hidden="true"%s></video>' % (img(v), rng)
    if yt:
        return '<div class="b-yt" data-yt="%s" aria-hidden="true"%s></div>' % (e(yt_id(yt)), rng)
    return ''
def clip(b, yt=None, v=None):   # 流す範囲が決まっていれば、その長さだけバナーを出す(秒)
    st, en = span(b or {}, yt if not v else None)
    return (en - (st or 0)) if en and en > (st or 0) else None

def tool_art(t, where):
    if t.get('image') or t.get('thumb'):
        src = t.get('image') if where == 'b' else (t.get('thumb') or t.get('image'))
        return '<img class="%s-shot" src="img/%s" alt="%sの画面">' % (where, img(src), e(t['name']))
    if t['key'] == 'moji':   # トゥーパ(体と玉)
        return '<span class="tupa%s"><img class="tb" src="img/b_tupa_body.webp" alt="トゥーパ"><img class="to" src="img/b_tupa_orb.webp" alt=""></span>' % ('' if where == 'b' else ' tl-tupa')
    return ''
def tool_title(t, cls):
    if t.get('title_image'):
        return '<img class="%s" src="img/%s" alt="%s">' % (cls, img(t['title_image']), e(t['name']))
    return '<span class="tool-name">%s</span>' % e(t['name'])
def tool_btn(t, tag='a'):   # ボタンはボードゲームと同じ「見る」
    lab = AR + L('見る', 'View')
    if tag == 'span':
        return '<span class="wb">%s</span>' % lab
    return '<a class="wb" href="%s"%s>%s</a>' % (e(t['url']), ext(t['url']), lab)

def banner(key, b=None):
    """(クラス, スタイル, 絵, 文字, ボタン, 動画)"""
    b = b or {}
    for t in TOOLS:
        if t['key'] == key:
            v = vid(t.get('video'), t.get('youtube'), b)
            art = tool_art(t, 'b') if not v else ''
            txt = '<p class="b-series"><span class="cap">PLAY &amp; TOOLS</span></p><h2 class="b-name">%s</h2><p class="b-intro">%s</p>' % (tool_title(t, 'b-mtitle'), T(t.get('intro_ja'), t.get('intro_en')))
            return 'b-tool b-' + key, 'background:%s;--fg:%s' % (MAIN(t), ACC(t)), art, txt, tool_btn(t), v
    g = [x for x in GAMES if x['key'] == key][0]
    bn = g.get('banner') or {}
    bg = MAIN(g)
    if bn.get('pattern') == 'tri':
        bg += ' ' + TRI
    if bn.get('image'):   # 背景を画像で作ったとき:パッケージは出さない
        bg = "%s url(img/%s) center/cover no-repeat" % (MAIN(g), img(bn['image']))
        art = ''
    else:
        w, h = size(g['pkg'])   # 横長のパッケージ(ミニシアター)は横長の置き方に
        art = '<img class="%s" src="img/%s" alt="%sのパッケージ">' % ('b-mini' if w > h else 'b-pkg', img(g['pkg']), e(g['name']))
    if bn.get('video') or bn.get('youtube'):
        art = ''
    intro = '<p class="b-intro">%s</p>' % T(g.get('intro_ja'), g.get('intro_en')) if g.get('intro_ja') else ''
    # 区分の行:[新作] BOARD GAME(シリーズがあれば / シリーズ名)。PLAY & TOOLS と同じ位置
    label = '%s<span class="cap">BOARD GAME%s</span>' % ('<span class="b-new"><span class="cap">NEW</span></span>' if g.get('new') else '', ' / ' + e(g['series']) if g.get('series') else '')
    txt = '<p class="b-series">%s</p><h2 class="b-name">%s</h2>%s' % (label, tlogo(g, 'b-logo'), intro)   # 人数〜ジャンルはバナーには出さない(カードと作品ページに)
    return 'b-' + key, 'background:%s;--fg:%s' % (bg, ACC(g)), art, txt, btns(g), vid(bn.get('video'), bn.get('youtube'), bn)

def clip_of(key):   # 作品の「バナー」欄に入れた動画の範囲
    g = next((x for x in GAMES + TOOLS if x['key'] == key), {})
    bn = g.get('banner') or {}
    return clip(bn, bn.get('youtube'), bn.get('video'))

def card(x, tool=False):
    """閉じたカード(縦長の画像)と開いたカード(色と画像から作る)。ボードゲームもツールも同じ形"""
    group = 'tools' if tool else 'board'
    cid = 'c-%s' % x['key']
    new = '<span class="c-new"><span class="cap">NEW</span></span>' if x.get('new') else ''
    if x.get('front'):
        face = '<img src="img/%s" alt="%s" loading="lazy">' % (img(x['front']), e(x['name']))
    else:   # 閉じたカードの画像がまだないツール:絵とタイトルで仮のカード
        face = '<span class="c-auto">%s<span class="c-auto-t">%s</span></span>' % (tool_art(x, 'tl'), tool_title(x, 'tl-title'))
    if tool:
        shot = x.get('image') or x.get('thumb')
        art = ('<img class="o-pkg wide" src="img/%s" alt="" loading="lazy">' % img(shot)) if shot else '<span class="o-art">%s</span>' % tool_art(x, 'b')
        lg = dict(x, logo=x.get('title_image') or '', logo_color=x.get('logo_color') or 'original')
        info = '<p class="o-intro">%s</p>' % T(x.get('intro_ja'), x.get('intro_en')) if x.get('intro_ja') else ''
        bt = tool_btn(x)
    else:
        w, h = size(x['pkg'])
        art = '<img class="o-pkg%s" src="img/%s" alt="" loading="lazy">' % (' wide' if w > h else '', img(x['pkg']))
        lg = x
        info = '%s<p class="o-genre">%s</p>' % (spec_pill(spec(x), ACC(x), MAIN(x)), genre(x))
        bt = btns(x, card=True)
    return ('        <li class="card" style="--c1:%s;--c2:%s"><input class="sr" type="radio" name="%s" id="%s">'
            '<label class="c-face" for="%s">%s%s</label>'
            '<div class="c-open">%s<div class="o-txt">%s%s<div class="o-btns">%s</div></div>'
            '<label class="o-x" for="%s-x" aria-label="とじる"></label></div></li>') % (
        ACC(x), MAIN(x), group, cid, cid, face, new, art, tlogo(lg, 'o-logo'), info, bt, group)

def render():
    slide = int(SITE.get('slide_seconds') or 7)
    n = len(BANNERS); total = n * slide
    radios = ''.join('<input class="br sr" type="radio" name="bn" id="br%d" aria-label="%d枚目">' % (i + 1, i + 1) for i in range(n))
    slides = []; durs = {}
    for i, b in enumerate(BANNERS):
        if b.get('key') == 'brand':   # 看板バナー:パンダキネマの英字ロゴ
            copy = T(SITE.get('brand_copy_ja') or str(SITE.get('about_ja') or '').split('\n')[0], SITE.get('brand_copy_en') or str(SITE.get('about_en') or '').split('\n')[0])
            slides.append('      <article class="slide s%d b-brand" style="--d:%ds"><img class="bb-logo" src="img/%s" alt="PANDA KINEMA"%s>%s<div class="bb-btns"><a class="wb" href="#board"><b class="ar" aria-hidden="true">▶︎</b>%s</a><a class="wb" href="#about"><b class="ar" aria-hidden="true">▶︎</b>%s</a></div></article>' % (
                i + 1, i * slide, img(SITE.get('brand_logo') or 'logo_en.png'), '' if i == 0 else ' loading="lazy"',
                ('<img class="bb-copyimg" src="img/%s" alt="%s">' % (img(SITE['brand_copy_image']), e(str(SITE.get('brand_copy_ja') or '')))) if SITE.get('brand_copy_image') else '<p class="bb-copy">%s</p>' % copy, L('作品を見る', 'Our games'), L('パンダキネマについて', 'About us')))
            continue
        if not b.get('key') and (b.get('image') or b.get('video') or b.get('youtube')):   # key なし:自分で作ったバナー画像・動画だけを出す
            alt = e(b.get('alt') or '')
            pic = vid(b.get('video'), b.get('youtube')) if (b.get('video') or b.get('youtube')) else '<img class="b-img" src="img/%s" alt="%s"%s>' % (img(b['image']), alt, '' if i == 0 else ' loading="lazy"')
            link = '<a class="b-link" href="%s"%s aria-label="%s"></a>' % (e(b['link']), ext(b['link']), alt) if b.get('link') else ''
            slides.append('      <article class="slide s%d b-custom" style="--d:%ds;background:%s">%s%s</article>' % (i + 1, i * slide, e(b.get('bg') or '#000'), pic, link))
            continue
        cls, bg, art, txt, bt, vd = banner(b['key'], b)
        if b.get('video') or b.get('youtube'):   # key と一緒に入れた動画は、その作品のバナーの背景で流す
            vd, art = vid(b.get('video'), b.get('youtube'), b), ''
        durs[i] = clip(b, b.get('youtube'), b.get('video')) or clip_of(b['key'])
        slides.append('      <article class="slide s%d %s%s" style="--d:%ds;%s%s">%s<div class="b-art">%s</div><div class="b-in">%s<div class="b-btns">%s</div></div></article>' % (
            i + 1, cls, ' has-vid' if vd else '', i * slide, e(bg), (';--dur:%gs' % durs[i]) if durs[i] else '', vd, art, txt, bt))
    bars = ''.join('<label for="br%d" style="--d:%ds%s" aria-label="%d枚目"><i></i></label>' % (i + 1, i * slide, (';--dur:%gs' % durs[i]) if durs.get(i) else '', i + 1) for i in range(n))
    w = 100.0 / n; fd = 0.8 / total * 100
    cyc = ('    @keyframes cyc{0%%{opacity:0;visibility:hidden;z-index:1}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:0;visibility:hidden;z-index:1}100%%{opacity:0;visibility:hidden;z-index:1}}\n'
           '    @keyframes fill{0%%{width:0}%.3f%%{width:100%%}%.3f%%,100%%{width:0}}\n'
           '    @keyframes kb{0%%{scale:1}%.3f%%{scale:1.04}100%%{scale:1.04}}') % (fd, w, w + fd, w, w + .001, w + fd)
    pick = '\n'.join('    .hero:has(#br%d:checked) .s%d{opacity:1;visibility:visible;z-index:2}\n    .hero:has(#br%d:checked) .bars label:nth-child(%d) i{width:100%%}' % (i + 1, i + 1, i + 1, i + 1) for i in range(n))
    cats = [(str(x.get('cat_ja') or ''), str(CAT_EN.get(x.get('cat_ja')) or x.get('cat_en') or x.get('cat_ja') or '')) for x in NEWS]
    catw = max([len(j) for j, _ in cats] + [len(en) * .62 for _, en in cats] + [2])   # いちばん長いカテゴリの幅(文字数)
    news = '\n'.join('        <li><a href="#n%d" data-nm="n%d"><time>%s</time><span class="cat">%s</span><span class="t">%s</span></a></li>' % (
        k + 1, k + 1, e(date(x['date'])), T(x.get('cat_ja'), CAT_EN.get(x.get('cat_ja')) or x.get('cat_en')), T(x.get('text_ja'), x.get('text_en'))) for k, x in enumerate(NEWS))
    modals = '\n'.join(
        '  <div class="nm" id="n%d" role="dialog" aria-modal="true" aria-labelledby="n%dt"><a class="nm-bg" href="#news" aria-label="とじる"></a><div class="nm-box">'
        '<p class="nm-meta"><span class="cat">%s</span><time>%s</time></p><h3 class="nm-t" id="n%dt">%s</h3>%s%s<a class="nm-x" href="#news" aria-label="とじる"></a></div></div>' % (
            k + 1, k + 1, T(x.get('cat_ja'), CAT_EN.get(x.get('cat_ja')) or x.get('cat_en')), e(date(x['date'])), k + 1, T(x.get('text_ja'), x.get('text_en')),
            '<div class="nm-body">%s</div>' % T(x.get('body_ja'), x.get('body_en')) if x.get('body_ja') else '',
            '<p class="nm-link"><a class="wb" href="%s"%s>%s%s</a></p>' % (e(x['link']), ext(x['link']), AR, L('リンクを開く', 'Open link')) if x.get('link') else '')
        for k, x in enumerate(NEWS))
    cards = [card(g) for g in GAMES]
    vids = '\n'.join('        <li><button class="vid" type="button" data-yt="%s" aria-label="%s"><img src="img/%s" alt="" loading="lazy"><span class="v-play" aria-hidden="true">▶</span><span class="v-t"><b>%s</b><small>%s</small></span>%s</button></li>'
                     % (e(yt_id(v.get('youtube'))), e(GAME_NAME.get(v.get('work')) or v.get('title') or ''), img(v['poster']), e(GAME_NAME.get(v.get('work')) or v.get('title') or ''), T(v.get('kind_ja'), v.get('kind_en')),
                        '' if v.get('youtube') else '<span class="v-soon">%s</span>' % L('準備中', 'Coming soon')) for v in VIDEOS)
    tools = '\n'.join(card(t, tool=True) for t in TOOLS)
    tools += '\n        <li class="card soon"><span>COMING SOON</span></li>'

    ogp = ''
    if SITE.get('ogp_image'):
        ogp = '  <meta property="og:url" content="%s">\n  <meta property="og:image" content="%simg/%s">' % (SITE_URL, SITE_URL, img(SITE['ogp_image']))
    v = dict(catw='%.2f' % catw, total=total, radios=radios, bars=bars, cyc=cyc, pick=pick, slides='\n'.join(slides), slide=slide, news=news, cards='\n'.join(cards), vids=vids, tools=tools,
             booth=e(SITE['booth']), x=e(SITE['x']), gm=e(SITE['gamemarket']), mail=e(SITE['mail']), note=e(SITE['note']), member_x=e(SITE['member_x']),
             about=T(SITE.get('about_ja'), SITE.get('about_en')), ogp=ogp, modals=modals,
             site_description=e(''.join(l.strip() for l in str(SITE.get('about_ja') or '').split('\n')) or 'パンダキネマ:世界観から遊びまでを1つの作品として制作する創作サークル。'),
             header_logo=img(SITE.get('header_logo') or 'brand.png'), member_handle=e('@' + (re.search(r'(?:x|twitter)\.com/([\w]+)', str(SITE.get('member_x') or '')) or re.search(r'(.*)', 'panda_kinema')).group(1)), about_copy=('<img class="a-copy" src="img/%s" alt="%s" loading="lazy">' % (img(SITE['brand_copy_image']), e(str(SITE.get('brand_copy_ja') or '')))) if SITE.get('brand_copy_image') else '', about_logo=img(SITE.get('about_logo') or 'logo_pk_kana.png'), icon=img(SITE.get('icon') or 'pk_icon.png'),
             member_label=e(SITE.get('member_label') or 'MEMBER'), member_name=T(SITE.get('member_name_ja') or 'ゐするぎ', SITE.get('member_name_en') or 'Isurugi'),
             member_role=e(SITE.get('member_role') or ''),
             member_bio=('<p class="a-bio">%s</p>' % T(SITE.get('member_bio_ja'), SITE.get('member_bio_en'))) if SITE.get('member_bio_ja') else '',
             member_ava=('<img src="img/%s" alt="">' % img(SITE['member_icon'])) if SITE.get('member_icon') else '<i></i>')
    s = open(os.path.join(ROOT, 'build', 'top_template.html'), encoding='utf-8').read()
    for _ in range(2):
        s = re.sub(r'\{\{(?!img:|L:)(\w+)\}\}', lambda m: str(v[m.group(1)]), s)
    s = re.sub(r'\{\{L:(.*?)\|(.*?)\}\}', r'<span lang="ja">\1</span><span lang="en">\2</span>', s, flags=re.S)
    s = re.sub(r'\{\{img:([\w.\-/]+)\}\}', r'img/\1', s)
    # 名前だけで書いた画像(img/foo.png)を、フォルダの中の場所に
    s = re.sub(r'(?<![\w/.])img/([\w.\-/]+\.(?:png|webp|jpg|jpeg|gif|svg|mp4))', lambda m: 'img/' + media.path(m.group(1)), s)
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)[:5]
    # 使っている画像がそろっているか
    missing = sorted({m for m in re.findall(r'img/([\w.\-/]+\.(?:png|webp|jpg|jpeg|gif|svg))', s) if not os.path.exists(os.path.join(IMG_DIR, m))})
    if missing:
        sys.exit('見つからない画像があります: ' + ', '.join(missing))
    return s

def colors():
    """色見本:編集画面では色コードしか見えないので、今の設定の色を並べたページを作る(colors.html)"""
    def sw(label, c):
        c = str(c or '').strip()
        if not c:
            return '<div class="sw none"><i></i><b>%s</b><code>(画像の色のまま)</code></div>' % label
        return '<div class="sw"><i style="background:%s"></i><b>%s</b><code>%s</code></div>' % (e(c), label, e(c))
    rows = []
    for g in GAMES:
        c = lambda v, d: col(g, v, d)
        name = lambda v, d: COLOR_NAMES.get(str(v or d), str(v or d))
        prev = '<div class="pv" style="background:%s"><span style="background:%s;color:%s">%s人 / %s分 / %s歳から</span><small style="color:%s">ジャンル:%s</small></div>' % (
            e(MAIN(g)), e(ACC(g)), e(MAIN(g)), *map(e, spec(g)), e(ACC(g)), e(g.get('genre_ja') or ''))
        keys = sw('メインカラー(背景)', g.get('main')) + sw('アクセントカラー(帯・文字)', g.get('accent'))
        uses = sw('ロゴ(%s)' % name(g.get('logo_color'), 'accent'), c(g.get('logo_color'), 'accent'))
        rows.append('<section><h2>%s <small>%s</small></h2><div class="grid">%s%s</div><p class="lbl">開いたカードの見え方</p>%s</section>' % (
            e(g['name']), e(g['key']), keys, uses, prev))
    for t in TOOLS:
        rows.append('<section><h2>%s <small>%s</small></h2><div class="grid">%s%s</div></section>' % (e(t['name']), e(t['key']), sw('メインカラー(背景)', t.get('main')), sw('アクセントカラー(文字)', t.get('accent'))))
    return """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>色見本 | PANDA KINEMA</title>
<style>body{margin:0;padding:24px 16px 48px;background:#1b2228;color:#f3f2ee;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif}main{max-width:900px;margin:auto}
h1{font-size:22px}p.note{color:#9aa3a9;font-size:13px;line-height:1.8}section{margin:22px 0;padding:18px;border:1px solid #3a464f;border-radius:12px;background:#222b32}h2{margin:0 0 12px;font-size:17px}h2 small{color:#9aa3a9;font-weight:400}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}.sw{display:grid;grid-template-columns:40px 1fr;grid-template-rows:auto auto;column-gap:10px;align-items:center}
.sw i{grid-row:1/3;width:40px;height:40px;border-radius:8px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25)}.sw.none i{background:repeating-linear-gradient(45deg,#3a464f 0 4px,#2a333a 4px 8px)}.sw b{font-size:13px}.sw code{font-size:13px;color:#cdd2d4}
.lbl{margin:14px 0 6px;font-size:12px;color:#9aa3a9}.pv{display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px;border-radius:10px}.pv span{padding:.2em .9em;border-radius:999px;font-weight:800;font-size:13px}.pv small{font-weight:800}</style></head>
<body><main><h1>色見本</h1><p class="note">編集画面の色コードが、実際に何色かを確かめるためのページです。保存して1〜2分すると、ここも新しい色に変わります。</p>""" + ''.join(rows) + '</main></body></html>'


def post_page():
    """Xの告知文(post.html):ニュースごとに、そのままXに投稿できる文を作る。サイトからはリンクしない(編集画面から開く)"""
    import re as _re
    e = H.escape
    items = []
    for i, n in enumerate(NEWS or []):
        link = str(n.get('link') or '').strip()
        url = news_cards.news_url(n)   # タイトルと日付の入ったカードが出る共有ページ(開くとリンク先へ移動)
        tags = ['パンダキネマ']
        m = _re.match(r'games/([\w-]+)/?', link)
        g = next((x for x in GAMES if m and x['key'] == m.group(1)), None)
        if not g:   # タイトルに『作品名』が入っていればその作品
            g = next((x for x in GAMES if x['name'] and (x['name'] in str(n.get('text_ja') or '') or x['name'].replace(' ', '') in str(n.get('text_ja') or ''))), None)
        if g:
            tags += [t for t in _re.split(r'[\s,、#]+', str(g.get('hashtag') or '')) if t] or [_re.sub(r'[^\w]', '', g['name'])]
        cat = str(n.get('cat_ja') or '').strip()
        body = str(n.get('body_ja') or '').strip()
        text = ('【%s】' % cat if cat else '') + str(n.get('text_ja') or '').strip() + ('\n\n' + body if body else '')
        items.append(dict(date=date(n.get('date')), text=text, url=url, tags=' '.join('#' + t for t in tags)))
    cards = ''.join('<section class="it"><p class="d">%s</p><textarea rows="6" data-i="%d">%s</textarea><p class="u">%s</p><p class="row"><span class="cnt"></span><button type="button" class="cp">コピー</button><a class="go" target="_blank" rel="noopener">Xに投稿する</a></p></section>' % (
        e(x['date']), i, e(x['text'] + '\n\n' + x['url'] + '\n' + x['tags']), e('リンクはURLとして文の中に入っています(Xでは23文字分)')) for i, x in enumerate(items))
    return """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Xの告知文 | PANDA KINEMA</title>
<link rel="icon" href="/favicon.ico" sizes="any">
<style>body{margin:0;padding:24px 16px 48px;background:#1b2228;color:#f3f2ee;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif}main{max-width:720px;margin:auto}
h1{font-size:22px}.note{color:#9aa3a9;font-size:13px;line-height:1.8}.it{margin:18px 0;padding:16px;border:1px solid #3a464f;border-radius:12px;background:#222b32}.d{margin:0 0 8px;font-size:13px;color:#9aa3a9}
textarea{box-sizing:border-box;width:100%;padding:10px 12px;border:1px solid #3a464f;border-radius:8px;background:#151b20;color:#f3f2ee;font-family:inherit;font-size:15px;line-height:1.7;resize:vertical}.u{display:none}
.row{display:flex;align-items:center;gap:10px;margin:10px 0 0}.cnt{margin-right:auto;font-size:12px;color:#9aa3a9}.cnt.over{color:#ff6b6b;font-weight:700}
button,.go{display:inline-flex;align-items:center;height:36px;padding:0 16px;border:1px solid #3a464f;border-radius:999px;background:none;color:#f3f2ee;font-family:inherit;font-size:13px;font-weight:700;white-space:nowrap;text-decoration:none;cursor:pointer}.go{border:0;background:#fff;color:#000}</style></head>
<body><main><h1>Xの告知文</h1><p class="note">ニュースごとに、Xに投稿する文を用意しています(新しい順)。文はここで直してから「Xに投稿する」を押すと、Xの投稿画面が開きます。ニュースを保存して1〜2分すると、ここにも出ます。<br>文の中のURLは、そのニュースの共有用ページです。Xに貼ると、タイトルと日付の入ったチケットのカードが出ます(開いた人はニュースのリンク先へ移動します)。<br>このページはサイトからはリンクしていません(検索にも出ません)。</p>""" + cards + """</main>
<script>
function w(t){var n=0;t=t.replace(/https?:\\/\\/\\S+/g,function(){n+=23;return""});for(var c of t){n+=/[\\u1100-\\uffff]/.test(c)&&!/[\\u2000-\\u200d\\u2010-\\u201f\\u2032-\\u2037]/.test(c)?2:1}return n}
document.querySelectorAll(".it").forEach(function(s){var ta=s.querySelector("textarea"),go=s.querySelector(".go"),cn=s.querySelector(".cnt");
function up(){var n=w(ta.value);cn.textContent="あと "+Math.floor((280-n)/2)+" 文字くらい";cn.classList.toggle("over",n>280);go.href="https://x.com/intent/post?text="+encodeURIComponent(ta.value)}
ta.addEventListener("input",up);up();
s.querySelector(".cp").addEventListener("click",function(){navigator.clipboard.writeText(ta.value);this.textContent="コピーしました";var b=this;setTimeout(function(){b.textContent="コピー"},1500)})});
</script></body></html>"""

if __name__ == '__main__':
    out = os.path.join(OUT_DIR, 'index.html')
    open(out, 'w', encoding='utf-8').write(bust(render(), {'img/': IMG_DIR}))
    print(out, os.path.getsize(out))
    open(os.path.join(OUT_DIR, 'colors.html'), 'w', encoding='utf-8').write(colors())
    open(os.path.join(OUT_DIR, 'post.html'), 'w', encoding='utf-8').write(post_page())
