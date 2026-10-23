# パンダキネマ トップページを組み立てる
# content/*.yml(ニュース・作品・動画など)と build/top_template.html から new/index.html を作ります。
# GitHub に保存すると .github/workflows/build.yml がこれを自動で動かします。
# 手元で動かすとき:  pip install pyyaml pillow  →  python build/build.py
import html as H, os, re, sys
import yaml
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'new')          # トップと入れ替えるときはここを変える
IMG_DIR = os.path.join(OUT_DIR, 'img')
SITE_URL = 'https://pandakinema.github.io/new/'
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
    """画像の欄の値(img/foo.png、/new/img/foo.png、foo.png など)を img/ 以下の名前にそろえる"""
    v = (v or '').strip().lstrip('/')
    for pre in ('new/img/', 'img/'):
        if v.startswith(pre):
            v = v[len(pre):]
    return v

def size(v):
    with Image.open(os.path.join(IMG_DIR, img(v))) as im:
        return im.size

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

def spec(g):
    return (str(g.get('players', '')), str(g.get('time', '')), str(g.get('age', '')))
def spec_pill(s, bg, fg):
    return '<span class="pill" style="--pc:%s;--pt:%s">%s{{L:人| players}} / %s{{L:分| min}} / %s{{L:歳から|+}}</span>' % (bg, fg, s[0], s[1], s[2])
def spec_line(s):
    return '%s{{L:人| players}} / %s{{L:分| min}} / %s{{L:歳から|+}}' % s
def tlogo(g, cls, lc=None):   # ロゴを好きな色に塗る(マスク)。色が空ならロゴ画像の色のまま
    w, h = size(g['logo'])
    if not (lc or g.get('logo_color')):
        return '<img class="%s" src="img/%s" alt="%s" width="%d" height="%d">' % (cls, img(g['logo']), e(g['name']), w, h)
    return '<span class="%s" role="img" aria-label="%s" style="--lg:url(img/%s);aspect-ratio:%d/%d;--lc:%s"></span>' % (cls, e(g['name']), img(g['logo']), w, h, lc or g['logo_color'])
def btns(g, card=False):
    """▶詳しく見る ▶BOOTHで購入。作品ページが空なら、バナーではカードを開き、カードでは薄く表示。BOOTHが空ならサークルのBOOTH"""
    b = ''
    if g.get('page'):
        b += '<a class="wb" href="%s"%s>%s%s</a>' % (e(g['page']), ext(g['page']), AR, L('詳しく見る', 'More info'))
    elif card:
        b += '<span class="wb off" title="準備中">%s%s</span>' % (AR, L('詳しく見る', 'More info'))
    else:
        b += '<label class="wb" for="c-%s">%s%s</label>' % (g['key'], AR, L('詳しく見る', 'More info'))
    booth = g.get('booth') or SITE['booth']
    b += '<a class="wb" href="%s" target="_blank" rel="noopener">%s%s</a>' % (e(booth), AR, L('BOOTHで購入', 'Buy on BOOTH'))
    return b
def meta(g):   # バナー用:2〜3人・10〜15分・6歳から・ジャンル(下地なし)
    s = spec(g)
    return '%s{{L:人| players}}・%s{{L:分| min}}・%s{{L:歳から|+}}・%s' % (s[0], s[1], s[2], T(g.get('genre_ja'), g.get('genre_en')))
def date(v):
    return str(v or '').strip().replace('-', '.').replace('/', '.')
def genre(g):
    return L('ジャンル:', 'Genre: ') + T(g.get('genre_ja'), g.get('genre_en'))

def yt_id(v):   # YouTube のURLでもIDでもOK
    v = str(v or '').strip()
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})', v)
    return m.group(1) if m else v
def vid(v, yt=None):   # バナーで流す動画(音なし・くり返し)。mp4 か YouTube
    if v:
        return '<video class="b-vid" src="img/%s" muted loop playsinline autoplay preload="metadata" aria-hidden="true"></video>' % img(v)
    if yt:
        return '<div class="b-yt" data-yt="%s" aria-hidden="true"></div>' % e(yt_id(yt))
    return ''

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
def tool_btn(t, tag='a'):
    lab = AR + L(t.get('button_ja') or 'あそぶ', t.get('button_en') or 'Play')
    if tag == 'span':
        return '<span class="wb">%s</span>' % lab
    return '<a class="wb" href="%s"%s>%s</a>' % (e(t['url']), ext(t['url']), lab)

def banner(key):
    """(クラス, スタイル, 絵, 文字, ボタン, 動画)"""
    for t in TOOLS:
        if t['key'] == key:
            v = vid(t.get('video'), t.get('youtube'))
            art = tool_art(t, 'b') if not v else ''
            txt = '<p class="b-series">PLAY &amp; TOOLS</p><h2 class="b-name">%s</h2><p class="b-intro">%s</p>' % (tool_title(t, 'b-mtitle'), T(t.get('intro_ja'), t.get('intro_en')))
            return 'b-tool b-' + key, 'background:%s;--fg:%s' % (t.get('bg') or '#163f53', t.get('text_color') or '#fff'), art, txt, tool_btn(t), v
    g = [x for x in GAMES if x['key'] == key][0]
    bn = g.get('banner') or {}
    bg = bn.get('bg') or g['color_face']
    if bn.get('pattern') == 'tri':
        bg += ' ' + TRI
    if bn.get('image'):   # 背景を画像で作ったとき:パッケージは出さない
        bg = "%s url(img/%s) center/cover no-repeat" % (bn.get('bg') or g['color_face'], img(bn['image']))
        art = ''
    else:
        w, h = size(g['pkg'])   # 横長のパッケージ(ミニシアター)は横長の置き方に
        art = '<img class="%s" src="img/%s" alt="%sのパッケージ">' % ('b-mini' if w > h else 'b-pkg', img(g['pkg']), e(g['name']))
    if bn.get('video') or bn.get('youtube'):
        art = ''
    intro = '<p class="b-intro">%s</p>' % T(g.get('intro_ja'), g.get('intro_en')) if g.get('intro_ja') else ''
    series = '<p class="b-series">%s</p>' % e(g['series']) if g.get('series') else ''
    txt = '%s%s<h2 class="b-name">%s</h2><p class="b-meta">%s</p>%s' % (
        '<p class="b-new">%s</p>' % L('新作', 'NEW') if g.get('new') else '', series, tlogo(g, 'b-logo', bn.get('logo_color')), meta(g), intro)
    return 'b-' + key, 'background:%s;--fg:%s' % (bg, bn.get('text_color') or '#fff'), art, txt, btns(g), vid(bn.get('video'), bn.get('youtube'))

def render():
    slide = int(SITE.get('slide_seconds') or 7)
    n = len(BANNERS); total = n * slide
    radios = ''.join('<input class="br sr" type="radio" name="bn" id="br%d" aria-label="%d枚目">' % (i + 1, i + 1) for i in range(n))
    slides = []
    for i, b in enumerate(BANNERS):
        if not b.get('key') and (b.get('image') or b.get('video') or b.get('youtube')):   # key なし:自分で作ったバナー画像・動画だけを出す
            alt = e(b.get('alt') or '')
            pic = vid(b.get('video'), b.get('youtube')) if (b.get('video') or b.get('youtube')) else '<img class="b-img" src="img/%s" alt="%s"%s>' % (img(b['image']), alt, '' if i == 0 else ' loading="lazy"')
            link = '<a class="b-link" href="%s"%s aria-label="%s"></a>' % (e(b['link']), ext(b['link']), alt) if b.get('link') else ''
            slides.append('      <article class="slide s%d b-custom" style="--d:%ds;background:%s">%s%s</article>' % (i + 1, i * slide, e(b.get('bg') or '#000'), pic, link))
            continue
        cls, bg, art, txt, bt, vd = banner(b['key'])
        if b.get('video') or b.get('youtube'):   # key と一緒に入れた動画は、その作品のバナーの背景で流す
            vd, art = vid(b.get('video'), b.get('youtube')), ''
        slides.append('      <article class="slide s%d %s%s" style="--d:%ds;%s">%s<div class="b-art">%s</div><div class="b-in">%s<div class="b-btns">%s</div></div></article>' % (
            i + 1, cls, ' has-vid' if vd else '', i * slide, e(bg), vd, art, txt, bt))
    bars = ''.join('<label for="br%d" style="--d:%ds" aria-label="%d枚目"><i></i></label>' % (i + 1, i * slide, i + 1) for i in range(n))
    w = 100.0 / n; fd = 0.8 / total * 100
    cyc = ('    @keyframes cyc{0%%{opacity:0;visibility:hidden;z-index:1}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:0;visibility:hidden;z-index:1}100%%{opacity:0;visibility:hidden;z-index:1}}\n'
           '    @keyframes fill{0%%{width:0}%.3f%%{width:100%%}%.3f%%,100%%{width:0}}\n'
           '    @keyframes kb{0%%{scale:1}%.3f%%{scale:1.04}100%%{scale:1.04}}') % (fd, w, w + fd, w, w + .001, w + fd)
    pick = '\n'.join('    .hero:has(#br%d:checked) .s%d{opacity:1;visibility:visible;z-index:2}\n    .hero:has(#br%d:checked) .bars label:nth-child(%d) i{width:100%%}' % (i + 1, i + 1, i + 1, i + 1) for i in range(n))
    news = '\n'.join('        <li><a href="#n%d" data-nm="n%d"><time>%s</time><span class="cat">%s</span><span class="t">%s</span></a></li>' % (
        k + 1, k + 1, e(date(x['date'])), T(x.get('cat_ja'), x.get('cat_en')), T(x.get('text_ja'), x.get('text_en'))) for k, x in enumerate(NEWS))
    modals = '\n'.join(
        '  <div class="nm" id="n%d" role="dialog" aria-modal="true" aria-labelledby="n%dt"><a class="nm-bg" href="#news" aria-label="とじる"></a><div class="nm-box">'
        '<p class="nm-meta"><span class="cat">%s</span><time>%s</time></p><h3 class="nm-t" id="n%dt">%s</h3>%s%s<a class="nm-x" href="#news" aria-label="とじる"></a></div></div>' % (
            k + 1, k + 1, T(x.get('cat_ja'), x.get('cat_en')), e(date(x['date'])), k + 1, T(x.get('text_ja'), x.get('text_en')),
            '<div class="nm-body">%s</div>' % T(x.get('body_ja'), x.get('body_en')) if x.get('body_ja') else '',
            '<p class="nm-link"><a class="wb" href="%s"%s>%s%s</a></p>' % (e(x['link']), ext(x['link']), AR, L('リンクを開く', 'Open link')) if x.get('link') else '')
        for k, x in enumerate(NEWS))
    cards = []
    for g in GAMES:   # 閉じたカード=縦長の画像、開いたカード=色と画像から作る(全作品同じ形)
        cid = 'c-%s' % g['key']
        w, h = size(g['pkg'])
        cards.append(('        <li class="card" style="--c1:%s;--c2:%s"><input class="sr" type="radio" name="board" id="%s">'
                      '<label class="c-face" for="%s"><img src="img/%s" alt="%s" loading="lazy">%s</label>'
                      '<div class="c-open"><img class="o-pkg%s" src="img/%s" alt="" loading="lazy"><div class="o-txt">%s%s<p class="o-genre">%s</p><div class="o-btns">%s</div></div>'
                      '<label class="o-x" for="board-x" aria-label="とじる"></label></div></li>')
                     % (g['color_band'], g['color_face'], cid, cid, img(g['front']), e(g['name']), '<span class="c-new">%s</span>' % L('新作', 'NEW') if g.get('new') else '',
                        ' wide' if w > h else '', img(g['pkg']), tlogo(g, 'o-logo'), spec_pill(spec(g), g['color_band'], g['color_face']), genre(g), btns(g, card=True)))
    vids = '\n'.join('        <li><button class="vid" type="button" data-yt="%s" aria-label="%s"><img src="img/%s" alt="" loading="lazy"><span class="v-play" aria-hidden="true">▶</span><span class="v-t"><b>%s</b><small>%s</small></span>%s</button></li>'
                     % (e(yt_id(v.get('youtube'))), e(v['title']), img(v['poster']), e(v['title']), T(v.get('kind_ja'), v.get('kind_en')),
                        '' if v.get('youtube') else '<span class="v-soon">%s</span>' % L('準備中', 'Coming soon')) for v in VIDEOS)
    tools = '\n'.join('        <li><a class="tool t-%s" href="%s"%s style="background:%s;color:%s">%s<span class="tl-t">%s%s</span></a></li>' % (
        t['key'], e(t['url']), ext(t['url']), t.get('bg') or '#163f53', t.get('text_color') or '#fff', tool_art(t, 'tl'), tool_title(t, 'tl-title'), tool_btn(t, 'span')) for t in TOOLS)
    tools += '\n        <li><div class="tool soon"><span>COMING SOON</span></div></li>'

    ogp = ''
    if SITE.get('ogp_image'):
        ogp = '  <meta property="og:url" content="%s">\n  <meta property="og:image" content="%simg/%s">' % (SITE_URL, SITE_URL, img(SITE['ogp_image']))
    v = dict(total=total, radios=radios, bars=bars, cyc=cyc, pick=pick, slides='\n'.join(slides), slide=slide, news=news, cards='\n'.join(cards), vids=vids, tools=tools,
             booth=e(SITE['booth']), x=e(SITE['x']), gm=e(SITE['gamemarket']), mail=e(SITE['mail']), note=e(SITE['note']), member_x=e(SITE['member_x']),
             about=T(SITE.get('about_ja'), SITE.get('about_en')), ogp=ogp, modals=modals)
    s = open(os.path.join(ROOT, 'build', 'top_template.html'), encoding='utf-8').read()
    for _ in range(2):
        s = re.sub(r'\{\{(?!img:|L:)(\w+)\}\}', lambda m: str(v[m.group(1)]), s)
    s = re.sub(r'\{\{L:(.*?)\|(.*?)\}\}', r'<span lang="ja">\1</span><span lang="en">\2</span>', s, flags=re.S)
    s = re.sub(r'\{\{img:([\w.\-/]+)\}\}', r'img/\1', s)
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)[:5]
    # 使っている画像がそろっているか
    missing = sorted({m for m in re.findall(r'img/([\w.\-/]+\.(?:png|webp|jpg|jpeg|gif|svg))', s) if not os.path.exists(os.path.join(IMG_DIR, m))})
    if missing:
        sys.exit('見つからない画像があります: ' + ', '.join(missing))
    return s

def colors():
    """色見本:編集画面では色コードしか見えないので、今の設定の色を並べたページを作る(new/colors.html)"""
    def sw(label, c):
        c = str(c or '').strip()
        if not c:
            return '<div class="sw none"><i></i><b>%s</b><code>(画像の色のまま)</code></div>' % label
        return '<div class="sw"><i style="background:%s"></i><b>%s</b><code>%s</code></div>' % (e(c), label, e(c))
    rows = []
    for g in GAMES:
        bn = g.get('banner') or {}
        prev = '<div class="pv" style="background:%s"><span style="background:%s;color:%s">%s人 / %s分 / %s歳から</span><small style="color:%s">ジャンル:%s</small></div>' % (
            e(g['color_face']), e(g['color_band']), e(g['color_face']), *map(e, spec(g)), e(g['color_band']), e(g.get('genre_ja') or ''))
        rows.append('<section><h2>%s <small>%s</small></h2><div class="grid">%s%s%s%s%s%s</div><p class="lbl">開いたカードの見え方</p>%s</section>' % (
            e(g['name']), e(g['key']), sw('開いたカードの背景色', g['color_face']), sw('人数〜年齢の下地の色', g['color_band']), sw('ロゴの色', g.get('logo_color')),
            sw('バナーの背景色', bn.get('bg') or g['color_face']), sw('バナーの文字の色', bn.get('text_color') or '#ffffff'), sw('バナーのロゴの色', bn.get('logo_color') or g.get('logo_color')), prev))
    for t in TOOLS:
        rows.append('<section><h2>%s <small>%s</small></h2><div class="grid">%s%s</div></section>' % (e(t['name']), e(t['key']), sw('背景色', t.get('bg')), sw('文字の色', t.get('text_color'))))
    return """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>色見本 | PANDA KINEMA</title>
<style>body{margin:0;padding:24px 16px 48px;background:#1b2228;color:#f3f2ee;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif}main{max-width:900px;margin:auto}
h1{font-size:22px}p.note{color:#9aa3a9;font-size:13px;line-height:1.8}section{margin:22px 0;padding:18px;border:1px solid #3a464f;border-radius:12px;background:#222b32}h2{margin:0 0 12px;font-size:17px}h2 small{color:#9aa3a9;font-weight:400}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}.sw{display:grid;grid-template-columns:40px 1fr;grid-template-rows:auto auto;column-gap:10px;align-items:center}
.sw i{grid-row:1/3;width:40px;height:40px;border-radius:8px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25)}.sw.none i{background:repeating-linear-gradient(45deg,#3a464f 0 4px,#2a333a 4px 8px)}.sw b{font-size:13px}.sw code{font-size:13px;color:#cdd2d4}
.lbl{margin:14px 0 6px;font-size:12px;color:#9aa3a9}.pv{display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px;border-radius:10px}.pv span{padding:.2em .9em;border-radius:999px;font-weight:800;font-size:13px}.pv small{font-weight:800}</style></head>
<body><main><h1>色見本</h1><p class="note">編集画面の色コードが、実際に何色かを確かめるためのページです。保存して1〜2分すると、ここも新しい色に変わります。</p>""" + ''.join(rows) + '</main></body></html>'

if __name__ == '__main__':
    out = os.path.join(OUT_DIR, 'index.html')
    open(out, 'w', encoding='utf-8').write(render())
    print(out, os.path.getsize(out))
    open(os.path.join(OUT_DIR, 'colors.html'), 'w', encoding='utf-8').write(colors())
