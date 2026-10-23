# パンダキネマ 作品ページを組み立てる(new/games/<key>/index.html)
# 文章と画像は content/pages/<key>.yml(編集画面の「作品ページ」)、人数・時間・年齢は content/games.yml から読みます。
# このファイルには、各作品のデザイン(色・背景・遊び方の図の動き)が入っています。新しい作品のページを足すときは GAMES に追加します。
# 手元で動かすとき:  pip install pyyaml pillow  →  python build/game_pages.py
#
# パンダキネマ 作品ページ 共通フォーマット v22
#     v22: TRICO を現フォーマットで(キャラ=トリコとニコ、帯=三角、アイコン=トリコのシルエット、4コマ=取説のアピールの流れ)
#     v21: スクリーンの光の広がりを小さく(ぼんやりはそのまま)
#     v20: スクリーンの白い光をぼんやり(広く・薄く)
#     v19: スクリーンの光は白/ギャラリーの英字ラベルは GALLERY
#     v18: スクリーンの光は普段なし、触れたとき(ホバー・フォーカス・再生中)だけ光る/紹介動画の上にもビビル文字の帯/ギャラリー
#     v17: 動画まわりの光をなくす(黒帯だけ)/STORYのトゥーパを小さく/駒のトゥーパのバッジは外す
#     v16: おまけは最後に別の帯で/JA・EN切替(英語は仮訳。英語版の説明書が来たら差し替え)/ビビル文字の帯は色の境目に置かず、紺の帯の内側に
#     v15: 余白を詰める/遊び方のカードを正方形に近く(図の枠を低く)/スクープ記事にジェネレータの見本
#     v14: 動画は画面幅いっぱいの黒帯(スクリーン)/おまけ→STORYの中の「スクープ」記事に/フォトギャラリー/説明書へのリンク
#          キャラとして動かすのはキャラのトゥーパ(駒のトゥーパはアイコン・ゲーム中の姿だけ)
#     v13: 演出は「動きを減らす」設定でも再生。スクロール連動のパララックス・模様の横流れだけ設定に従って止める
# パッケージのメインビジュアル → 映画館のスクリーン(動画) → キャラクター+取説の導入文 → どんなゲーム?(目的の要約+図) → おまけ → 購入 → クレジット → ほかの作品
# v9: 骨組みは共通、作品ごとに「着せ替えパーツ」を差し替える(ファミコンのソフトサイト方式)
#     着せ替え:2色の帯/境目の模様/背景の地紋/見出しの飾り/強調色/キャラクター+ゲーム中の姿(バッジ)
#     ばら撒きの小物はなし。飾りは見出しとキャラクターにだけ付ける
#     v10: 見出しの飾りはトゥーパ(トークン)のシルエット(ビビル文字は文字なので飾りに使わない)/遊び方は横に流れるカード
#     v12: 遊び方は「ビビルの塔はこんなゲーム!」(説明シート)の4コマ。図はCSSだけでくり返し動く(スクリプトやスクロールに頼らない)
#          メインビジュアルの登場もCSSだけ
#     v11: 文章は取説準拠(取説の文をそのまま抜き出す。[[ ]] は取説の赤字)/見出し・文章は真ん中揃え/カードは順番に再生
import base64, mimetypes, os, re, sys, html as H

mimetypes.add_type('image/webp', '.webp')
import yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'new', 'games', 'img')   # 作品ページの画像(編集画面の「作品ページの画像」)
TOP_IMG = os.path.join(ROOT, 'new', 'img')
MANUAL_JA = '#'   # 遊び方説明書(日本語)のURLが決まったら差し替え
MANUAL_EN = '#'   # 英語版のURL
BOOTH = 'https://pandakinema.booth.pm/'   # 商品ページのURLが決まったら差し替え

def L(ja, en):   # 日本語/英語。切替ボタンで表示が変わる
    return '{{L:%s|%s}}' % (ja, en)

def uri(f):   # 作品ページ(new/games/<key>/)から見た画像の場所
    if not os.path.exists(os.path.join(WEB, f)):
        sys.exit('見つからない画像があります: new/games/img/' + f)
    return '../img/' + f

def load(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as fh:
        return yaml.safe_load(fh) or {}
def imgname(v):   # 画像の欄の値(img/foo.png、/new/games/img/foo.png など)を名前だけに
    v = str(v or '').strip().lstrip('/')
    for pre in ('new/games/img/', 'games/img/', 'img/'):
        if v.startswith(pre):
            return v[len(pre):]
    return v
def LL(d, k):   # 編集画面の _ja / _en を切替用の文字に(英語が空なら日本語)
    ja = str(d.get(k + '_ja') or ''); en = str(d.get(k + '_en') or '') or ja
    return L(ja, en) if ja else ''

def lum(c):   # 色の明るさ(読みやすさの判定用)
    c = str(c).lstrip('#'); r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)
def ink(bg, other=None):   # 背景に乗せる文字の色:もう1つのキーカラーで読めればそれ、だめなら白か濃い色
    if other and contrast(bg, other) >= 4.5:
        return other
    return '#ffffff' if contrast(bg, '#ffffff') >= contrast(bg, '#1b2228') else '#1b2228'

def apply(key):
    """content/pages/<key>.yml(編集画面)の文章と画像を、作品の設定に上書きする。動きとデザインはこのファイルのまま"""
    g = GAMES[key]
    d = load('content/pages/%s.yml' % key)
    site = load('content/site.yml')
    games = {x['key']: x for x in load('content/games.yml')}
    t0 = games.get(key) or {}
    for k in ('title', 'description', 'now_label', 'logo_alt'):
        if d.get(k):
            g[k] = str(d[k])
    if not d.get('title') and t0.get('name'):
        g['title'] = g['logo_alt'] = str(t0['name'])
    if not d.get('description') and t0.get('name'):
        g['description'] = '%s:%s パンダキネマ。' % (t0['name'], t0.get('intro_ja') or '')
    for k in ('logo', 'logo_buy', 'logo_credits', 'pkg', 'fab_pkg'):
        if d.get(k):
            g[k] = imgname(d[k])
    for k in ('logo', 'pkg'):
        from PIL import Image
        with Image.open(os.path.join(WEB, g[k])) as im:
            g[k + '_size'] = im.size
    for k in ('catch', 'intro', 'summary', 'chara_name', 'chara_note', 'contents', 'price', 'extra_kicker', 'extra_title'):
        if (k + '_ja') in d:
            g[k] = LL(d, k)
    if d.get('extra_text_ja') is not None:
        g['extra_html'] = re.sub(r'(<p class="extra-text">)\{\{L:.*?\}\}(</p>)', lambda m: m.group(1) + LL(d, 'extra_text') + m.group(2), g['extra_html'], count=1, flags=re.S)
    for st, ds in zip(g['steps'], d.get('steps') or []):
        st['b'] = LL(ds, 'text')
    if d.get('gallery') is not None:
        g['gallery'] = [(imgname(x['image']), str(x.get('caption_ja') or ''), str(x.get('caption_en') or x.get('caption_ja') or ''), 'wide' if x.get('wide') else '') for x in d['gallery'] if x.get('image')]
    if d.get('gallery_todo') is not None:
        g['gallery_todo'] = [(str(x.get('text_ja') or ''), str(x.get('text_en') or x.get('text_ja') or '')) for x in d['gallery_todo'] if x.get('text_ja')]
    if d.get('credits') is not None:
        g['credits'] = [(L(str(x.get('role_ja') or ''), str(x.get('role_en') or x.get('role_ja') or '')), L(str(x.get('name_ja') or ''), str(x.get('name_en') or x.get('name_ja') or ''))) for x in d['credits']]
    g['videos'] = d.get('videos') or [{'kind_ja': '遊び方動画', 'kind_en': 'How to Play', 'poster': g['poster']}]
    # 人数・時間・年齢は トップ(ボードゲーム)の設定と同じものを使う
    t = games.get(key)
    if t:
        g['spec'] = [(L('人数', 'Players'), L('%s人' % t['players'], str(t['players']).replace('〜', '–'))), (L('時間', 'Time'), L('%s分' % t['time'], '%s min' % str(t['time']).replace('〜', '–'))), (L('年齢', 'Age'), L('%s歳から' % t['age'], '%s+' % t['age']))]
    g['booth'] = d.get('booth') or (t or {}).get('booth') or site.get('booth') or BOOTH
    g['manual_ja'] = d.get('manual_ja') or '#'
    g['manual_en'] = d.get('manual_en') or g['manual_ja']
    g['site'] = site
    g['games'] = games
    # 背景2色(色か画像)と帯・見出しの飾り:編集画面の値を CSS の変数で上書き
    def tile(v):   # 2倍の大きさで作った画像を半分の大きさで敷き詰める
        f = imgname(v)
        with Image.open(os.path.join(WEB, f)) as im:
            w, h = im.size
        return f, w // 2, h // 2
    from PIL import Image
    css = []
    # 色の初期値はトップ(ボードゲーム)のキーカラー。文字の色は空なら読みやすい方を自動で選ぶ
    t = games.get(key) or {}
    k1, k2 = t.get('key1'), t.get('key2')
    bg1 = d.get('bg1_color') or k1; bg2 = d.get('bg2_color') or k2
    if bg1: css.append('--k-bg:%s;--k-ink:%s' % (bg1, d.get('bg1_text') or ink(bg1, bg2)))
    if bg2: css.append('--b2-bg:%s;--b2-ink:%s' % (bg2, d.get('bg2_text') or ink(bg2, bg1)))
    if k1 and k2:   # ボタン(BOOTHで購入など)もキーカラーで
        css.append('--accent:%s;--on-accent:%s' % (k2, ink(k2, k1)))
    if 'bg1_image' in d:
        if d.get('bg1_image'):
            f, w, h = tile(d['bg1_image']); css.append('--tex-c:url(../img/%s);--tex-size:%dpx %dpx' % (f, w, h))
        else:
            css.append('--tex-c:none')
    if d.get('bg2_image'):
        f, w, h = tile(d['bg2_image']); css.append('--b2-img:url(../img/%s);--b2-size:%dpx %dpx' % (f, w, h))
    if 'band_image' in d:
        if d.get('band_image'):
            f, w, h = tile(d['band_image']); css.append('--band:url(../img/%s);--band-h:%dpx;--band-d:block' % (f, h))
        else:
            css.append('--band-d:none')
    for k, var in (('heading_icon', '--orn'), ('step_icon', '--snum')):
        if d.get(k):
            css.append('%s:url(../img/%s)' % (var, imgname(d[k])))
    if css:
        g['theme'] += '\n      ' + ';'.join(css) + ';'
    # STORY のキャラクター:1体ずつ表示。複数いるときは ◀▶ で切り替え。それぞれ名前とプロフィール
    chars = [x for x in (d.get('characters') or []) if x.get('image')]
    if chars:
        slides = []
        for k, x in enumerate(chars):
            f = imgname(x['image'])
            with Image.open(os.path.join(WEB, f)) as im:
                w, h = im.size
            alt = H.escape(str(x.get('name_ja') or ''))
            if x.get('float'):   # 浮かぶ部品(トゥーパの玉など)を上に。元のトゥーパ(本体 560×526)の枠 1164:1562 と同じ考え方
                fig = '<div class="tupa" style="aspect-ratio:%d/%d"><span class="orb"><img src="{{img:%s}}" alt=""></span><img class="body" src="{{img:%s}}" alt="%s" loading="lazy"></div>' % (
                    1164, round(1164 * h / w * 1562 / (1164 * 526 / 560)), imgname(x['float']), f, alt)
            else:
                fig = '<img class="solo" src="{{img:%s}}" alt="%s" width="%d" height="%d" loading="lazy">' % (f, alt, w, h)
            note = LL(x, 'note')
            slides.append('<div class="chara-slide%s"%s><div class="fig-wrap">%s</div><figcaption><span class="chara-name">%s</span>%s</figcaption></div>' % (
                ' cur' if k == 0 else '', '' if k == 0 else ' aria-hidden="true"', fig, LL(x, 'name'), ('<span class="chara-note">%s</span>' % note.replace('\n', '<br>')) if note else ''))
        nav = ('<button class="cnav prev js-only" type="button" aria-label="前のキャラクター"></button><button class="cnav next js-only" type="button" aria-label="次のキャラクター"></button>'
               '<div class="cdots js-only">%s</div>' % ''.join('<i%s></i>' % (' class="on"' if k == 0 else '') for k in range(len(chars)))) if len(chars) > 1 else ''
        g['chara_html'] = '<div class="chara-slides">%s</div>%s' % (''.join(slides), nav)
    # おまけ:ブロックを上から順に。横に置く画像は別の欄
    blocks = d.get('extra_blocks')
    if blocks is not None:
        out = []
        for b in blocks:
            t = b.get('type')
            if t == 'text':
                out.append('<p class="extra-text">%s</p>' % LL(b, 'text'))
            elif t == 'image' and b.get('image'):
                out.append('<img class="extra-img" src="{{img:%s}}" alt="%s" loading="lazy">' % (imgname(b['image']), H.escape(str(b.get('alt') or ''))))
            elif t == 'button' and b.get('url'):
                out.append('<a class="btn" href="%s" target="_blank" rel="noopener">%s <span aria-hidden="true">↗</span></a>' % (H.escape(b['url']), LL(b, 'label')))
            elif t == 'box':
                demo = ''
                if b.get('image'):
                    demo = '<div class="moji-demo">%s<img class="moji-out" src="{{img:%s}}" alt="%s" loading="lazy"></div>' % (
                        ('<span class="moji-in">%s</span><span class="moji-arrow" aria-hidden="true">→</span>' % H.escape(str(b['demo_text']))) if b.get('demo_text') else '',
                        imgname(b['image']), H.escape(str(b.get('alt') or '')))
                out.append('<div class="moji"><p class="moji-h">%s%s</p>%s%s%s</div>' % (
                    LL(b, 'title'), ('<small>%s</small>' % H.escape(str(b['sub']))) if b.get('sub') else '', demo,
                    ('<p class="moji-note">%s</p>' % LL(b, 'note')) if b.get('note_ja') else '',
                    ('<a class="btn" href="%s" target="_blank" rel="noopener">%s <span aria-hidden="true">↗</span></a>' % (H.escape(b['url']), LL(b, 'button'))) if b.get('url') else ''))
        g['extra_html'] = ''.join(out)
        side = d.get('extra_side_image')
        g['extra_img'] = ('<img class="stele" src="{{img:%s}}" alt="%s" loading="lazy">' % (imgname(side), H.escape(str(d.get('extra_side_alt') or '')))) if side else ''
    return g

LINEUP_OLD = [
    dict(key='bibilu',  logo='b_logo_white.png',       copy=L('ビビっている場合じゃない', 'No time to be scared!'),     pkg='bibilu_pkg_sm.webp', url='https://gamemarket.jp/game/188751', alt='ビビルの塔'),
    dict(key='trico',   logo='trico_logo_white.png',   copy=L('あのコをトリコにするために', 'To win her heart'),   pkg='trico_pkg.webp',     url='https://gamemarket.jp/game/186182', alt='TRICO!'),
    dict(key='ikatako', logo='ikatako_logo_white.png', copy=L('イカだ！タコだ！手を挙げろ！', 'Squid! Octopus! Hands up!'), pkg='ikatako_pkg.webp',   url='https://gamemarket.jp/game/186696', alt='イカタコ'),
    dict(key='moko',    logo='moko_logo_white.png',    copy=L('ねむりは競争だ。', 'Sleep is a race.'),             pkg='moko_pkg.webp',      url='https://gamemarket.jp/game/187698', alt='モコチャカ'),
]

# ---------------------------------------------------------------- 部品
CN = {'y': '黄', 'p': '紫', 'r': '赤'}
def tc(code, i=0, cls=''):
    return '<img class="c %s" style="--i:%d" src="{{img:tc_%s.webp}}" alt="%sの%s">' % (cls, i, code, CN[code[0]], code[1:])
def tflip(code, i=0):
    return '<span class="flip" style="--i:%d"><img class="c back" src="{{img:tc_ura.webp}}" alt=""><img class="c front" src="{{img:tc_%s.webp}}" alt="%sの%s"></span>' % (i, code, CN[code[0]], code[1:])
def jrow(n, label, cards, win, rule):
    cs = ''.join(('<span class="win" style="--i:%d">%s<b>WIN</b></span>' % (n * 3 + k, tc(c, n * 3 + k))) if c == win else tc(c, n * 3 + k) for k, c in enumerate(cards))
    return '<div class="jrow"><span class="jlabel">%s</span><span class="jcards">%s</span><span class="jrule">%s</span></div>' % (label, cs, rule)
def bc(n, i=0, cls=''):
    return '<img class="c %s" style="--i:%d" src="{{img:bc_%d.webp}}" alt="%dのカード">' % (cls, i, n, n)
def bflip(n, i=0):
    return '<span class="flip" style="--i:%d"><img class="c back" src="{{img:bc_ura.webp}}" alt=""><img class="c front" src="{{img:bc_%d.webp}}" alt="%dのカード"></span>' % (i, n, n)
def slot(n, i, badge=''):
    return '<span class="slot%s" style="--i:%d">%s<b>%s</b></span>' % (' on' if badge else '', i, bc(n, i), badge)
def tower(nums, fall=0):
    out = []
    for i, n in enumerate(nums):
        cls = 'fall' if i < fall else ('stay' if fall else '')
        out.append('<img class="tc %s" style="--i:%d" src="{{img:bc_%d.webp}}" alt="%dのカード">' % (cls, i, n, n))
    return '<div class="tower" style="--n:%d;--fall:%d">%s</div>' % (len(nums), fall, ''.join(out))

# くり返し動く図(説明シートの4コマを動かしたもの)
def lflip(n, i):
    return '<span class="lf" style="--i:%d"><img class="c back" src="{{img:bc_ura.webp}}" alt=""><img class="c front" src="{{img:bc_%d.webp}}" alt="%dのカード"></span>' % (i, n, n)
def pick(n, i, mark=''):
    mk = '' if not mark else ('<b class="star" aria-label="バッティング"></b>' if mark == 'star' else '<b class="crown" aria-label="%s位">%s</b>' % (mark, mark))
    return '<span class="pk%s" style="--i:%d">%s%s</span>' % (' sel' if mark else '', i, lflip(n, i), mk)
def ltower(nums, fall=0, ruler=5):
    cs = ''.join('<img class="lt%s" style="--i:%d" src="{{img:bc_%d.webp}}" alt="%dのカード">' % ((' fall' if k < fall else (' stay' if fall else '')), k, n, n) for k, n in enumerate(nums))
    rl = ''.join('<li style="--i:%d">%d</li>' % (k, k + 1) for k in range(ruler))
    return '<div class="ltw"><ol class="ruler" aria-hidden="true">%s</ol><div class="ltower" style="--n:%d;--fall:%d">%s</div></div>' % (rl, len(nums), fall, cs)

TRI_PATTERN = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='92' height='160'%3E%3Crect width='92' height='160' fill='%23fbc500'/%3E%3Cpolygon points='0,80 46,0 92,80' fill='%23fdd000'/%3E%3Cpolygon points='-46,160 0,80 46,160' fill='%23fdd000'/%3E%3Cpolygon points='46,160 92,80 138,160' fill='%23fdd000'/%3E%3C/svg%3E\")"

GAMES = {}

# ---- TRICO:くり返し動く図の部品
def tlf(code, i):   # 伏せたカードがめくれる
    return '<span class="lf" style="--i:%d"><img class="c back" src="{{img:tc_ura.webp}}" alt=""><img class="c front" src="{{img:tc_%s.webp}}" alt="%sの%s"></span>' % (i, code, CN[code[0]], code[1:])
def tcard(code, i=0, cls=''):
    return '<img class="tcd %s" style="--i:%d" src="{{img:tc_%s.webp}}" alt="%sの%s">' % (cls, i, code, CN[code[0]], code[1:])
def trow(n, label, cards, win, rule):
    cs = ''.join(('<span class="tw" style="--i:%d">%s<b>WIN</b></span>' % (n, tcard(c))) if c == win else tcard(c) for c in cards)
    return '<div class="trow" style="--i:%d"><span class="tlabel">%s</span><span class="tcards">%s</span><span class="trule">%s</span></div>' % (n, label, cs, rule)

GAMES['trico'] = dict(
    title='TRICO!',
    description='TRICO!(トリコ):カードを出し合い、場に出た色の数で勝敗が決まる「アピール」をくり返して3色をそろえる、2〜3人用のカードゲーム。パンダキネマ。',
    now_label='NOW SHOWING',
    theme='''
      --k-bg:#7b59a3; --k-ink:#ffffff;            /* キーカラー:紫(パッケージ下部) */
      --accent:#fdd000; --on-accent:#3a2366;      /* キーカラー:黄 */
      --p-ink:#3a2366; --soft:#fff6cf;
      --sec-bg:#fdd000; --sec-ink:#3a2366;
      --pan-bg:#e8343d; --pan-ink:#fff;
      --room:#4b2f7f; --glow:255,236,150;
      --b2-bg:#fdd000; --b2-ink:#3a2366;          /* もう1色の帯:黄 */
      --band:url({{img:t_band.png}}); --band-h:22px;          /* 帯の模様:パッケージの三角 */
      --tex-c:url({{img:t_tex_c.png}}); --tex-size:92px 160px;
      --orb-glow:255,236,150;
      --hl:#fdd000;                               /* 強調色(取説の赤字の代わり。紫の上で読める黄) */
      --orn:url({{img:t_bird_sten.png}}); --snum:url({{img:t_bird_sil.png}});   /* 見出しの飾り:トリコのシルエット。反転しない */
      --scoop-bg:#ffffff; --scoop-ink:#3a2366;
    ''',
    # パッケージ表面の構図:三角模様+宝石+トリコ+ロゴ
    hero_cls='hero-trico',
    hero_art='<div class="hero-art" style="background:#fdd000 ' + TRI_PATTERN + ' center top/92px 160px"></div>',
    hero_visual='''<div class="pkgvis" aria-hidden="true">
          <img class="g g1" src="{{img:gem_red.webp}}" alt=""><img class="g g2" src="{{img:gem_purple.webp}}" alt=""><img class="g g3" src="{{img:gem_yellow.webp}}" alt="">
          <img class="bird" src="{{img:trico_bird.webp}}" alt="">
        </div>''',
    hero_css='''
    .hero-trico{color:#3a2366}
    .hero-trico .hero-main{margin-block:auto}
    .hero-trico .btn{background:#7b59a3;color:#fff}
    .pkgvis{position:relative;width:min(380px,58vw);margin:0 auto -5%}
    .pkgvis .bird{position:relative;width:100%}
    .pkgvis .g{position:absolute}
    .pkgvis .g1{left:-20%;top:-14%;width:20%;rotate:-14deg}
    .pkgvis .g2{right:-24%;top:-8%;width:25%;rotate:8deg}
    .pkgvis .g3{left:-24%;top:58%;width:20%;rotate:-6deg}
    .hero-trico .logo{position:relative;width:min(460px,76vw)}
    /* 登場とゆらゆら(CSSだけ) */
    @media all{
      .pkgvis .bird{animation:tbird .8s cubic-bezier(.3,1.5,.5,1) .1s both}
      @keyframes tbird{from{opacity:0;translate:0 30px}}
      .pkgvis .g{animation:tgem .55s cubic-bezier(.3,1.8,.5,1) both,bob 2.8s ease-in-out 1.2s infinite alternate}
      .pkgvis .g1{animation-delay:.5s,1.2s}.pkgvis .g2{animation-delay:.65s,.4s}.pkgvis .g3{animation-delay:.8s,-.6s}
      @keyframes tgem{from{opacity:0;scale:.3}}
      @keyframes bob{to{translate:0 -10px}}
    }
    /* STORY:トリコとニコ */
    .cast{display:flex;align-items:flex-end;justify-content:center;gap:4px;width:min(520px,90vw)}
    .cast img{width:24%;animation:lhop2 3.6s cubic-bezier(.3,.6,.4,1) infinite;animation-delay:calc(var(--i) * -.9s)}
    .cast .cast-nico{width:27%}
    /* 遊び方の図 */
    .tp1{display:flex;align-items:flex-end;justify-content:center;gap:18px;padding-bottom:26px}
    .tp1 figure{position:relative;margin:0;display:flex;align-items:flex-end;gap:6px}
    .tp1 figcaption{position:absolute;left:50%;top:calc(100% + 8px);translate:-50% 0;padding:2px 10px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:11px;font-weight:800;white-space:nowrap}
    .tp1 .lead{width:40px;border-radius:4px;rotate:-8deg;box-shadow:0 3px 8px rgba(0,0,0,.14)}
    .tp1 .lf{--card-w:58px}
    .tp1 .tcd{width:58px}
    .tcd{display:block;border-radius:5px;box-shadow:0 3px 8px rgba(0,0,0,.14)}
    .tjudge{display:grid;gap:9px;width:100%}
    .trow{display:grid;grid-template-columns:34px auto minmax(0,1fr);align-items:center;gap:8px}
    .tlabel{display:grid;place-items:center;height:22px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:11px;font-weight:800}
    .tcards{display:flex;gap:4px}
    .tcards .tcd{width:36px;box-shadow:0 2px 5px rgba(0,0,0,.12)}
    .trule{font-size:11px;font-weight:800;line-height:1.35;text-align:left}
    .tw{position:relative;display:block;border-radius:5px;outline:3px solid #e8343d;outline-offset:1px}
    .tw b{position:absolute;left:50%;bottom:-8px;translate:-50% 0;padding:0 5px;border-radius:999px;background:#e8343d;color:#fff;font-size:9px;line-height:14px}
    .tp3{display:flex;align-items:flex-end;justify-content:center;gap:12px;padding-top:34px}
    .tp3 .tcd{width:62px}
    .tpick{position:relative;display:block;translate:0 -22px;rotate:4deg}
    .tpick b{position:absolute;left:50%;top:-30px;translate:-50% 0;padding:2px 10px;border-radius:999px;background:#e8343d;color:#fff;font-size:12px;white-space:nowrap}
    .tp4{display:flex;align-items:flex-end;justify-content:center;gap:12px;width:100%;padding-top:30px}
    .thand{position:relative;display:flex;gap:5px}
    .thand .tcd{width:50px}
    .tbub{position:absolute;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:800;white-space:nowrap}
    .tbub.nico2{left:22%;top:-30px;background:#ec6ea6;color:#fff}
    .twin{position:relative;display:flex;align-items:flex-end;gap:2px}
    .twin .wbird{width:70px}
    .twin .mk{width:34px;margin-bottom:2px}
    .tbub.trico3{left:-10px;top:-32px;border:2px solid var(--p-ink);background:#fff;color:var(--p-ink)}
    /* くり返し(スクリプト不要)。土台は完成図 */
    @media all{
      .s1 .lead,.s1 .tcd{animation:tdrop 6s cubic-bezier(.3,1.4,.5,1) infinite}
      @keyframes tdrop{0%{opacity:0;translate:0 -30px}8%{opacity:1;translate:0 0}86%{opacity:1;translate:0 0}94%,100%{opacity:0;translate:0 0}}
      .s1{--o:.5s}
      .s1 figcaption{animation:lmark 6s ease infinite}
      .trow{animation:trow 7s ease infinite;animation-delay:calc(var(--i) * .5s)}
      @keyframes trow{0%{opacity:0;translate:-14px 0}8%{opacity:1;translate:0 0}84%{opacity:1;translate:0 0}92%,100%{opacity:0;translate:0 0}}
      .tw{animation:tring 7s ease infinite;animation-delay:calc(var(--i) * .5s)}
      @keyframes tring{0%,16%{outline-color:transparent}22%,84%{outline-color:#e8343d}92%,100%{outline-color:transparent}}
      .tw b{animation:lmark 7s ease infinite;animation-delay:calc(var(--i) * .5s - .9s)}
      .s3 .tcd{animation:tdrop 6s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .15s)}
      .tpick{animation:tlift 6s cubic-bezier(.3,1.5,.5,1) infinite}
      @keyframes tlift{0%,26%{translate:0 0;rotate:0deg}34%,86%{translate:0 -22px;rotate:4deg}94%,100%{translate:0 0;rotate:0deg}}
      .tpick b{animation:lmark 6s ease infinite}
      .s4 .thand .tcd{animation:t4in 7s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .35s)}
      .s4 .thand .tcd.late{animation-name:t4late;animation-delay:0s}
      @keyframes t4in{0%{opacity:0;translate:0 -30px}7%{opacity:1;translate:0 0}86%{opacity:1;translate:0 0}93%,100%{opacity:0;translate:0 0}}
      @keyframes t4late{0%,44%{opacity:0;translate:0 -30px}50%{opacity:1;translate:0 0}86%{opacity:1;translate:0 0}93%,100%{opacity:0;translate:0 0}}
      .tbub.nico2{animation:t4nico 7s ease infinite}
      @keyframes t4nico{0%,22%{opacity:0;scale:.4}27%{opacity:1;scale:1.15}31%,46%{opacity:1;scale:1}50%,100%{opacity:0;scale:.6}}
      .twin .wbird{animation:t4bird 7s cubic-bezier(.3,1.6,.5,1) infinite}
      @keyframes t4bird{0%,52%{opacity:0;translate:0 24px}58%,86%{opacity:1;translate:0 0}93%,100%{opacity:0;translate:0 0}}
      .tbub.trico3,.twin .mk{animation:t4win 7s ease infinite}
      .twin .mk{animation-delay:.3s}
      @keyframes t4win{0%,58%{opacity:0;scale:.4}63%{opacity:1;scale:1.15}66%,86%{opacity:1;scale:1}93%,100%{opacity:0;scale:.6}}
    }
    .fig-wrap:has(.cast){width:auto}
    @media (max-width:650px){ .cast{width:min(360px,88vw)} }''',
    logo='trico_logo_purple.png', logo_size=(1021, 382), logo_alt='TRICO!(トリコ)',
    logo_buy='trico_logo_purple.png', logo_credits='trico_logo_white.png',
    viewers='',
    # キャラクター(キャラとして使う絵:トリコ3色とニコ)
    chara_name=L('トリコ と ニコ', 'Trico & Nico'),
    chara_fig='<div class="cast"><img style="--i:0" src="{{img:t_tricoR.webp}}" alt="赤のトリコ"><img style="--i:1" src="{{img:t_tricoY.webp}}" alt="黄のトリコ"><img class="cast-nico" style="--i:2" src="{{img:t_nico.webp}}" alt="ニコ"><img style="--i:3" src="{{img:t_tricoP.webp}}" alt="紫のトリコ"></div>',
    piece_img='t_marker.webp', piece_alt='トリコマーカー',
    chara_note='',
    catch=L('あのコをとりこにするために', 'To win her heart'),
    intro=L('どこかに生息するカラフルな鳥、トリコ。3匹のオスは、美しいメス「ニコ」のハートを射止めようとアピールをしています。ただし、それぞれが持ち寄る宝石の色によってニコの好みは変わります。見事ニコに3色の宝石を受け取ってもらえたら、「トリコ!」と高らかに宣言しましょう!',
            'Somewhere lives a colorful bird called Trico. Three males are courting the beautiful female, Nico, trying to win her heart. But Nico’s taste changes with the color of the gems each one brings. If Nico accepts gems of all three colors, proudly declare “Trico!”'),
    intro_img=('t_nico_pair.webp', 'ニコとトリコ', 'intro-pair'),
    summary=L('カードを手札から出し合い、場に出た色の数で勝敗が決まる[[「アピール」]]を行います。勝ったプレイヤーは場に出た3枚のカードのうち、好きなカードを獲得します。これを繰り返し、得点カードの中に[[3色が揃ったら、「トリコ!」と宣言してラウンド勝利]]となります。最初に[[2回]]ラウンド勝利したプレイヤーがこのゲームの勝者です。',
              'Players play cards from their hands in an [[“Appeal,”]] where the number of colors on the table decides the winner. The winner takes any one of the 3 cards played. Repeat this, and [[when your cards hold all 3 colors, declare “Trico!” to win the round.]] The first player to win [[2]] rounds wins the game.'),
    spec=[(L('人数', 'Players'), L('2〜3人', '2–3')), (L('時間', 'Time'), L('10〜15分', '10–15 min')), (L('年齢', 'Age'), L('6歳から', '6+'))],
    poster='trico_poster.webp',
    # 遊び方:取説「アピールの流れ」「ニコ!」「トリコ!」から(文は取説のまま、[[ ]]は取説の赤字)
    steps=[
        dict(cls='s1', b=L('リードプレイヤーが手札から1枚、カードを表向きに公開します。他の2人のプレイヤーは手札から裏向きで1枚カードを出し、[[同時に表向きに公開します。]]',
                           'The lead player reveals one card from their hand face up. The other 2 players each play a card face down, then [[reveal them at the same time.]]'),
             v='<div class="tp1"><figure><img class="lead" src="{{img:tc_lead_o.webp}}" alt="リードプレイヤーマーカー">' + tcard('y21') + '<figcaption>' + L('リードプレイヤー', 'Lead player') + '</figcaption></figure>'
               '<figure>' + tlf('p30', 1) + tlf('y12', 2) + '<figcaption>' + L('同時に公開', 'Reveal together') + '</figcaption></figure></div>'),
        dict(cls='s2', b=L('場に揃った[[色の数]]で勝敗を決めます。勝ったカードが複数あった場合アピールは無効となり、全て捨て札になります。',
                           'The [[number of colors]] on the table decides the winner. If more than one card wins, the Appeal is void and all cards are discarded.'),
             v='<div class="tjudge">' + trow(0, L('1色', '1'), ['p3', 'p12', 'p24'], 'p24', L('最も大きい数', 'Highest')) + trow(1, L('2色', '2'), ['p3', 'p24', 'r27'], 'p3', L('同じ色の中で<br>最も小さい数', 'Lowest of<br>the pair color')) + trow(2, L('3色', '3'), ['p9', 'y24', 'r15'], 'y24', L('最も大きい数', 'Highest')) + '</div>'),
        dict(cls='s3', b=L('アピールの勝者は場に出た3枚のカードのうち、[[好きなカードを1枚獲得]]し、手元に表向きで置きます。',
                           'The winner of the Appeal [[takes any one]] of the 3 cards played and places it face up in front of them.'),
             v='<div class="tp3">' + tcard('p3', 0) + '<span class="tpick">' + tcard('r27', 1) + '<b>' + L('獲得!', 'Take!') + '</b></span>' + tcard('p24', 2) + '</div>'),
        dict(cls='s4', b=L('獲得したカードが2色になったら[[「ニコ!」]]、3色になったら[[「トリコ!」]]と宣言します。トリコマーカーを2つ獲得したらゲーム終了!',
                           'Declare [[“Nico!”]] when your cards hold 2 colors, and [[“Trico!”]] at 3 colors. Collect 2 Trico markers to win the game!'),
             v='<div class="tp4"><div class="thand">' + tcard('p12', 0) + tcard('y6', 1) + '<span class="tbub nico2">' + L('ニコ!', 'Nico!') + '</span>' + tcard('r18', 2, 'late') + '</div>'
               '<div class="twin"><span class="tbub trico3">' + L('トリコ!', 'Trico!') + '</span><img class="wbird" src="{{img:t_tricoP.webp}}" alt=""><img class="mk" src="{{img:t_marker.webp}}" alt="トリコマーカー"></div></div>'),
    ],
    extra_kicker=L('みんなでかこう!', 'Let’s draw!'),
    extra_title=L('TRICO! えかきうた', 'TRICO! drawing song'),
    extra_html='<img class="extra-img" src="{{img:t_ekaki.webp}}" alt="トリコのえかきうた。西からのぼったおひさまが、ずれてはんしゃしているよ、今日もいい日だにじゅうまる!、ここはくちばしいっぽんせん、足としっぽをかいたなら、あっというまにトリコだね!" width="1286" height="511" loading="lazy">'
               '<p class="extra-text">' + L('キミもかいてみよう!!', 'Try drawing one yourself!') + '</p>',
    extra_img='',
    gallery=[('tg_manual1.webp', '遊び方説明書(表)', 'Rulebook (front)', 'wide'), ('trico_pkg_lg.webp', 'パッケージ', 'Box', ''),
             ('tg_summary.webp', 'サマリー', 'Summary card', ''), ('tg_manual2.webp', '遊び方説明書(裏)', 'Rulebook (back)', 'wide')],
    gallery_todo=[],
    fab_pkg='trico_pkg.webp',
    pkg='trico_pkg_lg.webp', pkg_size=(567, 900),
    contents=L('ゲームカード30枚(各色10枚)、リードプレイヤーマーカー1枚、サマリー1枚、トリコマーカー3個、遊び方説明書1枚',
               '30 game cards (10 per color), lead player marker, summary card, 3 Trico markers, rulebook'),
    price='',
    credits=[(L('デザイン・アートワーク', 'Design & Artwork'), L('ゐするぎ', 'Isurugi')), (L('印刷', 'Printing'), 'グラフィック'),
             (L('トークン製造', 'Tokens'), 'PROCASE STORE ' + L('様', '')), ('Special Thanks', L('テストプレイをしてくれた皆さん', 'Everyone who playtested')),
             ('', L('アンザイミユキ(イラスト原案)', 'アンザイミユキ (original illustration concept)')), (L('発行', 'Published'), L('2025年11月', 'November 2025'))],
)

GAMES['bibilu'] = dict(
    title='ビビルの塔',
    description='ビビルの塔:数字カードを同時に出し、高い塔を建てて得点を競う2〜4人用のカードゲーム。パンダキネマ。',
    now_label='NOW SHOWING',
    theme='''
      --k-bg:#163f53; --k-ink:#fff7df;            /* キーカラー:紺 */
      --accent:#fff1cf; --on-accent:#163f53;      /* キーカラー:クリーム */
      --p-ink:#163f53; --soft:#fbf0d5;
      --sec-bg:#fff1cf; --sec-ink:#163f53;
      --pan-bg:#163f53; --pan-ink:#fff;
      --room:#0b2533; --glow:170,215,225;
      --b2-bg:#fff1cf; --b2-ink:#163f53;          /* もう1色の帯:クリーム */
      --band:url({{img:b_band.png}}); --band-h:24px;          /* 帯の境目:塔の模様(ビビル文字) */
      --tex-c:url({{img:b_tex_c.png}}); --tex-size:525px 175px; --tex-a:rgba(255,241,207,.035);
      --orb-glow:27,185,238;
      --hl:#f2d756;                               /* 強調色(取説の赤字の代わり。紺の上で読める金色) */
      --orn:url({{img:b_tupa_sten.png}}); --snum:url({{img:b_tupa_sil.png}});   /* 見出しの飾り:トゥーパ(トークン)のシルエット。反転しない */
    ''',
    # パッケージの絵(文字なし)+ロゴ。パッケージと同じくロゴは下に
    hero_cls='hero-bibilu',
    hero_art='<div class="hero-art"><img class="art" src="{{img:b_art.jpg}}" alt="砂漠にそびえる塔と、丘を行く2人のトゥーパ" width="1600" height="1993" fetchpriority="high"></div>',
    hero_visual='',
    hero_css='''
    .hero-bibilu{color:#fff7df}
    .hero-bibilu .art{width:100%;height:100%;object-fit:cover;object-position:45% 64%}
    .hero-bibilu .hero-art::after{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,rgba(22,63,83,.45),transparent 16%,transparent 52%,rgba(22,63,83,.86) 82%,#163f53)}
    .hero-bibilu .logo{width:min(600px,86vw)}
    @media (max-width:650px){.hero-bibilu .art{object-position:40% 50%}}
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      .hero-bibilu .art{animation:artin 3s cubic-bezier(.2,.7,.2,1) both}
      @keyframes artin{from{opacity:0;scale:1.07}}
    }''',
    viewers='''<img class="viewer tupa" style="--x:14%;--i:0" src="{{img:b_tupa.webp}}" alt="">
        <img class="viewer tupa" style="--x:76%;--i:1" src="{{img:b_tupa.webp}}" alt="">''',
    logo='b_logo_cream.png', logo_size=(1100, 305), logo_alt='ビビルの塔 THE TOWER OF BIBILU',
    logo_buy='b_logo_navy.png', logo_credits='b_logo_white.png',
    # キャラクター(readme:キャラとして見せるときは tupa_1、木のコマとして見せるときは tokun)
    chara_name=L('トゥーパ [túpa]', 'Tupa [túpa]'),
    chara_fig='<div class="tupa"><span class="orb"><img src="{{img:b_tupa_orb.webp}}" alt=""></span><img class="body" src="{{img:b_tupa_body.webp}}" alt="トゥーパ" width="560" height="526" loading="lazy"></div>',
    piece_img='b_token_lg.webp', piece_alt='トゥーパ トークン',
    chara_note=L('遠い未来のどこかの惑星にいる生命体。\n塔を建てる力を持つ。\n古代の言い伝えを信じ、塔を建てることを大事にしている。', 'A lifeform on a planet somewhere in the distant future.\nIt has the power to build towers.\nIt believes in ancient legends and holds tower building dear.'),
    catch=L('ビビっている場合じゃない', 'No time to be scared!'),
    intro=L('遠い未来、どこかの惑星に、トゥーパという生命体がいました。彼らにとって、塔を建てることは何よりも大事です。高い塔ほど立派ですが、高くしすぎると神の天罰がくだり、たちまち崩れてしまいます。あなたもトゥーパとなり、ときには慎重に、ときには思いきって、誰よりも立派な塔を完成させましょう!', 'In the distant future, on a planet somewhere, lived beings called Tupa. To them, nothing mattered more than building towers. The taller the tower, the grander it is, but build it too high and divine punishment strikes, bringing it crashing down. Become a Tupa and, sometimes careful and sometimes bold, finish the grandest tower of all!'),
    intro_img=('b_tupa.webp', 'トゥーパ', 'intro-tupa'),
    summary=L('『ビビルの塔』は、[[数字カードを同時に出し、高い塔を建てて得点を競うゲームです。]]出した数字の大きさが[[1位と2位]]のプレイヤーは、そのカードを自分の前に重ねて塔を建てます。同じ数字を出したプレイヤーが複数いた場合は[[バッティング]]となり、そのプレイヤーだけが塔を建てます。塔は高いほど高得点を狙えますが、[[6枚になると天罰によって崩れてしまいます。]]手札がなくなったら塔の得点を計算し、最も得点の高かったプレイヤーがラウンドの勝者です。最初に[[2回]]ラウンド勝利をしたプレイヤーがこのゲームの勝者となります。', 'In The Tower of Bibilu, [[players reveal number cards at the same time and build tall towers to score points.]] The players who played the [[highest and second-highest]] numbers stack their cards in front of them to build their towers. If several players played the same number, it is a [[clash]], and only those players build. Taller towers score more, but [[at 6 cards, divine punishment makes them crumble.]] When hands run out, towers are scored and the highest score wins the round. The first player to win [[2]] rounds wins the game.'),
    spec=[(L('人数', 'Players'), L('2〜4人', '2–4')), (L('時間', 'Time'), L('10〜15分', '10–15 min')), (L('年齢', 'Age'), L('6歳から', '6+'))],
    poster='bibilu_poster.jpg',
    # 遊び方:説明シート「ビビルの塔はこんなゲーム!」の4コマ(文はそのまま、[[ ]]はシートの赤字)
    steps=[
        dict(cls='s1', b=L('全員がせーので手札からカードを出し、数字の大きさが[[1位と2位の人]]が出したカードを獲得し、[[手元に塔を建てられる!]]', 'Everyone plays a card at once. The players with the [[1st and 2nd highest numbers]] take their cards and [[build a tower!]]'),
             v='<div class="picks">' + pick(7, 0, '2') + pick(5, 1) + pick(3, 2) + pick(8, 3, '1') + '</div>'),
        dict(cls='s2', b=L('もし同じ数字を出した人がいたら[[バッティング。]][[バッティングした人だけが塔を建てる!]]', 'If anyone played the same number, it is a [[clash.]] [[Only the clashing players build!]]'),
             v='<div class="picks">' + pick(3, 0, 'star') + pick(3, 1, 'star') + pick(10, 2) + pick(2, 3) + '</div>'),
        dict(cls='s3', b=L('塔はどんどん上に重ねていく。ただし、6枚を超えると、[[天罰マークの数だけ下から崩れる!]]', 'Towers keep growing upward. But past 6 cards, [[they crumble from the bottom by the number of punishment marks!]]'),
             v='<div class="lscene">' + ltower([2, 5, 3, 7, 1, 8], fall=4) + '<div class="lnotes"><p class="n1">' + L('<em>6枚目に8を獲得!</em><br>8の天罰マークは<br>4つなので…', '<em>6th card: an 8!</em><br>The 8 has 4<br>marks, so…') + '</p><p class="n2">' + L('<em>下から4枚<br>捨てる!</em>', '<em>Discard 4<br>from the bottom!</em>') + '</p><p class="n3">' + L('上の2枚は残る', 'The top 2 stay') + '</p></div></div>'),
        dict(cls='s4', b=L('手札がなくなったらゲーム終了! [[「塔の1番上の数字×高さ」が最も大きい人が勝ち!]]', 'When hands run out, the game ends! [[Highest “top number × height” wins!]]'),
             v='<div class="lscene">' + ltower([3, 5, 2, 7, 8]) + '<div class="lscore"><p>' + L('8×5=<b>40点!</b>', '8×5=<b>40 pts!</b>') + '</p><span class="hop"><img class="hop-orb" src="{{img:b_tupa_orb.webp}}" alt=""><img class="hop-tok" src="{{img:b_tupa_body.webp}}" alt="トゥーパ"></span></div></div>'),
    ],
    extra_kicker=L('スクープ!', 'Scoop!'),
    extra_title=L('古代の碑文を独占入手!', 'Exclusive: an ancient stele!'),
    extra_html='<p class="extra-text">' + L('トゥーパたちは、この碑文を[[「ビビル」]]という神からのお告げだと信じているらしい。しかし、彼らにも全文は解読できていないという。碑文には何が記されているのか? 続報を待て!', 'The Tupa seem to believe this stele is a message from a god called [[“Bibilu.”]] But even they cannot read all of it. What does it say? Stay tuned!') + '</p>'
               '<div class="moji"><p class="moji-h">' + L('ビビル文字ジェネレータ', 'Bibilu Script Generator') + '<small>ことばつむぎ　みらいつなぐ</small></p>'
               '<div class="moji-demo"><span class="moji-in">びびるのとう</span><span class="moji-arrow" aria-hidden="true">→</span>'
               '<img class="moji-out" src="{{img:g_moji_sample.webp}}" alt="「びびるのとう」をビビル文字にした画像" width="504" height="504" loading="lazy"></div>'
               '<p class="moji-note">' + L('ひらがなを入れると、ビビル文字の碑文ができあがる。', 'Type in hiragana to make your own Bibilu stele.') + '</p>'
               '<a class="btn" href="https://pandakinema.github.io/bibilu-moji/" target="_blank" rel="noopener">' + L('ビビル文字を書いてみる', 'Write in Bibilu') + ' <span aria-hidden="true">↗</span></a></div>',
    extra_img='<img class="stele" src="{{img:b_stele.webp}}" alt="古代の碑文。ビビル文字がびっしりと刻まれている" width="396" height="639" loading="lazy">',
    gallery=[('g_rule.webp', '説明シート「ビビルの塔はこんなゲーム!」', 'Rules summary sheet', 'wide'), ('g_pkg_front.webp', 'パッケージ(表)', 'Box (front)', ''), ('g_pkg_back.webp', 'パッケージ(裏)', 'Box (back)', '')],
    gallery_todo=[('プレイ中の写真', 'Gameplay photos'), ('内容物の写真', 'Components photo')],
    pkg='b_pkg.webp', pkg_size=(498, 760),
    contents=L('カード40枚(1〜10が4セット)、トゥーパ トークン5個、遊び方説明書(JA/EN)各1枚', '40 cards (1–10 ×4), 5 Tupa tokens, rulebook (JA/EN)'),
    price=L('3,300円', '¥3,300'),
    credits=[(L('ゲームデザイン・アートワーク', 'Game Design & Artwork'), L('ゐするぎ', 'Isurugi')), (L('印刷', 'Printing'), L('萬印堂 様', '萬印堂')), (L('トークン製造', 'Tokens'), L('Sui Works 様', 'Sui Works')), ('Special Thanks', L('テストプレイをしてくれた皆さん', 'Everyone who playtested')), (L('発行', 'Published'), L('2026年10月', 'October 2026'))],
)

SEATS = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='76' height='64'%3E%3Cpath d='M8 64V20a14 14 0 0 1 14-14h32a14 14 0 0 1 14 14v44z' fill='black'/%3E%3C/svg%3E\")"

TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#090909">
  <title>{{title}} | PANDA KINEMA</title>
  <meta name="description" content="{{description}}">
  <style>
    :root{--bg:#090909;--line:#2a2a2a;--text:#f4f4f0;--muted:#949494;--soft-text:#c9c9c5;
      --sans:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP","Noto Sans CJK JP",sans-serif;
      --cond:"DIN Condensed","Avenir Next Condensed","Arial Narrow","Helvetica Neue",var(--sans)}
    @supports not (text-box:trim-both cap alphabetic){ :root{--cond:"Avenir Next Condensed","DIN Condensed","Arial Narrow","Helvetica Neue",var(--sans)} }
    /* ===== 作品ごとの色(パッケージ下部のツートンがキーカラー) ===== */
    .key{{{theme}}}

    *{box-sizing:border-box}
    html{scroll-behavior:smooth;scroll-padding-top:calc(76px + env(safe-area-inset-top,0px))}
    body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);-webkit-font-smoothing:antialiased;font-feature-settings:"palt";text-rendering:optimizeLegibility;overflow-x:clip}
    a{color:inherit;text-decoration:none}
    img{display:block;max-width:100%;height:auto}
    a:focus-visible,button:focus-visible{outline:2px solid currentColor;outline-offset:4px}
    .wrap{width:min(1100px,calc(100% - 40px));margin-inline:auto}

    /* ヘッダー:トップページと同じ形 */
    .site-header{position:sticky;top:0;z-index:40;padding-top:env(safe-area-inset-top,0px);background:rgba(27,34,40,.62);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
    .site-header .bar{display:flex;align-items:center;gap:clamp(14px,2.6vw,34px);min-height:56px;padding-inline:max(16px,3vw)}
    .brand{flex:none;display:flex;align-items:center;height:28px}
    .brand img{height:24px;width:auto}
    .site-nav{display:flex;gap:clamp(12px,2.2vw,30px);overflow-x:auto;scrollbar-width:none;color:#f3f2ee;font-family:var(--cond);font-size:clamp(14px,1.6vw,19px);font-weight:700;text-transform:uppercase;letter-spacing:.01em}
    .site-nav::-webkit-scrollbar{display:none}
    .site-nav a{display:flex;align-items:center;height:28px;white-space:nowrap;opacity:.9}
    .site-nav a:hover{opacity:1;text-decoration:underline;text-underline-offset:5px}
    .lang{display:flex;margin-left:auto;border:1.5px solid #f3f2ee;border-radius:2px}
    .lang[hidden]{display:none}
    .lang button{display:flex;align-items:center;height:26px;padding:0 9px;border:0;border-radius:0;background:none;color:#9aa3a9;font:700 16px var(--cond);cursor:pointer}
    .lang button[aria-pressed="true"]{background:#f3f2ee;color:#1b2228}
    .cap{display:block;line-height:1;text-box:trim-both cap alphabetic}
    /* 言語:表示中でない方を隠す */
    html:not(.lang-en) [lang="en"]{display:none !important}
    html.lang-en [lang="ja"]{display:none !important}

    /* ===== 共通パーツ ===== */
    .key{background:var(--k-bg);color:var(--k-ink)}
    .pill{display:inline-block;margin:0;padding:.42em 1.15em .46em;border-radius:999px;font-weight:800;line-height:1.25;letter-spacing:.03em}
    .sec-h{margin-bottom:22px;background:var(--sec-bg);color:var(--sec-ink);font-size:clamp(17px,1.9vw,21px)}
    .pan-h{background:var(--pan-bg);color:var(--pan-ink);font-size:16px}
    /* 見出し:英字ラベル+ピル。左右の飾りだけ作品ごとに差し替え */
    .sec-head{display:flex;flex-direction:column;align-items:center;gap:10px;margin:0 0 24px;text-align:center}
    .en{margin:0;font-size:11px;font-weight:800;letter-spacing:.34em;opacity:.72}
    .sec-head .en{padding-left:.34em}
    .sec-row{display:flex;align-items:center;gap:16px}
    .sec-row::before,.sec-row::after{content:"";flex:none;width:26px;height:26px;background:currentColor;
      -webkit-mask:var(--orn) center/contain no-repeat;mask:var(--orn) center/contain no-repeat}
    .sec-head .sec-h{margin:0}
    .btn{display:inline-flex;align-items:center;gap:.6em;padding:13px 26px;border-radius:999px;background:var(--accent);color:var(--on-accent);font-size:14px;font-weight:800;letter-spacing:.04em;transition:translate .15s ease,box-shadow .15s ease}
    .btn:hover{translate:0 -2px;box-shadow:0 6px 16px rgba(0,0,0,.18)}
    .panel{background:#fff;color:var(--p-ink);border-radius:20px;padding:28px 30px}
    .panel .btn{background:var(--p-ink);color:#fff}
    .spec{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 24px;margin:0}
    .spec div{display:flex;align-items:baseline;gap:7px}
    .spec dt{font-size:12px;opacity:.75}
    .spec dd{margin:0;font-size:17px;font-weight:800}

    /* ===== 1. メインビジュアル(パッケージの絵をそのまま大きく) ===== */
    .hero{position:relative;isolation:isolate;display:flex;flex-direction:column;min-height:clamp(600px,calc(100vh - 64px),920px);overflow:hidden}
    .hero-art{position:absolute;inset:0;z-index:-1;will-change:transform}
    .hero-copy{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;padding:24px 20px 40px}
    .crumb{display:flex;justify-content:space-between;width:100%;max-width:1100px;font-size:11px;letter-spacing:.12em;opacity:.8}
    .crumb p{margin:0}
    .hero-main{margin-top:auto;display:flex;flex-direction:column;align-items:center;padding-top:24px}
    .hero h1{margin:0}
    .billing{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:14px 28px;margin-top:26px}
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      .hero h1{animation:rise .9s cubic-bezier(.2,.8,.2,1) .45s both}
      .billing{animation:rise .8s ease .8s both}
      @keyframes rise{from{opacity:0;translate:0 16px}}
    }
{{hero_css}}

    /* ===== 2. 動画:映画館のスクリーンと客席 ===== */
    .cinema{position:relative;isolation:isolate;padding:64px 0 80px;overflow:hidden;background:var(--k-bg)}
    .screen-wrap{position:relative;max-width:860px;margin-inline:auto}
    .vplayer{position:relative;max-width:860px;margin-inline:auto}
    .vtrack{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;background:#000;box-shadow:0 0 0 0 rgba(var(--glow),0);transition:box-shadow .8s ease}
    /* 触れたときだけスクリーンが光る(ホバー・キーボードのフォーカス・再生中) */
    .vplayer:hover .vtrack,.vtrack:focus-within,.vtrack.playing{box-shadow:0 0 50px 2px rgba(255,255,255,.22)}
    .vtrack::-webkit-scrollbar{display:none}
    .vslide{flex:0 0 100%;scroll-snap-align:center;margin:0;position:relative;aspect-ratio:16/9;overflow:hidden}
    .vposter{all:unset;position:absolute;inset:0;cursor:pointer;display:block}
    .vposter[disabled]{cursor:default}
    .vposter img{width:100%;height:100%;object-fit:cover}
    .vplay{position:absolute;left:50%;top:50%;translate:-50% -50%;display:grid;place-items:center;width:72px;height:72px;border-radius:50%;background:rgba(255,255,255,.94);color:#111;font-size:24px;padding-left:4px;box-shadow:0 6px 20px rgba(0,0,0,.25);transition:scale .2s ease}
    .vposter:not([disabled]):hover .vplay{scale:1.08}
    .vposter[disabled] .vplay{opacity:.5}
    .vmeta{position:absolute;right:14px;top:14px;display:flex;align-items:center;gap:10px;padding:7px 14px;border-radius:999px;background:rgba(0,0,0,.66);color:#fff;font-size:13px;font-weight:800}
    .vsoon{padding:1px 8px;border-radius:999px;background:rgba(255,255,255,.2);font-size:11px;font-weight:400;letter-spacing:.1em}
    .vslide iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
    .vnav{position:absolute;top:50%;translate:0 -50%;width:44px;height:44px;border:0;border-radius:50%;background:#fff;color:#111;font-size:22px;line-height:1;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.3);transition:opacity .2s ease}
    .vnav.prev{left:-22px}.vnav.next{right:-22px}
    .vnav[disabled]{opacity:0;pointer-events:none}
    .vdots{display:flex;justify-content:center;gap:8px;margin-top:18px}
    /* 画面幅いっぱいの黒帯=スクリーン */
    .cinema{padding-top:80px;padding-bottom:76px}
    .cinema .sec-head{margin-bottom:28px}
    .screen-band{background:#070707;padding:34px 0}
    .cinema .vplayer{max-width:none;width:min(1400px,calc(100% - 120px));margin-inline:auto}
    .vdots button{display:flex;align-items:center;gap:8px;padding:6px 14px;border:0;border-radius:999px;background:transparent;color:#fff;font:inherit;font-size:13px;font-weight:700;opacity:.6;cursor:pointer}
    .vdots button::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
    .vdots button[aria-current="true"]{opacity:1;background:color-mix(in srgb,currentColor 12%,transparent)}
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      .js .cinema .vposter img{filter:brightness(.35);transition:filter 1.2s ease .5s}
      .js .cinema.on .vposter img{filter:none}
    }

    /* ===== 帯:キーカラー2色を交互に(パッケージ下部のツートン) ===== */
    .band{position:relative;padding:68px 0 72px}
    .band.tex{padding:86px 0 90px}
    .band>.wrap{position:relative;z-index:1}
    .band-c{z-index:2;background:var(--b2-bg);color:var(--b2-ink);
      --sec-bg:var(--b2-ink);--sec-ink:var(--b2-bg);--accent:var(--b2-ink);--on-accent:var(--b2-bg)}
    /* ビビル文字の帯(素材 bibilu_line):色の境目には置かず、紺の帯の内側に */
    .gband{position:absolute;left:0;right:0;z-index:1;height:var(--band-h);background:var(--b2-bg);pointer-events:none;
      -webkit-mask:var(--band) repeat-x;mask:var(--band) repeat-x;-webkit-mask-size:auto var(--band-h);mask-size:auto var(--band-h);
      -webkit-mask-position:calc(var(--sx,0) * 1px) 0;mask-position:calc(var(--sx,0) * 1px) 0}
    .gband.top{top:18px}
    .gband.bottom{bottom:18px;-webkit-mask-position:calc(var(--sx,0) * -1px) 0;mask-position:calc(var(--sx,0) * -1px) 0}
    .tex{background-image:var(--tex-c);background-size:var(--tex-size)}
    .band-c{background-image:var(--b2-img,none);background-size:var(--b2-size,auto)}
    .gband{display:var(--band-d,block)}
    .cast{display:flex;align-items:flex-end;justify-content:center;gap:4px;width:min(520px,90vw)}
    .cast img{animation:lhop2 3.6s cubic-bezier(.3,.6,.4,1) infinite;animation-delay:calc(var(--i) * -.9s)}
    .fig-wrap:has(.cast){width:auto}
    @media (max-width:650px){ .cast{width:min(360px,88vw)} }

    /* ===== 3. キャラクター+取説の導入文 ===== */
    .chara-in{display:flex;flex-direction:column;align-items:center;gap:36px;text-align:center}
    .story{display:flex;flex-direction:column;align-items:center}
    .chara-fig{margin:0;display:flex;flex-direction:column;align-items:center}
    .fig-wrap{position:relative;width:min(160px,40vw);margin-top:14px}
    .tupa{position:relative;width:100%;aspect-ratio:1164/1562}
    .tupa .body{position:absolute;left:0;bottom:0;width:100%}
    .tupa .orb{position:absolute;left:50%;top:0;width:30.4%;translate:-50% 0}
    .tupa .orb img{width:100%;filter:drop-shadow(0 0 8px rgba(var(--orb-glow),.5))}
    /* ゲーム中の姿:丸いバッジ(ファミコンサイトのドット絵バッジと同じ役目) */
    .badge{position:absolute;right:-16%;bottom:-2%;display:grid;place-items:center;width:38%;aspect-ratio:1;border:4px solid var(--b2-ink);border-radius:50%;background:#fff;box-shadow:0 10px 20px -8px rgba(0,0,0,.3)}
    .badge img{width:70%}
    .chara-fig figcaption{display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:22px;text-align:center}
    /* キャラクターは1体ずつ。◀▶で切り替え */
    .chara-slides{display:grid}
    .chara-slide{grid-area:1/1;display:flex;flex-direction:column;align-items:center;visibility:hidden;opacity:0;transition:opacity .35s ease,visibility 0s linear .35s}
    .chara-slide.cur{visibility:visible;opacity:1;transition:opacity .35s ease,visibility 0s}
    .chara-slide .solo{width:100%;height:auto;animation:lhop2 3.6s cubic-bezier(.3,.6,.4,1) infinite}
    .fig-wrap:has(.solo){width:min(220px,52vw)}
    .chara-fig{position:relative}
    .chara-fig:has(.cnav){padding-inline:58px}
    .cnav{position:absolute;top:min(110px,26vw);z-index:2;display:grid;place-items:center;width:40px;height:40px;padding:0;border:0;border-radius:50%;background:var(--b2-ink);cursor:pointer;translate:0 -50%}
    .cnav::before{content:"";border-style:solid;border-color:transparent}
    .cnav.prev{left:0}.cnav.next{right:0}
    .cnav.prev::before{border-width:7px 10px 7px 0;border-right-color:var(--b2-bg);margin-right:3px}
    .cnav.next::before{border-width:7px 0 7px 10px;border-left-color:var(--b2-bg);margin-left:3px}
    .cnav:hover{scale:1.08}
    .cdots{display:flex;justify-content:center;gap:7px;margin-top:14px}
    .cdots i{width:7px;height:7px;border-radius:50%;background:var(--b2-ink);opacity:.3}
    .cdots i.on{opacity:1}
    .js-only{display:none !important}
    .js .js-only.cnav{display:grid !important}
    .js .js-only.cdots{display:flex !important}
    .chara-note{font-size:13.5px;line-height:1.8;font-weight:700;word-break:auto-phrase}
    .chara-name{display:inline-block;padding:.32em 1.3em .36em;border-radius:999px;background:var(--b2-ink);color:var(--b2-bg);font-size:20px;font-weight:900;letter-spacing:.12em}
    .chara h2{margin:0 0 20px;font-size:clamp(24px,3.1vw,34px);font-weight:900;letter-spacing:.02em;line-height:1.35}
    .story>p:not(.en){margin:0;font-size:15.5px;line-height:2.05;max-width:34em;font-weight:500;word-break:auto-phrase}
    .story .en{margin-bottom:12px;padding-left:.34em}

    /* ===== 4. どんなゲーム?(目的の要約+図) ===== */
    .summary{margin:0 auto 26px;max-width:44em;font-size:16px;line-height:1.95;font-weight:700;text-align:center;word-break:auto-phrase}
    .summary em{font-style:normal;color:var(--hl)}
    /* 横に流れるカード(画面の端まで。左端は本文の幅にそろえる) */
    .flow{--gut:max(20px,calc((100vw - 1100px) / 2));--card:320px;--gap:46px;margin-inline:calc(50% - 50vw)}
    .steps{list-style:none;margin:0;display:flex;gap:var(--gap);overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;scroll-padding-inline:var(--gut);
      padding:8px 20px 16px var(--gut);scrollbar-width:none;counter-reset:step;cursor:grab}
    .steps::-webkit-scrollbar{display:none}
    .steps.drag{cursor:grabbing;scroll-snap-type:none;user-select:none}
    .step{counter-increment:step;position:relative;flex:0 0 var(--card);scroll-snap-align:start;display:flex;flex-direction:column;gap:12px;padding:16px 16px 16px;border-radius:20px;background:#fff;color:var(--p-ink)}
    .step:not(:last-child)::after{content:"";position:absolute;left:calc(100% + (var(--gap) - 14px) / 2);top:calc(50% - 10px);border-style:solid;border-width:10px 0 10px 14px;border-color:transparent transparent transparent var(--k-ink)}
    .step-head{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}
    .snum{display:grid;place-items:center;width:48px;height:46px;padding-top:4px;background:var(--p-ink);color:var(--k-ink);
      -webkit-mask:var(--snum) center/contain no-repeat;mask:var(--snum) center/contain no-repeat;font:900 22px/1 Georgia,"Times New Roman",serif}
    .step-lead{margin:0 4px;font-size:15px;line-height:1.7;font-weight:800;text-align:center;word-break:auto-phrase;text-wrap:pretty}
    .step-lead em{font-style:normal;color:#d4242b}   /* 取説の赤字 */
    .viz{--card-w:66px;position:relative;display:flex;align-items:center;justify-content:center;height:206px;padding:12px;border-radius:14px;background:var(--soft);overflow:hidden}
    .flow-ui{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:22px}
    .flow-ui[hidden]{display:none}
    .flow-bar{position:relative;width:min(220px,40vw);height:4px;border-radius:4px;background:color-mix(in srgb,var(--k-ink) 22%,transparent);overflow:hidden}
    .flow-bar span{position:absolute;top:0;bottom:0;left:var(--l,0%);width:var(--w,40%);border-radius:4px;background:var(--k-ink)}
    .fnav{width:42px;height:42px;border:0;border-radius:50%;background:var(--k-ink);color:var(--k-bg);font-size:22px;line-height:1;cursor:pointer;transition:opacity .2s ease}
    .fnav[disabled]{opacity:.3;cursor:default}
    /* ===== 遊び方の図:説明シートの4コマ。CSSだけで、くり返し動く ===== */
    .picks{display:flex;justify-content:center;gap:7px;padding-bottom:36px}
    .pk{position:relative;display:block;--card-w:58px}
    .lf{position:relative;display:block;width:var(--card-w);transform-style:preserve-3d}
    .lf .c{width:100%;border-radius:5px;backface-visibility:hidden;-webkit-backface-visibility:hidden}
    .lf .back{position:absolute;inset:0;transform:rotateY(180deg)}
    .pk.sel::after{content:"";position:absolute;inset:-4px;border:3px solid #d4242b;border-radius:8px;pointer-events:none}
    .crown{position:absolute;left:50%;top:calc(100% + 9px);translate:-50% 0;width:30px;height:26px;padding-top:7px;background:#f2d756;color:#163f53;
      clip-path:polygon(0 100%,0 12%,26% 42%,50% 4%,74% 42%,100% 12%,100% 100%);font:900 14px/1 Georgia,serif;text-align:center}
    .star{position:absolute;left:50%;top:calc(100% + 7px);translate:-50% 0;width:30px;height:30px;background:#f2d756;
      clip-path:polygon(50% 0,61.8% 35%,98% 35%,68.5% 57%,79.4% 91%,50% 70%,20.6% 91%,31.5% 57%,2% 35%,38.2% 35%)}
    .lscene{display:flex;align-items:flex-end;justify-content:center;gap:16px;width:100%;height:100%}
    .ltw{--cw:46px;--step:17px;position:relative;padding:6px 6px 6px 24px;border-radius:9px;background:#2b9fd9}
    .ltower{position:relative;width:var(--cw);height:calc(var(--cw) * 1.4 + (var(--n) - 1) * var(--step))}
    .lt{position:absolute;left:0;bottom:calc(var(--i) * var(--step));width:var(--cw);border-radius:4px;box-shadow:0 -2px 5px rgba(0,0,0,.2)}
    .lt.fall{opacity:.3}
    .ruler{position:absolute;left:0;bottom:6px;width:24px;margin:0;padding:0;list-style:none}
    .ruler li{position:absolute;left:0;right:0;bottom:calc(var(--i) * var(--step) + 2px);color:#fff;font:900 12px/16px Georgia,serif;text-align:center}
    .manual-link{display:flex;flex-direction:column;align-items:center;gap:12px;margin-top:30px;text-align:center}
    .manual-link p{margin:0;font-size:14px;font-weight:700;opacity:.85}
    /* STORYの最後:取説の「スクープ!」欄を切り抜き記事ふうに */
    .scoop{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:36px;align-items:center;width:min(780px,100%);margin:6px auto 0;padding:34px 40px;border-radius:6px;
      background:var(--scoop-bg,#e8d3a0);color:var(--scoop-ink,#163f53);box-shadow:0 22px 36px -22px rgba(0,0,0,.45);rotate:-1deg}
    .scoop:not(:has(.stele)){grid-template-columns:1fr}
    .scoop-text{display:flex;flex-direction:column;align-items:center;gap:14px}
    .scoop .stele{width:160px;rotate:2deg}
    .scoop .extra-kicker{margin:0}
    .moji{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%;margin-top:8px;padding-top:20px;border-top:2px dashed rgba(22,63,83,.25)}
    .moji-h{margin:0;font-size:17px;font-weight:900;line-height:1.4}
    .moji-h small{display:block;font-size:11px;font-weight:700;letter-spacing:.2em;opacity:.7}
    .moji-demo{display:flex;align-items:center;justify-content:center;gap:12px}
    .moji-in{padding:9px 14px;border:2px solid rgba(22,63,83,.35);border-radius:8px;background:#fffaf0;font-size:15px;font-weight:700}
    .moji-arrow{font-size:20px;font-weight:900;opacity:.6}
    .moji-out{width:150px;border-radius:6px;box-shadow:0 8px 16px -8px rgba(0,0,0,.4)}
    .moji-note{margin:0;font-size:13px;font-weight:700}
    /* フォトギャラリー */
    .gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
    .gallery figure{margin:0}
    .gallery .wide{grid-column:span 2}
    .gitem{display:block;width:100%;height:100%;min-height:220px;padding:14px;border:0;border-radius:16px;background:#fff;cursor:zoom-in}
    .gitem img{width:100%;height:100%;max-height:300px;object-fit:contain}
    .gph{display:grid;place-items:center;min-height:220px;height:100%;border:2px dashed color-mix(in srgb,var(--b2-ink) 30%,transparent);border-radius:16px;font-size:13px;font-weight:700;opacity:.75}
    .lb{max-width:none;max-height:none;padding:0;border:0;background:transparent;overflow:visible}
    .lb::backdrop{background:rgba(0,0,0,.86)}
    .lb img{max-width:92vw;max-height:88vh;width:auto;height:auto;border-radius:8px}
    .lb-x{position:absolute;top:-16px;right:-16px;width:40px;height:40px;border:0;border-radius:50%;background:#fff;color:#111;font-size:22px;cursor:pointer}
    .lnotes{position:relative;width:118px;align-self:stretch}
    .lnotes p{position:absolute;left:0;right:0;margin:0;font-size:11.5px;font-weight:800;line-height:1.45;text-align:left}
    .lnotes em{font-style:normal;color:#d4242b}
    .lnotes .n1{top:4px}
    .lnotes .n2{top:62px;font-size:16px;line-height:1.25}
    .lnotes .n3{bottom:4px;color:#2b9fd9;font-size:13px}
    .lscore{display:flex;flex-direction:column;align-items:center;gap:8px}
    .lscore p{margin:0;color:#d4242b;font-size:22px;font-weight:900;line-height:1.1;text-align:center;white-space:nowrap}
    .lscore b{display:block;font-size:34px}
    .hop{position:relative;display:block;width:70px;padding-top:30px}
    .hop-orb{position:absolute;left:50%;top:0;width:24px;translate:-50% 0;filter:drop-shadow(0 0 6px rgba(var(--orb-glow),.7))}
    .hop-tok{width:100%}

    /* 1. 扇に開いた手札 */
    .fan{display:flex;align-items:center;justify-content:center;padding-top:6px}
    .fan .flip{--card-w:70px;margin-left:-14px}
    .fan .flip:first-child{margin-left:0}
    .fan .flip:nth-child(1){rotate:-12deg;translate:0 12px}
    .fan .flip:nth-child(2){rotate:-4deg}
    .fan .flip:nth-child(3){rotate:4deg}
    .fan .flip:nth-child(4){rotate:12deg;translate:0 12px}
    .c{width:var(--card-w);border-radius:6px;box-shadow:0 5px 12px rgba(0,0,0,.15)}
    .row-cards{display:flex;align-items:flex-end;justify-content:center;gap:30px}
    .row-cards figure{margin:0;display:flex;flex-direction:column;align-items:center}
    .row-cards figcaption{margin-top:12px;padding:3px 12px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:12px;font-weight:800}
    .pair,.lead-pair{display:flex;align-items:flex-end;gap:10px}
    .lead-card{width:62px;border-radius:5px;rotate:-8deg;box-shadow:0 3px 8px rgba(0,0,0,.14)}
    .flip{position:relative;display:block;width:var(--card-w);transform-style:preserve-3d}
    .flip .c{width:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden}
    .flip .back{position:absolute;inset:0;transform:rotateY(180deg)}
    .judge{display:grid;gap:12px;width:100%}
    .jrow{display:grid;grid-template-columns:46px auto minmax(0,1fr);align-items:center;gap:14px}
    .jlabel{display:grid;place-items:center;height:28px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:13px;font-weight:800}
    .jcards{display:flex;gap:8px}
    .jcards .c{width:56px;box-shadow:0 2px 6px rgba(0,0,0,.12)}
    .jrule{font-size:14px;font-weight:800;line-height:1.45}
    .win{position:relative;display:block;border-radius:6px;outline:3px solid var(--pan-bg);outline-offset:1px}
    .win b{position:absolute;left:50%;bottom:-9px;translate:-50% 0;padding:0 6px;border-radius:999px;background:var(--pan-bg);color:var(--pan-ink);font-size:10px;line-height:15px;letter-spacing:.06em}
    .take{display:flex;align-items:flex-end;gap:18px;padding-top:30px}
    .picked{position:relative;display:block;translate:0 -20px;rotate:4deg}
    .picked b{position:absolute;left:50%;top:-34px;translate:-50% 0;padding:3px 12px;border-radius:999px;background:var(--pan-bg);color:var(--pan-ink);font-size:13px;white-space:nowrap}
    .collect{display:flex;align-items:flex-end;justify-content:center;gap:22px;width:100%;padding-top:34px}
    .hand{position:relative;display:flex;gap:8px}
    .hand .c{width:78px}
    .nico{position:absolute;left:50%;top:-34px;translate:-80% 0;padding:3px 13px;border-radius:999px;background:#ec6ea6;color:#fff;font-size:14px;font-weight:800;white-space:nowrap}
    .winner{position:relative;display:flex;align-items:flex-end;gap:6px}
    .w-bird{width:110px}
    .marker{width:46px;margin-bottom:4px}
    .bubble{position:absolute;left:-4px;top:-38px;padding:4px 13px 5px;border:2px solid var(--p-ink);border-radius:999px;background:#fff;font-size:15px;font-weight:800;white-space:nowrap}
    .rank{display:grid;gap:8px;width:100%}
    .rank>div{padding:6px 8px 8px;border-radius:10px;background:#fff}
    .rank p{margin:0;font-size:11.5px;font-weight:800;text-align:center}
    .rank .row{display:flex;justify-content:center;gap:5px;padding-top:19px}
    .slot{position:relative;display:block;width:22%}
    .slot .c{width:100%}
    .slot:not(.on) .c{opacity:.45}
    .slot b{position:absolute;left:50%;top:-18px;translate:-50% 0;padding:0 6px;border-radius:999px;background:#f2d756;color:#163f53;font-size:10px;line-height:16px;white-space:nowrap}
    .slot b:empty{display:none}
    .tower-scene{display:flex;align-items:flex-end;justify-content:center;gap:20px;width:100%;height:100%;padding-bottom:2px;border-bottom:2px solid color-mix(in srgb,var(--p-ink) 25%,transparent)}
    .tower{--cw:56px;--step:22px;position:relative;width:var(--cw);height:calc(var(--cw) * 1.4 + (var(--n) - 1) * var(--step))}
    .tc{position:absolute;left:0;bottom:calc(var(--i) * var(--step));width:var(--cw);border-radius:5px;box-shadow:0 -2px 6px rgba(0,0,0,.14)}
    .tlabel{margin-bottom:8px;font-size:12px;font-weight:800;line-height:1.5}
    .tlabel b{display:block;margin-top:4px;color:#d4242b;font-size:18px;line-height:1.3}
    .formula{margin-bottom:6px;font-size:18px;font-weight:800;white-space:nowrap}
    .formula small{display:block;margin-bottom:6px;font-size:11px;line-height:1.45;color:#d4242b}
    .formula b{display:block;font-size:32px;line-height:1.1}
    .discard{display:flex;align-items:center;justify-content:center;gap:26px;padding-top:26px}
    .pile{position:relative;width:76px;aspect-ratio:5/7}
    .pc{position:absolute;inset:0}
    .pc .c{width:100%}
    .ptag{position:absolute;left:50%;top:-34px;translate:-50% 0;z-index:2;padding:2px 12px;border-radius:999px;background:#d4242b;color:#fff;font-size:13px;font-weight:800;white-space:nowrap}
    .loop{font-size:44px;font-weight:800;line-height:1;color:var(--p-ink);opacity:.35}
    .tokens{display:flex;gap:5px;margin-top:8px}
    .tokens img{width:34px}

    /* おまけ(もう1色の帯にじか置き) */
    .extra-body{display:flex;flex-direction:column;align-items:center;gap:22px;max-width:820px;margin-inline:auto;text-align:center}
    .extra-kicker{margin:0 0 -10px;padding:3px 14px;border-radius:999px;background:#d4242b;color:#fff;font-size:13px;font-weight:800}
    .extra-title{margin:0;font-size:clamp(21px,2.6vw,28px);font-weight:900}
    .extra-text{margin:0;font-size:15.5px;line-height:1.95;font-weight:700;max-width:30em;word-break:auto-phrase}
    .extra-text em{font-style:normal;color:#d4242b}
    .extra-img{width:100%;border-radius:18px}
    .stele-wrap{display:flex;align-items:center;justify-content:center;gap:44px;text-align:left}
    .stele{width:min(190px,46vw);border-radius:10px;box-shadow:0 18px 30px -16px rgba(0,0,0,.35)}
    .stele-wrap p{margin:0 0 20px;font-size:15.5px;line-height:1.9;font-weight:700;max-width:24em}

    /* 購入 */
    .buy-box{display:grid;grid-template-columns:minmax(140px,210px) minmax(0,1fr);gap:44px;align-items:center;padding:34px 40px}
    .buy-box .pkg{filter:drop-shadow(0 16px 18px rgba(0,0,0,.2))}
    .buy-box>div{text-align:center}
    .buy-logo{width:min(300px,100%);margin:0 auto 16px}
    .buy-box .spec{justify-content:center}
    .contents{margin:10px 0 0;font-size:13px;opacity:.8}
    .price{margin:12px 0 0;font-size:22px;font-weight:800}
    .price small{margin-left:.5em;font-size:12px;font-weight:400;opacity:.7}
    .buy-box .btn{margin-top:18px}

    /* ===== 5. クレジット(黒・映画のエンドロール) ===== */
    .credits{padding:80px 0 20px;text-align:center}
    .credits-logo{width:min(300px,64vw);margin:0 auto 52px}
    .roll{display:grid;gap:18px;margin:0 auto;max-width:640px}
    .roll div{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:baseline}
    .roll dt{text-align:right;font-size:11px;letter-spacing:.14em;color:var(--muted)}
    .roll dd{margin:0;text-align:left;font-size:15px;font-weight:700}

    /* ===== 6. ほかの作品 ===== */
    .dotline{height:4px;margin-top:56px;background:radial-gradient(circle,rgba(205,210,212,.7) 1.6px,transparent 2px) 0 50%/16px 4px repeat-x}
    .lineup-sec{padding-top:34px}
    .lineup-h{margin:0 0 14px;font-family:var(--cond);font-size:clamp(26px,3vw,36px);font-weight:700;letter-spacing:.01em;text-transform:uppercase}
    .bg-row{list-style:none;margin:0;padding:0 0 6px;display:flex;gap:14px;overflow-x:auto;scrollbar-width:none}
    .bg-row::-webkit-scrollbar{display:none}
    .bg-row li{flex:none}
    .bg-card{position:relative;display:block;height:230px;aspect-ratio:560/790;border-radius:10px;overflow:hidden;transition:translate .2s ease}
    .bg-card:hover{translate:0 -4px}
    .bg-card img{width:100%;height:100%;object-fit:cover}
    .bg-new{position:absolute;left:50%;bottom:8px;translate:-50% 0;display:inline-flex;align-items:center;height:20px;padding:0 7px;border-radius:4px;background:#e8343d;color:#fff;font-size:11px;font-weight:800;letter-spacing:.08em;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.3)}
    .site-footer{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:56px;padding:22px 0 calc(28px + env(safe-area-inset-bottom,0px));background:radial-gradient(circle,rgba(205,210,212,.7) 1.6px,transparent 2px) 0 0/16px 4px repeat-x;font-size:12px;color:#cdd2d4}
    .site-footer a{font-family:var(--cond);font-size:14px;letter-spacing:.08em}

    /* ===== 追従するBOOTHボタン(メインビジュアルと購入欄が見えていない間だけ) ===== */
    .fab{position:fixed;right:max(18px,env(safe-area-inset-right,0px));bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:30;
      display:flex;align-items:center;gap:.5em;min-height:48px;padding:0 22px 0 70px;border:2px solid var(--on-accent);border-radius:999px;
      background:var(--accent);color:var(--on-accent);font-size:14px;font-weight:800;letter-spacing:.04em;box-shadow:0 12px 28px rgba(0,0,0,.32);
      opacity:0;translate:0 18px;visibility:hidden;transition:opacity .2s ease,translate .25s ease,visibility 0s linear .25s}
    .fab.show{opacity:1;translate:0 0;visibility:visible;transition:opacity .25s ease,translate .45s cubic-bezier(.3,1.6,.5,1),visibility 0s}
    .fab img{position:absolute;left:14px;bottom:7px;width:44px;filter:drop-shadow(0 4px 6px rgba(0,0,0,.3));transition:rotate .2s ease,translate .2s ease}
    .fab:hover img{translate:0 -4px}

    /* ===== スクロールの演出(見えたら再生、画面の外に出たら元に戻る) ===== */
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      @keyframes float{to{translate:0 calc(var(--s,24px) * -.45)}}
      /* 遊び方の図:くり返し(1・2コマ=6秒、3コマ=8秒、4コマ=6秒)。スクリプトもスクロールもいらない */
      .lf{animation:lflip 6s cubic-bezier(.3,1.2,.4,1) infinite;animation-delay:calc(var(--i) * .12s + var(--o,0s))}
      .s2{--o:.5s}
      @keyframes lflip{0%,10%{transform:rotateY(180deg)}22%,86%{transform:rotateY(0deg)}96%,100%{transform:rotateY(180deg)}}
      .pk.sel::after{animation:lring 6s ease infinite;animation-delay:var(--o,0s)}
      .crown,.star{animation:lmark 6s ease infinite;animation-delay:calc(var(--o,0s) + var(--i) * .08s)}
      @keyframes lring{0%,30%{opacity:0}36%,84%{opacity:1}90%,100%{opacity:0}}
      @keyframes lmark{0%,32%{opacity:0;scale:.3}38%{opacity:1;scale:1.18}43%,84%{opacity:1;scale:1}90%,100%{opacity:0;scale:.6}}
      .s4 .lt{animation:lbuild 6s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .22s)}
      @keyframes lbuild{0%{opacity:0;translate:0 -46px}6%{opacity:1;translate:0 0}78%{opacity:1;translate:0 0}84%,100%{opacity:0;translate:0 0}}
      .s4 .lscore p{animation:lpop 6s ease infinite}
      @keyframes lpop{0%,28%{opacity:0;scale:.4}34%{opacity:1;scale:1.15}38%,80%{opacity:1;scale:1}86%,100%{opacity:0;scale:.8}}
      .s4 .hop{animation:lhop 1.6s cubic-bezier(.3,.6,.4,1) infinite}
      @keyframes lhop{0%,55%,100%{translate:0 0}72%{translate:0 -12px}}
      .s4 .hop-orb{animation:float 2.4s ease-in-out infinite alternate;--s:14px}
      .s3 .lt{animation:l3drop 8s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .25s)}
      .s3 .lt.fall{opacity:1;animation-name:l3fall}
      .s3 .lt.stay{animation-name:l3stay}
      @keyframes l3drop{0%{opacity:0;translate:0 -46px}6%{opacity:1;translate:0 0}78%{opacity:1;translate:0 0}84%,100%{opacity:0;translate:0 0}}
      @keyframes l3fall{0%{opacity:0;translate:0 -46px;rotate:0deg}6%{opacity:1;translate:0 0;rotate:0deg}40%{opacity:1;translate:0 0;rotate:0deg}43%{opacity:1;translate:-3px 0;rotate:-3deg}
        50%,100%{opacity:0;translate:calc((var(--i) - 1.5) * 24px) 56px;rotate:calc((var(--i) - 1.5) * 16deg)}}
      @keyframes l3stay{0%{opacity:0;translate:0 -46px}6%{opacity:1;translate:0 0}52%{translate:0 0}58%{translate:0 calc(var(--fall) * var(--step) + 4px)}61%{translate:0 calc(var(--fall) * var(--step))}
        78%{opacity:1;translate:0 calc(var(--fall) * var(--step))}84%,100%{opacity:0;translate:0 calc(var(--fall) * var(--step))}}
      .s3 .n1{animation:ln1 8s ease infinite}.s3 .n2{animation:ln2 8s ease infinite}.s3 .n3{animation:ln3 8s ease infinite}
      @keyframes ln1{0%,22%{opacity:0;translate:0 6px}26%,80%{opacity:1;translate:0 0}86%,100%{opacity:0}}
      @keyframes ln2{0%,39%{opacity:0;scale:.5}43%{opacity:1;scale:1.12}46%,80%{opacity:1;scale:1}86%,100%{opacity:0}}
      @keyframes ln3{0%,68%{opacity:0;translate:0 6px}72%,80%{opacity:1;translate:0 0}86%,100%{opacity:0}}
      /* キャラクター:ときどき跳ねる */
      .tupa{animation:lhop2 3.6s cubic-bezier(.3,.6,.4,1) infinite}
      @keyframes lhop2{0%,78%,100%{translate:0 0}86%{translate:0 -10px}92%{translate:0 0}96%{translate:0 -4px}}
      .js .sec-row::before,.js .sec-row::after{scale:0;translate:0 10px}
      .js .sec-head.on .sec-row::before,.js .sec-head.on .sec-row::after{scale:1;translate:0 0;transition:scale .5s cubic-bezier(.3,1.7,.5,1) .25s,translate .5s cubic-bezier(.3,1.7,.5,1) .25s}
      .js .sec-head.on .sec-row::after{transition-delay:.35s}
      .tupa .orb img{animation:float 2.8s ease-in-out infinite alternate;--s:16px}
      .js .chara-fig .tupa .body{opacity:0;translate:0 50px;scale:.86}
      .js .chara-fig.on .tupa .body{opacity:1;translate:0 0;scale:1;transition:opacity .25s ease .1s,translate .7s cubic-bezier(.3,1.7,.5,1) .1s,scale .7s cubic-bezier(.3,1.7,.5,1) .1s}
      .js .chara-fig .tupa .orb{opacity:0;translate:-50% -40px;scale:.4}
      .js .chara-fig.on .tupa .orb{opacity:1;translate:-50% 0;scale:1;transition:opacity .5s ease .7s,translate .9s cubic-bezier(.2,.9,.2,1) .7s,scale .6s cubic-bezier(.3,1.6,.5,1) .7s}
      .js .story>*{opacity:0;translate:0 22px}
      .js .story.on>*{opacity:1;translate:0 0;transition:opacity .6s ease,translate .7s cubic-bezier(.2,.8,.2,1)}
      .js .story.on>:nth-child(2){transition-delay:.15s}
      .js .story.on>:nth-child(3){transition-delay:.35s}
      .js .story.reveal{opacity:1;translate:0 0}
      .js .discard .ptag,.js .discard .loop{scale:0}
      .js .on .discard .ptag{animation:pop .4s cubic-bezier(.3,1.8,.5,1) .2s both}
      .js .on .discard .loop{animation:pop .45s cubic-bezier(.3,1.8,.5,1) 1s both}
      .js .chara-fig .chara-name{scale:0}
      .js .chara-fig.on .chara-name{scale:1;transition:scale .45s cubic-bezier(.3,1.8,.5,1) 1.05s}
      .js .chara-fig .badge{scale:0;rotate:-40deg}
      .js .chara-fig.on .badge{scale:1;rotate:0deg;transition:scale .5s cubic-bezier(.3,1.7,.5,1) 1.2s,rotate .5s cubic-bezier(.3,1.7,.5,1) 1.2s}
      .js .chara-fig .chara-note{opacity:0}
      .js .chara-fig.on .chara-note{opacity:1;transition:opacity .5s ease 1.3s}
      .js .reveal{opacity:0;translate:0 28px;transition:opacity .5s ease,translate .6s cubic-bezier(.2,.8,.2,1)}
      .js .reveal.on{opacity:1;translate:0 0}
      @keyframes deal{from{opacity:0;translate:-40px 16px;rotate:-14deg}to{opacity:1;translate:0 0;rotate:0deg}}
      @keyframes deal-dim{from{opacity:0;translate:-40px 16px;rotate:-14deg}to{opacity:.45;translate:0 0;rotate:0deg}}
      @keyframes pop{from{scale:0}to{scale:1}}
      @keyframes fadein{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
      .js .viz .deal,.js .viz .lead-card,.js .viz .jcards .c,.js .viz .slot .c{opacity:0}
      .js .on .viz .deal,.js .on .viz .lead-card,.js .on .viz .jcards .c,.js .on .viz .slot .c{animation:deal .5s cubic-bezier(.2,.9,.3,1.2) both;animation-delay:calc(.2s + var(--i,0) * .12s)}
      .js .on .viz .slot:not(.on) .c{animation-name:deal-dim}
      .js .viz .flip{transform:rotateY(180deg)}
      .js .on .viz .flip{transform:rotateY(0deg);transition:transform .7s cubic-bezier(.3,1.2,.4,1);transition-delay:calc(.7s + var(--i,0) * .1s)}
      .js .viz .win b,.js .viz .picked b,.js .viz .slot b,.js .viz .nico,.js .viz .bubble,.js .viz .marker,.js .viz figcaption{scale:0}
      .js .on .viz .win b{animation:pop .4s cubic-bezier(.3,1.8,.5,1) both;animation-delay:calc(1s + var(--i,0) * .1s)}
      .js .on .viz .slot b{animation:pop .4s cubic-bezier(.3,1.8,.5,1) .9s both}
      .js .on .viz figcaption{animation:pop .35s cubic-bezier(.3,1.8,.5,1) .5s both}
      .js .viz .picked{translate:0 0;rotate:0deg}
      .js .on .viz .picked{translate:0 -20px;rotate:4deg;transition:translate .5s cubic-bezier(.3,1.5,.5,1) 1s,rotate .5s ease 1s}
      .js .on .viz .picked b{animation:pop .4s cubic-bezier(.3,1.8,.5,1) 1.3s both}
      .js .on .viz .nico{animation:pop .4s cubic-bezier(.3,1.8,.5,1) .65s both}
      .js .viz .w-bird{opacity:0;translate:0 30px}
      .js .on .viz .w-bird{opacity:1;translate:0 0;transition:opacity .3s ease 1.2s,translate .6s cubic-bezier(.3,1.6,.5,1) 1.2s}
      .js .on .viz .bubble{animation:pop .45s cubic-bezier(.3,1.8,.5,1) 1.55s both}
      .js .on .viz .marker{animation:pop .45s cubic-bezier(.3,1.8,.5,1) 1.75s both}
      .js .viz .tc,.js .viz .tlabel,.js .viz .formula{opacity:0}
      .js .on .viz .tc{animation:drop .45s cubic-bezier(.3,1.4,.5,1) both;animation-delay:calc(.25s + var(--i) * .2s)}
      .js .on .viz .tc.fall{animation:drop .45s cubic-bezier(.3,1.4,.5,1) calc(.25s + var(--i) * .2s) both,crash .7s ease-in calc(1.9s + var(--i) * .06s) forwards}
      .js .on .viz .tc.stay{animation:drop .45s cubic-bezier(.3,1.4,.5,1) calc(.25s + var(--i) * .2s) both,settle .5s cubic-bezier(.3,1.3,.5,1) 2.6s forwards}
      @keyframes drop{from{opacity:0;translate:0 -70px}to{opacity:1;translate:0 0}}
      @keyframes crash{0%{opacity:1;translate:0 0;rotate:0deg}20%{translate:-4px 0;rotate:-3deg}100%{opacity:0;translate:calc((var(--i) - 1.5) * 30px) 70px;rotate:calc((var(--i) - 1.5) * 18deg)}}
      @keyframes settle{to{opacity:1;translate:0 calc(var(--fall) * var(--step))}}
      .js .on .viz .tlabel{animation:fadein .4s ease 1.7s both}
      .js .on .viz .formula{animation:fadein .4s ease 1.5s both}
      .js .roll div{opacity:0;translate:0 18px}
      .js .credits.on .roll div{opacity:1;translate:0 0;transition:opacity .6s ease,translate .7s ease;transition-delay:calc(.15s + var(--i,0) * .16s)}
    }
    @media (prefers-reduced-motion:reduce){
      html{scroll-behavior:auto}
      .tc.fall{opacity:.28}
    }

    /* ===== タブレット以下 ===== */
    @media (max-width:900px){
      .vnav.prev{left:8px}.vnav.next{right:8px}
      .chara-in{gap:30px}
    }
    /* ===== スマホ ===== */
    @media (max-width:650px){
      .wrap{width:calc(100% - 28px)}
      .brand img{height:18px}
      .site-nav{gap:12px;font-size:14px}
      html{scroll-padding-top:calc(66px + env(safe-area-inset-top,0px))}
      .hero{min-height:clamp(540px,calc(100svh - 58px),760px)}
      .hero-copy{padding:16px 14px 30px}
      .hero-trico{min-height:0}
      .hero-trico .hero-main{margin-block:36px 0}
      .crumb{font-size:10px}
      .billing{flex-direction:column;gap:14px;width:100%}
      .billing .btn{width:100%;justify-content:center}
      .screen-band{padding:14px 0}
      .cinema .vplayer{width:100%}
      .scoop{grid-template-columns:1fr;gap:20px;padding:26px 18px;rotate:-.6deg}
      .moji-out{width:120px}
      .scoop .stele{width:120px;margin-inline:auto}
      .gallery{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
      .gitem,.gph{min-height:150px}
      .vplay{width:56px;height:56px;font-size:19px}
      .vmeta{right:10px;top:10px;font-size:12px;padding:5px 11px}
      .cinema{padding:62px 0 62px}
      .band{padding:50px 0 54px}
      .band.tex{padding:66px 0 70px}
      .gband.top{top:14px}.gband.bottom{bottom:14px}
      .panel{padding:20px 16px;border-radius:16px}
      .chara-in{gap:28px}
      .fig-wrap{width:min(130px,36vw)}
      .chara-fig figcaption{margin-top:16px}
      .chara-fig:has(.cnav){padding-inline:44px}
      .cnav{width:34px;height:34px}
      .chara-note{font-size:12.5px}
      .chara-name{font-size:17px}
      .story>p:not(.en){font-size:14.5px;line-height:1.95}
      .step .pan-h{font-size:14px}
      .sec-head{gap:8px;margin-bottom:20px}
      .sec-row{gap:12px}
      .sec-row::before,.sec-row::after{width:21px;height:21px}
      .badge{border-width:3px}
      .fab{min-height:44px;padding:0 18px 0 60px;font-size:13px}
      .fab img{left:12px;width:38px}
      .summary{font-size:15px}
      .flow{--gut:14px;--card:min(310px,80vw);--gap:36px}
      .steps{padding-right:14px}
      .row-cards{gap:14px}
      .pair,.lead-pair{gap:6px}
      .lead-card{width:44px}
      .jrow{grid-template-columns:38px auto minmax(0,1fr);gap:8px}
      .jcards{gap:5px}
      .jcards .c{width:min(46px,12vw)}
      .jrule{font-size:11.5px}
      .hand .c{width:min(60px,15vw)}
      .w-bird{width:84px}
      .marker{width:36px}
      .stele-wrap{flex-direction:column;gap:22px}
      .extra-text{font-size:14.5px}
      .buy-box{grid-template-columns:1fr;gap:22px;padding:24px 18px}
      .buy-box .pkg{width:min(160px,50%);margin-inline:auto}
      .buy-box .btn{display:flex;justify-content:center}
      .credits{padding-top:64px}
      .roll{gap:14px}
      .roll div{grid-template-columns:1fr;gap:2px}
      .roll dt,.roll dd{text-align:center}
      .bg-card{height:180px}
      .site-footer{flex-direction:column;gap:8px}
    }
  </style>
  <script>document.documentElement.className+=" js"</script>
</head>
<body>
<header class="site-header">
  <div class="bar">
    <a class="brand" href="../../"><img src="../../img/{{header_logo}}" alt="PANDA KINEMA"></a>
    <nav class="site-nav" aria-label="サイト"><a href="../../#news"><span class="cap">NEWS</span></a><a href="../../#board"><span class="cap">BOARD GAME</span></a><a href="../../#movie"><span class="cap">MOVIE</span></a><a href="../../#tools"><span class="cap">PLAY&amp;TOOLS</span></a><a href="../../#about"><span class="cap">ABOUT</span></a></nav>
    <div class="lang" role="group" aria-label="言語 / Language" hidden><button type="button" data-l="ja" aria-pressed="true"><span class="cap">JA</span></button><button type="button" data-l="en" aria-pressed="false"><span class="cap">EN</span></button></div>
  </div>
</header>

<main class="key">
  <!-- 1. メインビジュアル:パッケージの絵をそのまま大きく -->
  <section class="hero {{hero_cls}}" aria-labelledby="title">
    {{hero_art}}
    <div class="hero-copy">
      <div class="crumb"><p><a href="../../#board">BOARD GAME</a> / {{title}}</p>{{now_label_html}}</div>
      <div class="hero-main">
        {{hero_visual}}
        <h1 id="title"><img class="logo" src="{{img:{{logo}}}}" alt="{{logo_alt}}" width="{{logo_w}}" height="{{logo_h}}"></h1>
        <div class="billing">
          <dl class="spec">
{{spec_html}}
          </dl>
          <a class="btn" href="{{booth}}" target="_blank" rel="noopener">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
        </div>
      </div>
    </div>
  </section>

  <!-- 2. 動画:画面幅いっぱいの黒帯をスクリーンに(data-yt に YouTube の動画IDを入れると再生できる) -->
  <section class="cinema reveal-cinema" id="video" aria-labelledby="video-title">
    <div class="gband top" aria-hidden="true"></div>
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">MOVIE</p><div class="sec-row"><h2 class="pill sec-h" id="video-title">{{L:紹介動画|Videos}}</h2></div></header>
    </div>
    <div class="screen-band">
      <div class="vplayer">
        <div class="vtrack" tabindex="0">
{{videos_html}}
        </div>
        <button class="vnav prev" type="button" aria-label="前の動画">‹</button>
        <button class="vnav next" type="button" aria-label="次の動画">›</button>
      </div>
    </div>
    <div class="gband bottom" aria-hidden="true"></div>
    <div class="vdots">{{vdots_html}}</div>
  </section>

  <!-- 3. キャラクター+取説の導入文(世界観+ルール) -->
  <section class="band band-c chara" id="story" aria-labelledby="intro-title">
    <div class="wrap chara-in">
      <div class="story reveal">
        <p class="en" aria-hidden="true">STORY</p>
        <h2 id="intro-title">{{catch}}</h2>
        <p>{{intro}}</p>
      </div>
      <figure class="chara-fig reveal-chara">
        {{chara_html}}
      </figure>
    </div>
  </section>

  <!-- 4. どんなゲーム?(目的の要約+図) -->
  <section class="band tex" id="rules" aria-labelledby="rules-title">
    <div class="gband top" aria-hidden="true"></div><div class="gband bottom" aria-hidden="true"></div>
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">HOW TO PLAY</p><div class="sec-row"><h2 class="pill sec-h" id="rules-title">{{L:どんなゲーム?|What kind of game?}}</h2></div></header>
      <p class="summary">{{summary}}</p>
      <div class="flow">
        <ol class="steps" tabindex="0" aria-label="遊び方の流れ(横にスクロール)">
{{steps_html}}
        </ol>
        <div class="flow-ui" hidden><button class="fnav prev" type="button" aria-label="前のカード">‹</button><div class="flow-bar" aria-hidden="true"><span></span></div><button class="fnav next" type="button" aria-label="次のカード">›</button></div>
      </div>
      <div class="manual-link reveal"><p>{{L:くわしいルールは遊び方説明書で|Full rules are in the rulebook}}</p><a class="btn" lang="ja" href="{{manual_ja}}" target="_blank" rel="noopener">遊び方説明書を読む <span aria-hidden="true">↗</span></a><a class="btn" lang="en" href="{{manual_en}}" target="_blank" rel="noopener">Read the rulebook <span aria-hidden="true">↗</span></a></div>
    </div>
  </section>

  <section class="band band-c" id="photo" aria-labelledby="photo-title">
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">GALLERY</p><div class="sec-row"><h2 class="pill sec-h" id="photo-title">{{L:ギャラリー|Gallery}}</h2></div></header>
      <div class="gallery reveal">
{{gallery_html}}
      </div>
    </div>
  </section>

  <section class="band tex buy" id="buy" aria-label="購入">
    <div class="gband top" aria-hidden="true"></div><div class="gband bottom" aria-hidden="true"></div>
    <div class="wrap">
    <div class="panel buy-box reveal">
      <img class="pkg" src="{{img:{{pkg}}}}" alt="{{title}}のパッケージ" width="{{pkg_w}}" height="{{pkg_h}}" loading="lazy">
      <div>
        <img class="buy-logo" src="{{img:{{logo_buy}}}}" alt="{{logo_alt}}" loading="lazy">
        <dl class="spec">
{{spec_html}}
        </dl>
        <p class="contents">{{contents}}</p>
        {{price_html}}
        <a class="btn" href="{{booth}}" target="_blank" rel="noopener">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
      </div>
    </div>
    </div>
  </section>

  <!-- おまけ:興味のある人向けに最後に -->
  <section class="band band-c extra" id="extra" aria-labelledby="extra-title">
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">EXTRA</p><div class="sec-row"><h2 class="pill sec-h" id="extra-title">{{L:おまけ|Extras}}</h2></div></header>
      <article class="scoop reveal" aria-labelledby="scoop-title">
        <div class="scoop-text">{{extra_kicker_html}}<h3 class="extra-title" id="scoop-title">{{extra_title}}</h3>{{extra_html}}</div>
        {{extra_img}}
      </article>
    </div>
  </section>

  <dialog class="lb" aria-label="写真"><img alt=""><button class="lb-x" type="button" aria-label="閉じる">×</button></dialog>

  <a class="fab" href="{{booth}}" target="_blank" rel="noopener"><img src="{{img:{{fab_pkg}}}}" alt="" width="44" height="67">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
</main>

<!-- 5. クレジット -->
<section class="credits wrap reveal-credits" aria-label="クレジット">
  <img class="credits-logo" src="{{img:{{logo_credits}}}}" alt="{{logo_alt}}" loading="lazy">
  <dl class="roll">
{{credits_html}}
  </dl>
</section>

<!-- 6. ほかの作品:トップと同じカード(少し小さめ) -->
<div class="wrap"><div class="dotline" aria-hidden="true"></div></div>
<section class="lineup-sec" id="lineup" aria-labelledby="lineup-title">
  <div class="wrap">
    <h2 class="lineup-h" id="lineup-title"><span class="cap">BOARD GAME</span></h2>
    <ul class="bg-row">
{{lineup_html}}
    </ul>
  </div>
</section>

<div class="wrap"><footer class="site-footer"><span>©2015-2026 Panda Kinema</span><a href="#"><span class="cap">BACK TO TOP ↑</span></a></footer></div>

<script>
(function(){
  var root=document.documentElement, motion=!window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var done=false; function lit(){ if(done) return; done=true; requestAnimationFrame(function(){ root.classList.add("lit") }) }
  var hero=[].slice.call(document.querySelectorAll(".hero img")), left=hero.filter(function(i){return !i.complete}).length;
  if(!left) lit(); else hero.forEach(function(i){ if(!i.complete){ i.addEventListener("load",function(){ if(--left<=0) lit() }); i.addEventListener("error",lit) } });
  setTimeout(lit,1500);

  /* スクロール:見えたら再生、画面の外に出たら戻す(戻ってきたらもう一度) */
  var els=[].slice.call(document.querySelectorAll(".reveal,.reveal-credits,.reveal-cinema,.reveal-chara"));
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){ var k=0; es.forEach(function(e){
      var t=e.target;
      if(e.isIntersecting && e.intersectionRatio>=.18){
        if(t.classList.contains("step")){ var d=k++*550; clearTimeout(t._t); t._t=setTimeout(function(){ t.classList.add("on") },d) }   /* 一度に入ったカードは左から順に */
        else t.classList.add("on");
      } else if(!e.isIntersecting){ clearTimeout(t._t); t.classList.remove("on") }
    }) },{threshold:[0,.18]});
    els.forEach(function(el){ io.observe(el) });
  } else els.forEach(function(el){ el.classList.add("on") });

  /* 追従するBOOTHボタン:メインビジュアルのボタン・購入欄・フッターが見えていない間だけ出す */
  var fab=document.querySelector(".fab");
  if(fab){
    var watch=[document.querySelector(".hero .billing"),document.querySelector("#buy .buy-box"),document.querySelector(".site-footer")].filter(Boolean);
    if("IntersectionObserver" in window){
      var seen=[]; watch.forEach(function(){ seen.push(true) });
      var fo=new IntersectionObserver(function(es){ es.forEach(function(e){ seen[watch.indexOf(e.target)]=e.isIntersecting });
        fab.classList.toggle("show",seen.indexOf(true)<0) });
      watch.forEach(function(w){ fo.observe(w) });
    } else fab.classList.add("show");
  }

  /* スクロールに合わせて:メインビジュアルのパララックス/境目の模様が流れる */
  var art=document.querySelector(".hero-art"), heroSec=document.querySelector(".hero");
  if(motion){
    var ticking=false;
    function frame(){
      ticking=false; var sy=window.scrollY, vh=window.innerHeight;
      if(art && heroSec){ var y=Math.min(sy,heroSec.offsetHeight); art.style.transform="translate3d(0,"+(y*.28)+"px,0)" }
      root.style.setProperty("--sx",(sy*.25).toFixed(1))
    }
    window.addEventListener("scroll",function(){ if(ticking) return; ticking=true; requestAnimationFrame(frame) },{passive:true});
    window.addEventListener("resize",frame); frame();
  }

  /* キャラクター:◀▶ で1体ずつ */
  [].forEach.call(document.querySelectorAll(".chara-fig"),function(fig){
    var sl=[].slice.call(fig.querySelectorAll(".chara-slide")), dots=[].slice.call(fig.querySelectorAll(".cdots i")), cur=0;
    if(sl.length<2) return;
    function go(k){ cur=(k+sl.length)%sl.length; sl.forEach(function(s,i){ s.classList.toggle("cur",i===cur); if(i===cur) s.removeAttribute("aria-hidden"); else s.setAttribute("aria-hidden","true") }); dots.forEach(function(d,i){ d.classList.toggle("on",i===cur) }) }
    fig.querySelector(".cnav.prev").addEventListener("click",function(){ go(cur-1) });
    fig.querySelector(".cnav.next").addEventListener("click",function(){ go(cur+1) });
  });
  /* 言語切替(JA/EN)。選んだ言語はこの端末に覚えておく。?lang=en でも開ける */
  var langBox=document.querySelector(".lang");
  if(langBox){
    langBox.hidden=false;
    var setLang=function(l){ root.classList.toggle("lang-en",l==="en"); root.lang=l;
      [].forEach.call(langBox.querySelectorAll("button"),function(b){ b.setAttribute("aria-pressed",b.getAttribute("data-l")===l?"true":"false") });
      try{ localStorage.setItem("pk-lang",l) }catch(e){} };
    var q=(location.search.match(/[?&]lang=(ja|en)/)||[])[1], saved=null; try{ saved=localStorage.getItem("pk-lang") }catch(e){}
    setLang(q||saved||"ja");
    langBox.addEventListener("click",function(e){ var b=e.target.closest("button"); if(b) setLang(b.getAttribute("data-l")) });
  }

  /* 遊び方:横に流れるカード(ボタン・バー・マウスのドラッグ) */
  var flow=document.querySelector(".flow .steps");
  if(flow){
    var ui=document.querySelector(".flow-ui"), fb=ui.querySelector(".flow-bar span"), fp=ui.querySelector(".prev"), fn=ui.querySelector(".next");
    function fsync(){ var max=flow.scrollWidth-flow.clientWidth; ui.hidden=max<4; if(max<4) return;
      fb.style.setProperty("--w",(flow.clientWidth/flow.scrollWidth*100)+"%"); fb.style.setProperty("--l",(flow.scrollLeft/flow.scrollWidth*100)+"%");
      fp.disabled=flow.scrollLeft<4; fn.disabled=flow.scrollLeft>max-4 }
    function step(){ var c=flow.querySelector(".step"); return c.offsetWidth+parseFloat(getComputedStyle(flow).columnGap||0) }
    fp.addEventListener("click",function(){ flow.scrollBy({left:-step(),behavior:"smooth"}) });
    fn.addEventListener("click",function(){ flow.scrollBy({left:step(),behavior:"smooth"}) });
    flow.addEventListener("scroll",function(){ requestAnimationFrame(fsync) },{passive:true});
    window.addEventListener("resize",fsync); fsync();
    var sx0=0, sl0=0, moved=false, down=false;
    flow.addEventListener("pointerdown",function(e){ if(e.pointerType!=="mouse"||e.button!==0) return; down=true; moved=false; sx0=e.clientX; sl0=flow.scrollLeft });
    window.addEventListener("pointermove",function(e){ if(!down) return; var dx=e.clientX-sx0; if(!moved&&Math.abs(dx)>5){ moved=true; flow.classList.add("drag") } if(moved) flow.scrollLeft=sl0-dx });
    window.addEventListener("pointerup",function(){ if(!down) return; down=false; if(moved){ var l=flow.scrollLeft; flow.classList.remove("drag"); flow.scrollLeft=l; flow.scrollBy({left:0}) } });
    flow.addEventListener("click",function(e){ if(moved){ e.preventDefault(); e.stopPropagation(); moved=false } },true);
    flow.addEventListener("dragstart",function(e){ e.preventDefault() });
  }

  /* ギャラリー:クリックで大きく */
  var lb=document.querySelector(".lb");
  if(lb && lb.showModal){
    var lbi=lb.querySelector("img");
    [].forEach.call(document.querySelectorAll(".gitem"),function(g){ g.addEventListener("click",function(){ var im=g.querySelector("img"); lbi.src=im.src; lbi.alt=im.alt; lb.showModal() }) });
    lb.addEventListener("click",function(e){ if(e.target===lb||e.target.classList.contains("lb-x")) lb.close() });
  }

  /* 動画:1枠で切り替え */
  var track=document.querySelector(".vtrack"); if(!track) return;
  var slides=[].slice.call(track.children), dots=[].slice.call(document.querySelectorAll(".vdots button"));
  var prev=document.querySelector(".vnav.prev"), next=document.querySelector(".vnav.next"), cur=0;
  function go(i){ i=Math.max(0,Math.min(slides.length-1,i)); track.scrollTo({left:slides[i].offsetLeft-track.clientLeft*0,behavior:"smooth"}) }
  function sync(){ cur=Math.round(track.scrollLeft/track.clientWidth);
    dots.forEach(function(d,k){ d.setAttribute("aria-current",k===cur?"true":"false") });
    prev.disabled=(cur===0); next.disabled=(cur===slides.length-1) }
  prev.addEventListener("click",function(){ go(cur-1) });
  next.addEventListener("click",function(){ go(cur+1) });
  dots.forEach(function(d,k){ d.addEventListener("click",function(){ go(k) }) });
  track.addEventListener("scroll",function(){ requestAnimationFrame(sync) },{passive:true});
  track.addEventListener("keydown",function(e){ if(e.key==="ArrowRight"){ e.preventDefault(); go(cur+1) } if(e.key==="ArrowLeft"){ e.preventDefault(); go(cur-1) } });
  prev.disabled=true; next.disabled=slides.length<2;
  slides.forEach(function(s){
    var id=(s.getAttribute("data-yt")||"").trim(), btn=s.querySelector(".vposter"), title=s.getAttribute("data-title");
    if(!id){ btn.disabled=true; btn.setAttribute("aria-label",title+"(準備中)"); return }
    var soon=s.querySelector(".vsoon"); if(soon) soon.remove();
    btn.querySelector("img").src="https://i.ytimg.com/vi/"+id+"/hqdefault.jpg";
    btn.setAttribute("aria-label",title+"を再生");
    btn.addEventListener("click",function(){
      var f=document.createElement("iframe");
      f.src="https://www.youtube-nocookie.com/embed/"+id+"?autoplay=1&rel=0"; f.title=title; f.allow="autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen=true;
      s.appendChild(f); btn.remove(); track.classList.add("playing");
    });
  });
})();
</script>
</body>
</html>
'''

def hl(t):   # [[ ]] = 取説の赤字(強調)
    return re.sub(r'\[\[(.+?)\]\]', r'<em>\1</em>', t)

def yt(v):   # YouTube のURLでもIDでもOK
    v = str(v or '').strip()
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})', v)
    return m.group(1) if m else v

def card_href(x):   # トップのカードのリンク先を、作品ページから見た場所に
    u = str(x.get('page') or '')
    if u.startswith('http'):
        return u
    if u.startswith('games/'):
        return '../' + u[len('games/'):]
    return u or '../../#board'

def render(key):
    g = apply(key); e = H.escape
    br = lambda t: t.replace('\n', '<br>')
    steps = '\n'.join('''          <li class="step reveal %s">
            <div class="step-head"><span class="snum" aria-label="ステップ%d">%d</span><p class="step-lead">%s</p></div>
            <div class="viz">%s</div>
          </li>''' % (st.get('cls', ''), n + 1, n + 1, hl(e(st['b'])), st['v']) for n, st in enumerate(g['steps']))
    credits = '\n'.join('    <div style="--i:%d"><dt>%s</dt><dd>%s</dd></div>' % (i, e(a), e(b)) for i, (a, b) in enumerate(g['credits']))
    v = dict(
        header_logo=imgname(g['site'].get('header_logo') or 'brand.png'),
        title=e(g['title']), description=e(g['description']), theme=g['theme'], booth=e(g['booth']), seats=SEATS,
        now_label_html=('<p>%s</p>' % e(g['now_label'])) if g['now_label'] else '',
        hero_cls=g['hero_cls'], hero_art=g['hero_art'], hero_visual=g['hero_visual'], hero_css=g['hero_css'], viewers=g['viewers'],
        logo=g['logo'], logo_w=g['logo_size'][0], logo_h=g['logo_size'][1], logo_alt=e(g['logo_alt']),
        logo_buy=g['logo_buy'], logo_credits=g['logo_credits'], poster=g['poster'],
        catch=br(e(g['catch'])), intro=br(e(g['intro'])), intro_img=g['intro_img'][0], intro_alt=e(g['intro_img'][1]), intro_cls=g['intro_img'][2],
        summary=br(re.sub(r'\[\[(.+?)\]\]', r'<em>\1</em>', e(g['summary']))),
        spec_html='\n'.join('            <div><dt>%s</dt><dd>%s</dd></div>' % (e(a), e(b)) for a, b in g['spec']),
        steps_html=steps, extra_title=e(g['extra_title']), extra_html=hl(g['extra_html']), extra_img=g.get('extra_img', ''), manual_ja=e(g['manual_ja']), manual_en=e(g['manual_en']),
        gallery_html='\n'.join(['        <figure class="%s"><button class="gitem" type="button" aria-label="%sを大きく見る"><img src="{{img:%s}}" alt="%s" loading="lazy"></button></figure>' % (c, e(t), f, e(t)) for f, t, te, c in g.get('gallery', [])]
                                + ['        <div class="gph">{{L:%s(準備中)|%s (coming soon)}}</div>' % (e(t), e(te)) for t, te in g.get('gallery_todo', [])]),
        extra_kicker_html=('<p class="extra-kicker">%s</p>' % e(g['extra_kicker'])) if g.get('extra_kicker') else '',
        pkg=g['pkg'], pkg_w=g['pkg_size'][0], pkg_h=g['pkg_size'][1], contents=br(e(g['contents'])),
        price_html=('<p class="price">%s<small>{{L:BOOTH価格|on BOOTH}}</small></p>' % e(g['price'])) if g['price'] else '',
        credits_html=credits,
        chara_html=g.get('chara_html') or ('<div class="chara-slides"><div class="chara-slide cur"><div class="fig-wrap">%s</div><figcaption><span class="chara-name">%s</span><span class="chara-note">%s</span></figcaption></div></div>' % (g.get('chara_fig', ''), e(g.get('chara_name', '')), e(g.get('chara_note', '')).replace('\n', '<br>'))),
        piece_img=g.get('piece_img', ''), piece_alt=e(g.get('piece_alt', '')),
        chara_note=e(g.get('chara_note', '')).replace('\n', '<br>'),
        fab_pkg=g.get('fab_pkg', 'bibilu_pkg_sm.webp'),
        videos_html='\n'.join('          <figure class="vslide" data-yt="%s" data-title="%s"><button class="vposter" type="button"><img src="{{img:%s}}" alt="" loading="lazy"><span class="vplay" aria-hidden="true">▶</span><span class="vmeta">%s%s</span></button></figure>' % (
            e(yt(v.get('youtube'))), e(str(v.get('kind_ja') or '')), imgname(v.get('poster')) or g['poster'], LL(v, 'kind'), '' if v.get('youtube') else '<span class="vsoon">{{L:準備中|Coming soon}}</span>') for v in g['videos']),
        vdots_html=''.join('<button type="button"%s>%s</button>' % (' aria-current="true"' if i == 0 else '', LL(v, 'kind')) for i, v in enumerate(g['videos'])),
        lineup_html='\n'.join(
            '      <li><a class="bg-card" href="%s"%s><img src="../../img/%s" alt="%s" loading="lazy">%s</a></li>' % (
                card_href(x), ' target="_blank" rel="noopener"' if str(x.get('page') or '').startswith('http') else '', imgname(x['front']), e(x['name']),
                '<span class="bg-new">{{L:新作|NEW}}</span>' if x.get('new') else '') for x in g['games'].values() if x['key'] != key),
    )
    s = TEMPLATE
    for _ in range(3):
        s = re.sub(r'\{\{(?!img:)(\w+)\}\}', lambda m: str(v[m.group(1)]), s)
    s = re.sub(r'\{\{L:(.*?)\|(.*?)\}\}', r'<span lang="ja">\1</span><span lang="en">\2</span>', s)
    s = re.sub(r'\{\{img:([\w.\-]+)\}\}', lambda m: uri(m.group(1)), s)
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)[:5]
    return s

if __name__ == '__main__':
    for key in GAMES:
        out = os.path.join(ROOT, 'new', 'games', key, 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(render(key))
        print(out, os.path.getsize(out))
