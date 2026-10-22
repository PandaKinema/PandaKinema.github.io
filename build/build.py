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
MINIS = load('minis')
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
def tlogo(g, cls, lc=None):   # ロゴを好きな色に塗る(マスク)
    w, h = size(g['logo'])
    return '<span class="%s" role="img" aria-label="%s" style="--lg:url(img/%s);aspect-ratio:%d/%d;--lc:%s"></span>' % (cls, e(g['name']), img(g['logo']), w, h, lc or g['logo_color'])
def btns(g, more=True):
    """▶詳しく見る ▶BOOTHで購入。作品ページが空ならカードを開く。BOOTHが空ならサークルのBOOTH"""
    b = ''
    if more:
        if g.get('page'):
            b += '<a class="wb" href="%s"%s>%s%s</a>' % (e(g['page']), ext(g['page']), AR, L('詳しく見る', 'More info'))
        else:
            b += '<label class="wb" for="c-%s">%s%s</label>' % (g['key'], AR, L('詳しく見る', 'More info'))
    booth = g.get('booth') or SITE['booth']
    b += '<a class="wb" href="%s" target="_blank" rel="noopener">%s%s</a>' % (e(booth), AR, L('BOOTHで購入', 'Buy on BOOTH'))
    return b
def meta(g):   # バナー用:2〜3人・10〜15分・6歳から・ジャンル(下地なし)
    s = spec(g)
    return '%s{{L:人| players}}・%s{{L:分| min}}・%s{{L:歳から|+}}・%s' % (s[0], s[1], s[2], L(g.get('genre_ja'), g.get('genre_en')))
def date(v):
    return str(v or '').strip().replace('-', '.').replace('/', '.')
def genre(g):
    return L('ジャンル:', 'Genre: ') + L(g.get('genre_ja'), g.get('genre_en'))

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
            txt = '<p class="b-series">PLAY &amp; TOOLS</p><h2 class="b-name">%s</h2><p class="b-intro">%s</p>' % (tool_title(t, 'b-mtitle'), L(t.get('intro_ja'), t.get('intro_en')))
            return 'b-tool b-' + key, 'background:%s;--fg:%s' % (t.get('bg') or '#163f53', t.get('text_color') or '#fff'), art, txt, tool_btn(t), v
    for i, m in enumerate(MINIS):
        if m['key'] == key:
            art = '<img class="b-mini" src="img/%s" alt="%s">' % (img(m['pkg']), e(m['name']))
            intro = L(m.get('intro_ja'), m.get('intro_en')) if m.get('intro_ja') else L(m.get('copy_ja'), m.get('copy_en'))
            txt = '<p class="b-series">MINI THEATER SERIES %02d</p><h2 class="b-name"><img class="b-mlogo" src="img/%s" alt="%s"></h2><p class="b-meta">%s</p><p class="b-intro">%s</p>' % (
                i + 1, img(m['logo']), e(m['name']), meta(m), intro)
            return 'b-minis', 'background:%s;--fg:%s' % (m['color_face'], m.get('text_color') or '#fff'), '' if (m.get('video') or m.get('youtube')) else art, txt, btns(m), vid(m.get('video'), m.get('youtube'))
    g = [x for x in GAMES if x['key'] == key][0]
    bn = g.get('banner') or {}
    bg = bn.get('bg') or g['color_face']
    if bn.get('pattern') == 'tri':
        bg += ' ' + TRI
    if bn.get('image'):   # 背景を画像で作ったとき:パッケージは出さない
        bg = "%s url(img/%s) center/cover no-repeat" % (bn.get('bg') or g['color_face'], img(bn['image']))
        art = ''
    else:
        art = '<img class="b-pkg" src="img/%s" alt="%sのパッケージ">' % (img(g['pkg']), e(g['name']))
    if bn.get('video') or bn.get('youtube'):
        art = ''
    intro = '<p class="b-intro">%s</p>' % L(g.get('intro_ja'), g.get('intro_en')) if g.get('intro_ja') else ''
    txt = '%s%s<p class="b-meta">%s</p>%s' % (
        '<p class="b-new">%s</p>' % L('新作', 'NEW') if g.get('new') else '', tlogo(g, 'b-logo', bn.get('logo_color')), meta(g), intro)
    return 'b-' + key, 'background:%s;--fg:%s' % (bg, bn.get('text_color') or '#fff'), art, txt, btns(g), vid(bn.get('video'), bn.get('youtube'))

def render():
    slide = int(SITE.get('slide_seconds') or 7)
    n = len(BANNERS); total = n * slide
    radios = ''.join('<input class="br sr" type="radio" name="bn" id="br%d" aria-label="%d枚目">' % (i + 1, i + 1) for i in range(n))
    slides = []
    for i, b in enumerate(BANNERS):
        if b.get('image') or b.get('video') or b.get('youtube'):   # 自分で作ったバナー画像・動画をそのまま出す(画面いっぱいに広げる)
            alt = e(b.get('alt') or '')
            pic = vid(b.get('video'), b.get('youtube')) if (b.get('video') or b.get('youtube')) else '<img class="b-img" src="img/%s" alt="%s"%s>' % (img(b['image']), alt, '' if i == 0 else ' loading="lazy"')
            link = '<a class="b-link" href="%s"%s aria-label="%s"></a>' % (e(b['link']), ext(b['link']), alt) if b.get('link') else ''
            slides.append('      <article class="slide s%d b-custom" style="--d:%ds;background:%s">%s%s</article>' % (i + 1, i * slide, e(b.get('bg') or '#000'), pic, link))
            continue
        cls, bg, art, txt, bt, vd = banner(b['key'])
        slides.append('      <article class="slide s%d %s%s" style="--d:%ds;%s">%s<div class="b-art">%s</div><div class="b-in">%s<div class="b-btns">%s</div></div></article>' % (
            i + 1, cls, ' has-vid' if vd else '', i * slide, e(bg), vd, art, txt, bt))
    bars = ''.join('<label for="br%d" style="--d:%ds" aria-label="%d枚目"><i></i></label>' % (i + 1, i * slide, i + 1) for i in range(n))
    w = 100.0 / n; fd = 0.8 / total * 100
    cyc = ('    @keyframes cyc{0%%{opacity:0;visibility:hidden;z-index:1}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:1;visibility:visible;z-index:2}%.3f%%{opacity:0;visibility:hidden;z-index:1}100%%{opacity:0;visibility:hidden;z-index:1}}\n'
           '    @keyframes fill{0%%{width:0}%.3f%%{width:100%%}%.3f%%,100%%{width:0}}\n'
           '    @keyframes kb{0%%{scale:1}%.3f%%{scale:1.04}100%%{scale:1.04}}') % (fd, w, w + fd, w, w + .001, w + fd)
    pick = '\n'.join('    .hero:has(#br%d:checked) .s%d{opacity:1;visibility:visible;z-index:2}\n    .hero:has(#br%d:checked) .bars label:nth-child(%d) i{width:100%%}' % (i + 1, i + 1, i + 1, i + 1) for i in range(n))
    news = '\n'.join('        <li><a href="%s"%s><time>%s</time><span class="cat">%s</span><span class="t">%s</span></a></li>' % (
        e(x.get('link') or '#news'), ext(x.get('link')), e(date(x['date'])), L(x.get('cat_ja'), x.get('cat_en')), L(x.get('text_ja'), x.get('text_en'))) for x in NEWS)
    cards = []
    for i, g in enumerate(GAMES):
        cid = 'c-%s' % g['key']
        cards.append(('        <li class="card" style="--c1:%s;--c2:%s"><input class="sr" type="radio" name="board" id="%s">'
                      '<label class="c-face" for="%s"><img src="img/%s" alt="%s" loading="lazy">%s</label>'
                      '<div class="c-open"><img class="o-pkg" src="img/%s" alt="" loading="lazy"><div class="o-txt">%s%s<p class="o-genre">%s</p><div class="o-btns">%s</div></div>'
                      '<label class="o-x" for="board-x" aria-label="とじる"></label></div></li>')
                     % (g['color_band'], g['color_face'], cid, cid, img(g['front']), e(g['name']), '<span class="c-new">%s</span>' % L('新作', 'NEW') if g.get('new') else '',
                        img(g['pkg']), tlogo(g, 'o-logo'), spec_pill(spec(g), g['color_band'], g['color_face']), genre(g), btns(g)))
    for i, m in enumerate(MINIS):
        cid = 'c-%s' % m['key']
        bt = btns(m, more=bool(m.get('page')))
        cards.append(('        <li class="card mini" style="--c1:%s;--c2:%s"><input class="sr" type="radio" name="board" id="%s">'
                      '<label class="c-face m-face" for="%s"><span class="m-top">MINI THEATER SERIES %02d</span><span class="m-mid"><img class="m-chara" src="img/%s" alt="" loading="lazy"><img class="m-logo" src="img/%s" alt="%s" loading="lazy"></span></label>'
                      '<div class="c-open m-open"><img class="m-pkg" src="img/%s" alt="%sのパッケージ" loading="lazy"><div class="m-info"><div class="m-l"><img class="m-ologo" src="img/%s" alt="">%s</div><div class="m-r"><p class="o-genre">%s</p><p class="o-copy">%s</p>%s</div></div>'
                      '<label class="o-x" for="board-x" aria-label="とじる"></label></div></li>')
                     % (m['color_band'], m['color_face'], cid, cid, i + 1, img(m['chara']), img(m['logo']), e(m['name']), img(m['pkg']), e(m['name']), img(m['logo']),
                        spec_pill(spec(m), m['color_band'], m['color_face']), genre(m), L(m.get('copy_ja'), m.get('copy_en')), '<div class="o-btns">%s</div>' % bt))
    vids = '\n'.join('        <li><button class="vid" type="button" data-yt="%s" aria-label="%s"><img src="img/%s" alt="" loading="lazy"><span class="v-play" aria-hidden="true">▶</span><span class="v-t"><b>%s</b><small>%s</small></span>%s</button></li>'
                     % (e(yt_id(v.get('youtube'))), e(v['title']), img(v['poster']), e(v['title']), L(v.get('kind_ja'), v.get('kind_en')),
                        '' if v.get('youtube') else '<span class="v-soon">%s</span>' % L('準備中', 'Coming soon')) for v in VIDEOS)
    tools = '\n'.join('        <li><a class="tool t-%s" href="%s"%s style="background:%s;color:%s">%s<span class="tl-t">%s%s</span></a></li>' % (
        t['key'], e(t['url']), ext(t['url']), t.get('bg') or '#163f53', t.get('text_color') or '#fff', tool_art(t, 'tl'), tool_title(t, 'tl-title'), tool_btn(t, 'span')) for t in TOOLS)
    tools += '\n        <li><div class="tool soon"><span>COMING SOON</span></div></li>'

    ogp = ''
    if SITE.get('ogp_image'):
        ogp = '  <meta property="og:url" content="%s">\n  <meta property="og:image" content="%simg/%s">' % (SITE_URL, SITE_URL, img(SITE['ogp_image']))
    v = dict(total=total, radios=radios, bars=bars, cyc=cyc, pick=pick, slides='\n'.join(slides), slide=slide, news=news, cards='\n'.join(cards), vids=vids, tools=tools,
             booth=e(SITE['booth']), x=e(SITE['x']), gm=e(SITE['gamemarket']), mail=e(SITE['mail']), note=e(SITE['note']), member_x=e(SITE['member_x']),
             about=L(SITE.get('about_ja'), SITE.get('about_en')), ogp=ogp)
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

if __name__ == '__main__':
    out = os.path.join(OUT_DIR, 'index.html')
    open(out, 'w', encoding='utf-8').write(render())
    print(out, os.path.getsize(out))
