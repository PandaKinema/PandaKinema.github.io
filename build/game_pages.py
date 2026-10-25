# パンダキネマ 作品ページを組み立てる(new/games/<key>/index.html)
# 文章と画像は content/pages/<key>.yml(編集画面の「作品ページ」)、人数・時間・年齢は content/games.yml から読みます。
# このファイルには、各作品のデザイン(色・背景・遊び方の図の動き)が入っています。新しい作品のページを足すときは GAMES に追加します。
# 手元で動かすとき:  pip install pyyaml pillow  →  python build/game_pages.py
#
# パンダキネマ 作品ページ 共通フォーマット v46
#     v46: TRICO!の4コマを遊び方動画どおりに(リードマーカーはカードの横)
#     v45: ビビルの塔の重ね方を説明シートどおりに(下のカードは下の4割=窓と土台が見え、真ん中の紺が隠れる)
#     v44: 帯の画像は1周期に自動で切りそろえてループ/強調の下線はなし
#     v43: 本文を細く・強調を太く(同じ色なら下線)/項目ごとに背景の色を選べる
#     v42: ページの幅はトップの絵の幅まで(左右は黒)/帯の色を自由に指定/白い文字優先のときBOOTHボタンも白文字
#     v41: 遊び方をタブで複数(イカタコ:対戦・協力・ソロ)/トップの文字色を選べる(hero_ink)/白い文字を優先(prefer_white)
#     v40: 強調は選んだ色か赤、読みにくければ太字だけ/遊び方の図の下地はメインカラーの薄色
#     v39: 文字は決めた色・白・黒だけ/強調は色を変える(基本は赤、編集画面で選べる。読みにくければ自動でほかの色)
#     v38: 作品ページの幅に上限(1440px)。その外はサイトの黒い下地
#     v37: トップの絵はいつも全部見せる(画面の高さに合わせる)。横長の画面では左右を模様か端の色でつなぐ
#     v36: 編集画面で画像を消したら、帯・模様・見出しの飾りも消える(デザインの初期値に戻らない)
#     v35: 黒文字の代わりに作品の色を暗くした色
#     v34: 強調の色は地と4.5以上の差があるときだけ(なければ赤→文字色+太字)/見出しの飾りの色を選べる
#     v33: 全面の絵の上で部品を動かす(TRICO!=鳥と宝石、モコチャカ=アイコンが回る)
#     v32: トップは画面の高さいっぱい、ロゴを画面の高さに合わせて大きく
#     v31: トップ画像の下からのぼかしをなくす
#     v30: トップ画像(横長)を全作品に。明るい絵は下をぼかさない/絵の拡大(zoom)
#     v29: ギャラリーはスクロールではなく1枚ずつ動かす(途中で止まらない)/アクセントカラー2の帯にも模様
#     v28: 遊び方のカードはまとめて表示(横スクロールで上下に揺れない)
#     v27: 4コマをゲームの終わりまで(モコチャカ・イカタコ・こいこいのぼり)
#     v26: 作品ページでアクセントカラー2を選べる(背景・帯/見出し)/トップの絵のパララックスをやめる(ロゴが絵にかぶらない)
#     v25: 閉じたカードのトップはフルサイズ(画面の高さいっぱい)/ギャラリーは1枚ずつ ◀▶ で切り替え
#     v24: イカタコ・こいこいのぼり・BASH&SMASH(トップはカード)/名前が空のキャラは名札を出さない
#     v23: モコチャカ(かんたんルールの4コマ・方眼のトップ・モコのシルエット)。トップの模様に grid(方眼)を追加
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import media
WEB = TOP_IMG = media.IMG   # 画像はすべて new/img(作品ごとのフォルダ)
MANUAL_JA = '#'   # 遊び方説明書(日本語)のURLが決まったら差し替え
MANUAL_EN = '#'   # 英語版のURL
BOOTH = 'https://pandakinema.booth.pm/'   # 商品ページのURLが決まったら差し替え

def L(ja, en):   # 日本語/英語。切替ボタンで表示が変わる
    return '{{L:%s|%s}}' % (ja, en)

def uri(f):   # 作品ページ(new/games/<key>/)から見た画像の場所
    p = media.path(f)
    if not os.path.isfile(os.path.join(WEB, p)):
        sys.exit('見つからない画像があります: new/img/' + f)
    return '../../img/' + p

def load(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as fh:
        return yaml.safe_load(fh) or {}
def imgname(v):   # 画像の欄の値(img/trico/foo.png、foo.png など)を new/img からの場所に
    return media.path(v)
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
PAL = ['#ffffff', '#000000']   # 作品で決めた色(メイン・アクセント・アクセントカラー2)。apply で設定
PREFW = [False]   # 作品ページ「白い文字を優先」
WMIN = [4.5]   # 白にする読みやすさの下限(「文字はすべて白」なら低く)
def ink(bg, other=None):   # 文字の色:決めた色・白・黒だけを使う。もう1色 → 白 → 決めた色 → 黒 の順で読めるもの
    if PREFW[0] and contrast(bg, '#ffffff') >= WMIN[0]:
        return '#ffffff'
    for c in ([other] if other else []) + ['#ffffff'] + PAL + ['#000000']:
        if c and contrast(bg, c) >= 4.5:
            return c
    return max(PAL + ['#ffffff', '#000000'], key=lambda c: contrast(bg, c))
def deep(bg, base=None):   # (互換)読める濃い色:決めた色か黒
    return next((c for c in PAL + ['#000000'] if contrast(bg, c) >= 4.5), '#000000')

def mix(a, b, w):   # 色 a を w の割合で b に混ぜる
    a, b = str(a).lstrip('#'), str(b).lstrip('#')
    return '#' + ''.join('%02x' % round(int(a[i:i + 2], 16) * w + int(b[i:i + 2], 16) * (1 - w)) for i in (0, 2, 4))

RED = '#d4242b'   # 取説の赤字

def num(v, default):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default
def tint_tile(v, color):
    """模様の画像を同じ形のまま指定の色に(透明度はそのまま。白にするときは少し控えめに)"""
    from PIL import Image
    f = imgname(v)
    stem, ext = os.path.splitext(f)
    out = '%s_%s.png' % (stem, color.lstrip('#'))
    with Image.open(os.path.join(WEB, f)) as im:
        im = im.convert('RGBA')
        a = im.getchannel('A')
        if color.lower() == '#ffffff' and im.getpixel((0, 0))[:3] != (255, 255, 255):
            a = a.point(lambda x: int(x * .75))
        o = Image.new('RGBA', im.size, tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        o.putalpha(a)
        o.save(os.path.join(WEB, out))
    return out

def loop_band(v):
    """帯の画像を、横にきれいにつながる幅(模様の1周期ぶん)に自動で切りそろえる。つながる幅が見つからなければそのまま"""
    from PIL import Image
    f = imgname(v)
    src = os.path.join(WEB, f)
    with Image.open(src) as im:
        im = im.convert('RGBA'); W, H = im.size
        a = im.getchannel('A').resize((W, max(4, min(H, 24))))
        hh = a.height; px = a.load()
        cols = [[px[x, y] for y in range(hh)] for x in range(W)]
        def diff(p):
            n = W - p
            return sum(abs(cols[x][y] - cols[x + p][y]) for x in range(0, n, 2) for y in range(hh)) / max(1, (n // 2) * hh)
        ds = {p: diff(p) for p in range(max(8, W // 40), W // 2 + 1)}   # 2回以上くり返している幅だけ調べる
        base = sum(ds.values()) / len(ds)
        best = next((p for p, dv in ds.items() if dv < base * .12), None)   # いちばん短いくり返しの幅
        if not best:
            return f   # くり返しが見つからない=画像の幅ぴったりで作ってある
        per = best
        # 周期はぴったりの整数とは限らないので、何周期か先で本当にぴったり重なる幅を探す(半分くらい重なる範囲で一番長く)
        m = max(1, (W // 2) // per)
        L = min(range(m * per - 3, m * per + 4), key=lambda q: diff(q) if 0 < q < W else 1e9)
        x0 = 0
        crop = im.crop((x0, 0, x0 + L, H))
        if L % 2:   # 半分の大きさで並べるので幅は偶数に(半端なピクセルで継ぎ目が出ないように)
            crop = crop.resize((L + 1, H), Image.LANCZOS)
        stem, ext = os.path.splitext(f)
        out = stem + '_loop.png'
        crop.save(os.path.join(WEB, out))
        return out

def aw_ah(f):
    from PIL import Image
    with Image.open(os.path.join(WEB, imgname(f))) as im:
        return im.width / im.height

def hero(g, d, t):
    """メインビジュアル(編集画面の「メインビジュアル」)
    ・背景の絵:画面いっぱいに敷く(ビビルの塔)
    ・部品:模様の上に画像を重ねて動かす(TRICO!)。1枚目が土台、2枚目からは土台に対する位置(%)。部品があるときはトップ画像より優先(トップ画像を見本に組む)
    ・どちらもなければ、トップの閉じたカードの画像を出す"""
    h = d.get('hero') or {}
    style = []
    lw, lh = g['logo_size']
    style.append('--lw:%dpx;--lar:%.4f' % (min(600, round(168 * lw / lh)), lw / lh))   # ロゴの縦横比(大きさは画面の高さに合わせる)
    g['h1_cls'] = ''
    # トップは画像が主役:背景の色はページの色ではなく、トップ画像(なければ閉じたカード)の地の色から取る
    hbg = hbg2 = None
    src = h.get('art') or t.get('front')
    if src:
        from PIL import Image
        with Image.open(os.path.join(WEB, imgname(src))) as im:
            px = im.convert('RGB').crop((0, 0, min(160, im.width), min(160, im.height))).getcolors(1 << 20) or []
        top = [c for _, c in sorted(px, reverse=True)[:2]]
        if top:
            c = max(top, key=lambda x: sum(x))   # よく使われている2色のうち明るい方
            hbg = '#%02x%02x%02x' % c
            hbg2 = '#%02x%02x%02x' % min(top, key=lambda x: sum(x)) if len(top) > 1 else None   # 暗い方(三角模様の地。トップ画像と同じ色に)
            M, A = t.get('main') or '#1b2228', t.get('accent') or '#ffffff'
            fg = max((M, A, deep(hbg), '#ffffff'), key=lambda x: (contrast(x, hbg) >= 4.5, x in (M, A), x == '#ffffff', contrast(x, hbg)))
            style.append('--hero-bg:%s;--hero-ink:%s' % (hbg, fg))
    art_wide = False
    cover_layers = str(h.get('fit') or '') == 'cover' and h.get('art') and [x for x in (h.get('layers') or []) if x.get('image')]
    if cover_layers:   # 全面に敷いた絵の上で、切り抜いた部品を動かす(位置は絵に対する %)
        art_wide = True
    elif h.get('art') and not [x for x in (h.get('layers') or []) if x.get('image')]:   # 部品(Claudeが設定)があればそちらを優先。トップ画像は見本   # トップ画像:横長なら全面に敷く、縦長・正方形なら背景の色の上に置く
        from PIL import Image
        with Image.open(os.path.join(WEB, imgname(h['art']))) as im:
            aw, ah = im.size
        fit = str(h.get('fit') or '')   # cover=全面に敷く / center=置く(Claudeが設定)。空なら形で決める
        art_wide = fit == 'cover' or (fit != 'center' and aw >= ah * 1.2)
        if not art_wide:
            h = dict(h, layers=[{'image': h['art'], 'motion': 'rise'}], pattern=h.get('pattern'))
    if art_wide:
        g['hero_cls'] = 'hero-cover'
        # 絵の下の方が明るいとき(モコチャカ・TRICO! など)は暗くぼかさず、文字はその上で読める色に
        from PIL import Image
        with Image.open(os.path.join(WEB, imgname(h['art']))) as im:
            im = im.convert('RGB'); bw, bh = im.size
            px = [im.getpixel((x, y)) for x in range(0, bw, max(1, bw // 40)) for y in range(int(bh * .7), bh, max(1, bh // 30))]
        bot = '#%02x%02x%02x' % tuple(sum(p[c] for p in px) // len(px) for c in range(3))
        M, A = t.get('main') or '#1b2228', t.get('accent') or '#ffffff'
        g['hero_cls'] += ' light'   # 下からのぼかしはなし。文字は絵の下の方の色の上で読める色
        fg = max((M, A, deep(bot), '#ffffff'), key=lambda x: (contrast(x, bot) >= 4.5, x in (M, A), x == '#ffffff', contrast(x, bot)))
        if d.get('hero_ink') in ('white', 'black'):   # トップの文字・ボタンの色を指定
            fg = '#ffffff' if d['hero_ink'] == 'white' else '#000000'
            g['hero_cls'] += ' ink-set'
        style.append('--hero-ink:%s' % fg)
        if h.get('zoom'):
            style.append('--zoom:%g' % num(h['zoom'], 1))
        g['hero_art'] = '<div class="hero-art"><img class="art" src="{{img:%s}}" alt="" fetchpriority="high"></div>' % imgname(h['art'])
        if not cover_layers:   # 部品なしでも、絵は箱に入れて全部見せる
            cover_layers = []
        if True:
            pos = (str(h.get('art_pos') or '50% 50%').split() + ['50%'])[:2]
            fx, fy = (num(v.rstrip('%'), 50) / 100 for v in pos)
            out = []
            for i, x in enumerate(cover_layers):
                mo = str(x.get('motion') or 'none')
                st = '--x:%g%%;--y:%g%%;--w:%g%%;--r:%gdeg;--dl:%.2fs;--sp:%gs' % (num(x.get('x'), 0), num(x.get('y'), 0), num(x.get('width'), 20), num(x.get('rotate'), 0), .2 + .12 * i, num(x.get('speed'), 0) or 26 + (i % 3) * 5)
                out.append('<img class="aly%s" style="%s" src="{{img:%s}}" alt="">' % ('' if mo == 'none' else ' m-' + mo, st, imgname(x['image'])))
            # 絵はいつも画面の高さに合わせて全部見せる。画面が絵より横長なら、左右は背景の模様(side)か絵の端の色でつなぐ
            fill = ''
            if h.get('side'):
                fill = '<div class="art-fill" style="background-image:url({{img:%s}})"></div>' % imgname(h['side'])
            else:
                from PIL import Image
                with Image.open(os.path.join(WEB, imgname(h['art']))) as im:
                    im = im.convert('RGB'); W, Hh = im.size
                    def edge(x0):
                        stops = []
                        for k in range(13):
                            y = min(Hh - 1, round(k * (Hh - 1) / 12))
                            c = [sum(im.getpixel((x, y))[j] for x in range(x0, x0 + 6)) // 6 for j in range(3)]
                            stops.append('#%02x%02x%02x %.1f%%' % (c[0], c[1], c[2], k * 100 / 12))
                        return 'linear-gradient(%s)' % ','.join(stops)
                    fill = '<div class="art-fill edge" style="--edge-l:%s;--edge-r:%s"></div>' % (edge(1), edge(W - 7))
            g['hero_art'] = '<div class="hero-art"><div class="art-wrap" style="--ar:%.4f;--fx:%g">%s<div class="art-box"><img class="art-bg" src="{{img:%s}}" alt="" fetchpriority="high">%s</div></div></div>' % (aw_ah(h['art']), fx, fill, imgname(h['art']), ''.join(out))
        g['hero_visual'] = ''
        if h.get('art_pos'):
            style.append('--art-pos:%s' % str(h['art_pos']))
    else:
        g['hero_cls'] = 'hero-stage'
        g['hero_art'] = '<div class="hero-art"></div>'
        if h.get('pattern') == 'tri':
            style.append('--pat:%s;--pat-size:92px 160px' % tri_pattern(hbg or g.get('_D') or t.get('main') or '#fdd000', hbg2 if hbg else None))
        elif h.get('pattern') == 'grid':
            style.append('--pat:%s;--pat-size:44px 44px' % grid_pattern(hbg or g.get('_D') or t.get('main') or '#f19ebc'))
        if h.get('width'):
            style.append('--sw:%dpx' % num(h['width'], 380))
        layers = [x for x in (h.get('layers') or []) if x.get('image')]
        out = []
        for i, x in enumerate(layers):
            mo = str(x.get('motion') or 'none')
            cls = 'ly0' if i == 0 else 'ly'
            st = '' if i == 0 else '--x:%g%%;--y:%g%%;--w:%g%%;--r:%gdeg;' % (num(x.get('x'), 0), num(x.get('y'), 0), num(x.get('width'), 20), num(x.get('rotate'), 0))
            st += '--dl:%.2fs;--bd:%.2fs' % (.1 if i == 0 else .5 + .15 * (i - 1), 1.2 - .8 * i)
            out.append('<img class="%s%s" style="%s" src="{{img:%s}}" alt="">' % (cls, '' if mo == 'none' else ' m-' + mo, st, imgname(x['image'])))
        if out:
            g['hero_visual'] = '<div class="stage" aria-hidden="true">%s</div>' % ''.join(out)
        elif t.get('front'):   # 閉じたカードを画面の高さいっぱいに。左右は画像の端の色をのばす、下(人数・購入)は画像の下端の色
            f = imgname(t['front'])
            from PIL import Image
            with Image.open(os.path.join(WEB, f)) as im:
                im = im.convert('RGB'); W, Hh = im.size
                def edge(x0):
                    stops = []
                    for k in range(13):
                        y = min(Hh - 1, round(k * (Hh - 1) / 12))
                        r, gg, b = [sum(im.getpixel((x, y))[c] for x in range(x0, x0 + 4)) // 4 for c in range(3)]
                        stops.append('#%02x%02x%02x %.1f%%' % (r, gg, b, k * 100 / 12))
                    return 'linear-gradient(%s)' % ','.join(stops)
                bot = [im.getpixel((x, Hh - 3)) for x in range(0, W, max(1, W // 40))]
                bc = tuple(sum(p[c] for p in bot) // len(bot) for c in range(3))
                el, er = edge(1), edge(W - 5)
            hb = '#%02x%02x%02x' % bc
            M, A = t.get('main') or '#1b2228', t.get('accent') or '#ffffff'
            fg = max((M, A, deep(hb), '#ffffff'), key=lambda x: (contrast(x, hb) >= 4.5, x in (M, A), x == '#ffffff', contrast(x, hb)))
            style.append('--hero-bg:%s;--hero-ink:%s;--edge-l:%s;--edge-r:%s;--card-ar:%d/%d' % (hb, fg, el, er, W, Hh))
            g['hero_cls'] = 'hero-full'
            g['hero_art'] = '<div class="hero-art"><img class="card-full" src="../../img/%s" alt="%s" fetchpriority="high"></div>' % (f, H.escape(str(t.get('name') or '')))
            g['hero_visual'] = ''
            g['h1_cls'] = ' class="sr-only"'
        else:
            g['hero_visual'] = ''
    g['hero_style'] = H.escape(';'.join(style))

def apply(key):
    """content/pages/<key>.yml(編集画面)の文章と画像を、作品の設定に上書きする。動きとデザインはこのファイルのまま"""
    g = GAMES[key]
    d = load('content/pages/%s.yml' % key)
    site = load('content/site.yml')
    games = {x['key']: x for x in load('content/games.yml')}
    t0 = games.get(key) or {}
    for k in ('title', 'description', 'logo_alt'):
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
    for k in ('catch', 'intro', 'summary', 'chara_name', 'chara_note', 'contents', 'price'):
        if (k + '_ja') in d:
            g[k] = LL(d, k)
    for st, ds in zip(g['steps'], d.get('steps') or []):
        st['b'] = LL(ds, 'text')
    if d.get('gallery') is not None:
        g['gallery'] = [(imgname(x['image']), str(x.get('caption_ja') or ''), str(x.get('caption_en') or x.get('caption_ja') or ''), 'wide' if x.get('wide') else '') for x in d['gallery'] if x.get('image')]
    if d.get('gallery_todo') is not None:
        g['gallery_todo'] = [(str(x.get('text_ja') or ''), str(x.get('text_en') or x.get('text_ja') or '')) for x in d['gallery_todo'] if x.get('text_ja')]
    if d.get('credits') is not None:   # 役割の英語は「スタッフロールの役割」から
        roles = {str(r.get('name')): str(r.get('name_en') or r.get('name')) for r in (load('content/roles.yml') or []) if r.get('name')}
        g['credits'] = [(L(str(x.get('role_ja') or ''), str(x.get('role_en') or roles.get(str(x.get('role_ja') or ''), '') or x.get('role_ja') or '')),
                         L(str(x.get('name_ja') or ''), str(x.get('name_en') or x.get('name_ja') or ''))) for x in d['credits']]
    # 動画は「動画」(一元管理)から、この作品のものだけ
    g['videos'] = [v for v in (load('content/videos.yml') or []) if v.get('work') == key]
    g['related'] = [str(x) for x in (d.get('related') or []) if x]
    g['ogp_image'] = d.get('ogp_image') or ''
    g['related_links'] = [x for x in (d.get('related_links') or []) if x.get('url')]
    # 人数・時間・年齢は トップ(ボードゲーム)の設定と同じものを使う
    t = games.get(key)
    if t:
        g['spec'] = [(L('人数', 'Players'), L('%s人' % t['players'], str(t['players']).replace('〜', '–'))), (L('時間', 'Time'), L('%s分' % t['time'], '%s min' % str(t['time']).replace('〜', '–'))), (L('年齢', 'Age'), L('%s歳から' % t['age'], '%s+' % t['age']))]
    g['booth'] = d.get('booth') or (t or {}).get('booth') or site.get('booth') or BOOTH
    g['manual_ja'] = d.get('manual_ja') or '#'
    g['manual_en'] = d.get('manual_en') or g['manual_ja']
    g['site'] = site
    g['games'] = games
    g['tools'] = load('content/tools.yml') or []
    # 背景2色(色か画像)と帯・見出しの飾り:編集画面の値を CSS の変数で上書き
    def tile(v):   # 2倍の大きさで作った画像を半分の大きさで敷き詰める
        f = imgname(v)
        with Image.open(os.path.join(WEB, f)) as im:
            w, h = im.size
        return f, w // 2, h // 2
    from PIL import Image
    css = []
    # 色:トップ(ボードゲーム)のメインカラー(背景)とアクセントカラー(帯・文字)。作品ページで別の組み合わせも選べる
    t = games.get(key) or {}
    M, A = t.get('main'), t.get('accent')
    if M and A:
        PREFW[0] = bool(d.get('prefer_white') or d.get('text_white'))
        WMIN[0] = 2.0 if d.get('text_white') else 4.5
        PAL[:] =[c for c in (M, A, '#' + str(d.get('color3')).lstrip('#') if d.get('color3') else None) if c]
        pick = {'main': M, 'accent': A, 'white': '#ffffff', 'black': '#000000'}
        c3 = str(d.get('color3') or '').strip()
        if re.fullmatch(r'#?[0-9a-fA-F]{6}', c3):   # 作品ページの「アクセントカラー2」
            pick['third'] = '#' + c3.lstrip('#')
        cb = str(t.get('bg') or 'main')   # カードの「背景の色」
        D = pick.get(str(d.get('bg_color') or cb), M)            # 背景(動画・遊び方・購入)。空ならカードと同じ
        O0 = 'accent' if cb == 'main' else ('main' if cb == 'accent' else max(('main', 'accent'), key=lambda k: contrast(pick[k], D)))
        O = pick.get(str(d.get('accent_color') or O0), A)        # 帯(ストーリー・ギャラリー)・見出し・ボタン。空ならもう一方
        bc = str(d.get('band_color') or '').strip()
        if re.fullmatch(r'#?[0-9a-fA-F]{6}', bc):   # 「帯の色」を自由に指定したとき(帯・見出しだけ)
            O = '#' + bc.lstrip('#')
        if D == O:
            O = A if D != A else M
        dark, light = (D, O) if lum(D) < lum(O) else (O, D)
        p_ink = dark if contrast(dark, '#ffffff') >= 4.5 else deep('#ffffff', dark)   # 白い枠(遊び方・購入)の文字(黒ではなく作品の色を暗くしたもの)
        HLC = {'red': RED, 'main': M, 'accent': A, 'third': pick.get('third'), 'white': '#ffffff', 'black': '#000000'}
        hl_want = HLC.get(str(d.get('hl_color') or 'red')) or RED
        def text_hl(bg, fg_pref, fixed=None):   # (文字の色, 強調の色):強調は太字にしたところ。色を変える(基本は赤)。読みにくければほかの決めた色
            fg = ink(bg, fg_pref)
            if fixed and contrast(fixed, bg) >= 3:   # 取説で決まっている強調の色(ビビルの金など)はそのまま
                return fg, fixed
            for c in [hl_want, RED]:   # 選んだ色か赤。どちらも読みにくければ太字だけ
                if c and contrast(c, fg) >= 1.8 and contrast(c, bg) >= 3:   # 地で読めて、文字の色ともはっきり違う
                    return fg, c
            return fg, fg
        k_ink, hl = text_hl(D, O, g.get('hl_fixed'))
        b2_ink, hl2 = text_hl(O, D)
        css.append('--k-bg:%s;--k-ink:%s;--hl:%s' % (D, k_ink, hl))
        css.append('--b2-bg:%s;--b2-ink:%s;--hl2:%s' % (O, ink(O, D), hl2))
        css.append('--sec-bg:%s;--sec-ink:%s' % (O, ink(O, D)))         # 見出しのピル
        css.append('--accent:%s;--on-accent:%s' % (O, ink(O, D)))       # ふつうのボタン
        css.append('--buy-bg:%s;--buy-ink:%s' % (M, '#ffffff' if PREFW[0] and contrast(M, '#ffffff') >= 2 else ink(M, A)))         # BOOTHで購入:土台がメインカラー、文字がアクセントカラー
        soft = mix(M, '#ffffff', .15)   # 遊び方の図の下地:メインカラーを15%だけ白に重ねた色
        css.append('--p-ink:%s;--soft:%s;--pan-bg:%s;--pan-ink:#fff' % (p_ink, soft, p_ink))
        css.append('--lt:%s;--on-lt:%s;--dk:%s;--on-dk:%s' % (light, ink(light, dark), dark, ink(dark, light)))
        g['_D'] = D
        css.append('--hl-deco:%s;--hl2-deco:%s' % ('underline' if hl == k_ink else 'none', 'underline' if hl2 == b2_ink else 'none'))   # 強調が文字と同じ色なら下線
        # 項目ごとの背景色(編集画面「背景の色(項目ごと)」)。空なら今までどおり
        g['sec_style'] = {}
        for sec, typ in (('video', 'k'), ('story', 'b'), ('rules', 'k'), ('photo', 'b'), ('buy', 'k')):
            v = str((d.get('sections') or {}).get(sec + '_bg') or '').strip()
            C = pick.get(v) or (('#' + v.lstrip('#')) if re.fullmatch(r'#?[0-9a-fA-F]{6}', v) else None)
            if not C:
                continue
            oth = max((D, O, '#ffffff', '#000000'), key=lambda x: (x in (D, O), contrast(x, C) >= 3, contrast(x, C)))
            fg, h = text_hl(C, oth, g.get('hl_fixed') if typ == 'k' else None)
            deco = 'underline' if h == fg else 'none'
            tex = ''
            if typ == 'k' and d.get('bg1_image'):   # 背景の模様:地の明るさに合わせて、模様の色を白か黒に(形はそのまま)
                tex = ';--tex-c:url(../../img/%s)' % tint_tile(d['bg1_image'], '#ffffff' if lum(C) < .2 else '#000000')
            if typ == 'k':
                st = 'background-color:%s;--k-bg:%s;--k-ink:%s;--hl:%s;--hl-deco:%s;--sec-bg:%s;--sec-ink:%s;--accent:%s;--on-accent:%s;color:%s' % (C, C, fg, h, deco, oth, ink(oth, C), oth, ink(oth, C), fg) + tex
            else:
                st = '--b2-bg:%s;--b2-ink:%s;--hl2:%s;--hl2-deco:%s' % (C, fg, h, deco)
            g['sec_style'][sec] = ' style="%s"' % st
    hero(g, d, t)
    # 編集画面がすべて:画像の欄が空(消した)なら、デザイン側の初期値も使わず「なし」
    if d.get('bg1_image'):
        f, w, h = tile(d['bg1_image']); css.append('--tex-c:url(../../img/%s);--tex-size:%dpx %dpx' % (f, w, h))
    else:
        css.append('--tex-c:none')
    if d.get('bg2_image'):
        f, w, h = tile(d['bg2_image']); css.append('--b2-img:url(../../img/%s);--b2-size:%dpx %dpx' % (f, w, h))
    if d.get('band_image'):
        f, w, h = tile(loop_band(d['band_image'])); css.append('--band:url(../../img/%s);--band-h:%dpx;--band-d:block' % (f, h))
    else:
        css.append('--band-d:none')
    for k, var in (('step_num_x', '--snum-x'), ('step_num_y', '--snum-y')):   # 遊び方の番号の位置(px)
        if d.get(k) not in (None, ''):
            css.append('%s:%gpx' % (var, num(d[k], 0)))
    oc = str(d.get('heading_icon_color') or '')
    if M and A and oc:
        cc = {'main': M, 'accent': A, 'white': '#ffffff', 'black': '#000000', 'third': pick.get('third')}.get(oc)
        if cc:
            css.append('--orn-c:%s' % cc)   # 見出しの飾りの色(背景の色のところ。帯の色のところは自動)
    for k, var in (('heading_icon', '--orn'), ('step_icon', '--snum')):
        if d.get(k):
            css.append('%s:url(../../img/%s)' % (var, imgname(d[k])))
        elif k == 'heading_icon':
            css.append('--orn-d:none')    # 見出しの飾りなし
        else:
            css.append('--snum:none;--snum-r:50%')   # 番号はただの丸に
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
            note = rich_L(LL(x, 'note'))
            slides.append('<div class="chara-slide%s"%s><div class="fig-wrap">%s</div><figcaption><span class="chara-name">%s</span>%s</figcaption></div>' % (
                ' cur' if k == 0 else '', '' if k == 0 else ' aria-hidden="true"', fig, LL(x, 'name'), ('<span class="chara-note">%s</span>' % note) if note else ''))
        nav = ('<button class="cnav prev js-only" type="button" aria-label="前のキャラクター"></button><button class="cnav next js-only" type="button" aria-label="次のキャラクター"></button>'
               '<div class="cdots js-only">%s</div>' % ''.join('<i%s></i>' % (' class="on"' if k == 0 else '') for k in range(len(chars)))) if len(chars) > 1 else ''
        g['chara_html'] = '<div class="chara-slides">%s</div>%s' % (''.join(slides), nav)
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

def tri_pattern(c, base=None):   # TRICO のパッケージの三角模様。base = 地の色(なければ c を少し濃く)
    a, b = (base or mix(c, '#000000', .965)).lstrip('#'), str(c).lstrip('#')
    return ("url(\"data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' width='92' height='160'%%3E%%3Crect width='92' height='160' fill='%%23%s'/%%3E"
            "%%3Cpolygon points='0,80 46,0 92,80' fill='%%23%s'/%%3E%%3Cpolygon points='-46,160 0,80 46,160' fill='%%23%s'/%%3E%%3Cpolygon points='46,160 92,80 138,160' fill='%%23%s'/%%3E%%3C/svg%%3E\")") % (a, b, b, b)

def grid_pattern(c):   # モコチャカのカード・パッケージの方眼。c = 地の色、線は白を少し混ぜた色
    a, b = str(c).lstrip('#'), mix('#ffffff', c, .28).lstrip('#')
    return ("url(\"data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44'%%3E%%3Crect width='44' height='44' fill='%%23%s'/%%3E"
            "%%3Cpath d='M0 .75H44M.75 0V44' stroke='%%23%s' stroke-width='1.5'/%%3E%%3C/svg%%3E\")") % (a, b)

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
    theme='''
      /* 色はトップ(ボードゲーム)のメインカラー・アクセントカラーから自動(build の apply) */
      --glow:255,236,150;
      --band:url({{img:t_band.png}}); --band-h:22px;          /* 帯の模様:パッケージの三角 */
      --tex-c:url({{img:t_tex_c.png}}); --tex-size:92px 160px;
      --orb-glow:255,236,150;
      --orn:url({{img:t_bird_sten.png}}); --snum:url({{img:t_bird_sil.png}});   /* 見出しの飾り:トリコのシルエット。反転しない */
    ''',
    hero_css='''
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
    /* 1コマ目:P3(リード)が表で出す → P1・P2が裏で出す → せーの!で表に。リードプレイヤーマーカーはカードの横に横向きで */
    .tpl{position:relative;display:flex;align-items:flex-start;justify-content:center;gap:12px;padding:24px 0 6px}
    .tpl figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:6px}
    .tlab{padding:1px 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:10px;font-weight:800}
    .tpl .lf{--card-w:48px}
    .tpl .tcd{width:48px}
    .tlead{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px}
    .tlead .lead{width:44px;border-radius:3px;box-shadow:0 2px 5px rgba(0,0,0,.18)}   /* リードプレイヤーマーカーはカードの下に横向き */
    .tsay{position:absolute;left:50%;top:0;translate:-50% 0;font-size:16px;font-weight:900;color:var(--p-ink)}
    /* 2コマ目:勝利条件の図 */
    .s2 .viz{padding:8px}
    .tjbox{position:relative;width:100%;max-height:100%;aspect-ratio:2000/1124}
    .tjp{position:absolute;left:0;width:100%;object-fit:contain}
    /* 4コマ目:ニコとトリコ。2枚目で「ニコ!」、3枚目で「トリコ!」(同じ場所) */
    .t4{display:flex;flex-direction:column;align-items:center;gap:10px;width:100%}
    .t4pair{position:relative;display:grid;width:min(190px,84%)}
    .t4pair img{grid-area:1/1;width:100%}
    .t4row{position:relative;display:flex;gap:6px;padding-right:96px}
    .t4row .tcd{width:44px}
    .t4say{position:absolute;right:0;top:50%;translate:0 -50%;display:grid;width:90px;text-align:center}
    .t4say b{grid-area:1/1;padding:4px 0;border-radius:999px;font-size:15px;font-weight:900;color:#fff}
    .t4n{background:#ec6ea6}
    .t4t{background:var(--p-ink)}
    @media all{
      .t1a,.t1b{animation:t1in 7s cubic-bezier(.3,1.4,.5,1) infinite}
      .t1b{animation-name:t1in2}
      @keyframes t1in{0%,10%{opacity:0;translate:0 -24px}16%,88%{opacity:1;translate:0 0}95%,100%{opacity:0;translate:0 0}}
      @keyframes t1in2{0%,20%{opacity:0;translate:0 -24px}26%,88%{opacity:1;translate:0 0}95%,100%{opacity:0;translate:0 0}}
      .s1 .tlead{animation:t1lead 7s ease infinite}
      @keyframes t1lead{0%{opacity:0;translate:0 -20px}6%,88%{opacity:1;translate:0 0}95%,100%{opacity:0}}
      .tpl .lf{animation:t1flip 7s cubic-bezier(.3,1.2,.4,1) infinite}
      @keyframes t1flip{0%,48%{transform:rotateY(180deg)}58%,100%{transform:rotateY(0deg)}}
      .tsay{animation:t1say 7s ease infinite}
      .tjp{animation:tjin 7s cubic-bezier(.3,1.3,.5,1) infinite both;animation-delay:calc(var(--i) * .55s)}
      @keyframes tjin{0%{opacity:0;translate:-16px 0}8%,80%{opacity:1;translate:0 0}88%,100%{opacity:0;translate:0 0}}
      @keyframes t1say{0%,34%{opacity:0;scale:.4}39%{opacity:1;scale:1.15}42%,52%{opacity:1;scale:1}58%,100%{opacity:0;scale:.6}}
      .t4c{animation:t4c0 7s cubic-bezier(.3,1.4,.5,1) infinite}
      .t4c[style*="--k:1"]{animation-name:t4c1}.t4c[style*="--k:2"]{animation-name:t4c2}
      @keyframes t4c0{0%{opacity:0;translate:0 -24px}5%,88%{opacity:1;translate:0 0}95%,100%{opacity:0;translate:0 0}}
      @keyframes t4c1{0%,24%{opacity:0;translate:0 -24px}29%,88%{opacity:1;translate:0 0}95%,100%{opacity:0;translate:0 0}}
      @keyframes t4c2{0%,46%{opacity:0;translate:0 -24px}50.5%,88%{opacity:1;translate:0 0}95%,100%{opacity:0;translate:0 0}}
      .t4n{animation:t4n 7s ease infinite}
      @keyframes t4n{0%,26%{opacity:0;scale:.4}30%{opacity:1;scale:1.12}33%,47%{opacity:1;scale:1}50%,100%{opacity:0;scale:.6}}
      .t4t{animation:t4t 7s ease infinite}
      @keyframes t4t{0%,50%{opacity:0;scale:.4}52%{opacity:1;scale:1.15}55%,88%{opacity:1;scale:1}95%,100%{opacity:0;scale:.6}}
      .t4pair{animation:t4pair 7s ease infinite}
      .t4p2{animation:t4look 7s steps(1) infinite}   /* トリコ!でニコがこっちを向く */
      .t4p1{animation:t4look1 7s steps(1) infinite}
      @keyframes t4look{0%{opacity:0}50.5%{opacity:1}95%{opacity:0}}
      @keyframes t4look1{0%{opacity:1}50.5%{opacity:0}95%{opacity:1}}
      @keyframes t4pair{0%,50.5%{translate:0 0}53%{translate:0 -8px}57%{translate:0 0}61%{translate:0 -4px}65%,100%{translate:0 0}}
    }
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
        # 遊び方動画(trico_howto)の6つの説明を4コマに
        dict(cls='s1', b=L('リードプレイヤーが1枚を表向きに出したら、他の2人は裏向きに出して[[同時に公開!]]', 'The lead player plays a card face up; the other two play face down and [[reveal at the same time!]]'),
             v='<div class="tpl">'
               '<figure class="t1a"><span class="tlab">P1</span>' + tlf('p3', 0) + '</figure>'
               '<figure class="t1b"><span class="tlab">P2</span>' + tlf('r27', 1) + '</figure>'
               '<figure class="lead-col"><span class="tlab">P3</span><span class="tlead">' + tcard('p24') + '<img class="lead" src="{{img:tc_lead_h.webp}}" alt="リードプレイヤーマーカー"></span></figure>'
               '<span class="tsay">' + L('せーの!', 'Reveal!') + '</span></div>'),
        dict(cls='s2', b=L('場に揃った[[色の数]]で勝敗を決める!', 'The [[number of colors]] on the table decides the winner!'),
             v='<div class="tjbox" role="img" aria-label="アピールの勝利条件:場の色が1色なら最も大きい数、2色なら同じ色の中で最も小さい数、3色なら最も大きい数。勝ったカードが複数あった場合アピールは無効となり、全て捨て札になる。"><img class="tjp" style="--i:0;top:0.00%;height:16.93%" src="{{img:t_judge_0.webp}}" alt=""><img class="tjp" style="--i:1;top:20.31%;height:20.94%" src="{{img:t_judge_1.webp}}" alt=""><img class="tjp" style="--i:2;top:44.02%;height:20.94%" src="{{img:t_judge_2.webp}}" alt=""><img class="tjp" style="--i:3;top:67.56%;height:20.94%" src="{{img:t_judge_3.webp}}" alt=""><img class="tjp" style="--i:4;top:91.18%;height:5.98%" src="{{img:t_judge_4.webp}}" alt=""></div>'),
        dict(cls='s3', b=L('場の色が2色なので、[[紫の中で最も小さい3の勝ち!]] 勝った人は場の3枚から[[好きなカードを1枚獲得]]し、手元に表向きで置く!', 'Two colors on the table, so [[the lowest purple, 3, wins!]] The winner [[takes any one]] of the 3 cards and places it face up.'),
             v='<div class="tp3">' + tcard('p3', 0) + '<span class="tpick">' + tcard('r27', 1) + '<b>' + L('獲得!', 'Take!') + '</b></span>' + tcard('p24', 2) + '</div>'),
        dict(cls='s4', b=L('手元のカードが2色になったら[[「ニコ!」]]、3色になったら[[「トリコ!」]]と宣言! [[宣言した人がラウンド勝利!]]', 'Declare [[“Nico!”]] at 2 colors and [[“Trico!”]] at 3! [[Whoever declares Trico wins the round!]]'),
             v='<div class="t4"><span class="t4pair"><img class="t4p1" src="{{img:t_pair_a.webp}}" alt="ニコとトリコ"><img class="t4p2" src="{{img:t_pair.webp}}" alt=""></span><div class="t4row">'
               '<span class="t4c" style="--k:0">' + tcard('r27') + '</span><span class="t4c" style="--k:1">' + tcard('y21') + '</span><span class="t4c" style="--k:2">' + tcard('p9') + '</span>'
               '<span class="t4say"><b class="t4n">' + L('ニコ!', 'Nico!') + '</b><b class="t4t">' + L('トリコ!', 'Trico!') + '</b></span></div></div>'),
    ],
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
    hl_fixed='#f2d756',   # 強調は取説の金色のまま
    description='ビビルの塔:数字カードを同時に出し、高い塔を建てて得点を競う2〜4人用のカードゲーム。パンダキネマ。',
    theme='''
      /* 色はトップ(ボードゲーム)のメインカラー・アクセントカラーから自動(build の apply) */
      --glow:170,215,225;
      --band:url({{img:b_band.png}}); --band-h:24px;          /* 帯の境目:塔の模様(ビビル文字) */
      --tex-c:url({{img:b_tex_c.png}}); --tex-size:525px 175px; --tex-a:rgba(255,241,207,.035);
      --orb-glow:27,185,238;
      --orn:url({{img:b_tupa_sten.png}}); --snum:url({{img:b_tupa_sil.png}});   /* 見出しの飾り:トゥーパ(トークン)のシルエット。反転しない */
    ''',
    hero_css='',
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
    gallery=[('g_rule.webp', '説明シート「ビビルの塔はこんなゲーム!」', 'Rules summary sheet', 'wide'), ('g_pkg_front.webp', 'パッケージ(表)', 'Box (front)', ''), ('g_pkg_back.webp', 'パッケージ(裏)', 'Box (back)', '')],
    gallery_todo=[('プレイ中の写真', 'Gameplay photos'), ('内容物の写真', 'Components photo')],
    pkg='b_pkg.webp', pkg_size=(498, 760),
    contents=L('カード40枚(1〜10が4セット)、トゥーパ トークン5個、遊び方説明書(JA/EN)各1枚', '40 cards (1–10 ×4), 5 Tupa tokens, rulebook (JA/EN)'),
    price=L('3,300円', '¥3,300'),
    credits=[(L('ゲームデザイン・アートワーク', 'Game Design & Artwork'), L('ゐするぎ', 'Isurugi')), (L('印刷', 'Printing'), L('萬印堂 様', '萬印堂')), (L('トークン製造', 'Tokens'), L('Sui Works 様', 'Sui Works')), ('Special Thanks', L('テストプレイをしてくれた皆さん', 'Everyone who playtested')), (L('発行', 'Published'), L('2026年10月', 'October 2026'))],
)

# ---- モコチャカ:くり返し動く図の部品(カードは new/img/parts/mc_*.webp)
MN = {'m': 'モコ', 'p': 'パカ', 'o': 'ポメ', 'g': 'ガブ'}
def mcd(code, cls='', st=''):   # 表向きのカード(m2 = モコが2匹)
    return '<img class="mcd %s" style="%s" src="{{img:mc_%s.webp}}" alt="%sが%s匹のカード">' % (cls, st, code, MN[code[0]], code[1:])
def mfield(top, bl, br, extra=''):   # 場:3つの山(上・左下・右下)と中央のトークン(かんたんルールの図と同じ並び)
    return ('<div class="mpile mt">%s</div><div class="mpile ml">%s</div><div class="mpile mr">%s</div>'
            '<img class="mtok" src="{{img:m_token.webp}}" alt="トークン">%s') % (top, bl, br, extra)
def mdeck(label):   # 手札(裏向きの束)
    return '<div class="mdeck"><img class="mcd" src="{{img:mc_ura.webp}}" alt=""><img class="mcd" src="{{img:mc_ura.webp}}" alt=""><img class="mcd" src="{{img:mc_ura.webp}}" alt="手札"></div><span class="mcap">%s</span>' % label

# ---- モコチャカ:場はトークンを中心に放射状(上は縦、左下・右下は斜め)。カードの頭はトークンへ向ける
MK_T = (150, 96)   # トークンの中心
MK_P = [(150, 33, '180deg'), (94, 134, '60deg'), (206, 134, '-60deg')]   # 上・左下・右下の山(中心x, 中心y, 向き)
def mkc(code, cls=''):
    return '<img class="mkc %s" src="{{img:mc_%s.webp}}" alt="%sが%s匹のカード">' % (cls, code, MN[code[0]], code[1:])
def mkdeck():
    return '<div class="mkdeck"><img class="mkc" src="{{img:mc_ura.webp}}" alt=""><img class="mkc" src="{{img:mc_ura.webp}}" alt=""><img class="mkc" src="{{img:mc_ura.webp}}" alt="手札"></div><span class="mkcap">' + L('手札', 'Hand') + '</span>'
def mkfield(top, bl, br, piles=1, take=False):
    out = []
    under = {'m': ['m1', 'm3'], 'p': ['p1', 'p3'], 'o': ['o3', 'o1']}
    for k, ((cx, cy, r), code) in enumerate(zip(MK_P, (top, bl, br))):
        cards = (under.get(code[0], [code, code])[:piles - 1] if piles > 1 else []) + [code]
        cls = ''
        st = '--cx:%dpx;--cy:%dpx;--r:%s' % (cx, cy, r)
        if take and k in (0, 1):   # 取った人が選ぶ山(上と左下)→手札の位置へ
            cls = ' take' + (' t2' if k == 1 else '')
            st += ';--pdx:%dpx;--pdy:%dpx' % (23 - cx, 96 - cy)
        back = '<img class="mkc mkbk" src="{{img:mc_ura.webp}}" alt="">' if take and k in (0, 1) else ''
        out.append('<div class="mkp%s" style="%s">%s%s</div>' % (cls, st, ''.join(mkc(c) for c in cards), back))
    tok = '<img class="mktok" style="--tx:%dpx;--ty:%dpx;--tdx:%dpx;--tdy:%dpx" src="{{img:m_token.webp}}" alt="トークン">' % (MK_T[0], MK_T[1], 23 - MK_T[0], 156 - MK_T[1])   # 取ったトークンは手札の下へ
    return ''.join(out) + tok
def mkpl(i, name, cards, n0, n1, win=False):
    hand = ''.join(mkc(c, 'g' if c[0] == 'g' else '') for c in cards) if cards else '<span class="zero">0</span>'
    n = '<span class="n"><span class="a">%s</span><span class="b">%s</span></span>' % (L('%d枚' % n0, '%d' % n0), L('%d枚' % n1, '%d' % n1))
    return '<div class="pl" style="--i:%d"><span class="lab"><b>%s</b>%s%s</span><div class="hand">%s</div></div>' % (i, name, n, ('<span class="win">' + L('勝ち!', 'Win!') + '</span>') if win else '', hand)

GAMES['moko'] = dict(
    title='モコチャカ',
    description='モコチャカ:場に見えている3枚のカードの動物を数えて、素早く名前を呼ぶ2〜4人用のカードゲーム。パンダキネマ。',
    theme='''
      /* 色はトップ(ボードゲーム)のメインカラー・アクセントカラーから自動(build の apply) */
      --glow:241,158,188;
      --band:url({{img:m_band.png}}); --band-h:20px;            /* 帯の模様:カードの「### Moko ###」の柵 */
      --tex-c:url({{img:m_tex_c.png}}); --tex-size:36px 36px;   /* 背景:説明書の方眼 */
      --orb-glow:241,158,188;
      --orn:url({{img:m_moko_sten.png}}); --snum:url({{img:m_moko_sil.png}});   /* 見出しの飾り:モコのシルエット */
    ''',
    hero_css='''
    /* ===== モコチャカ:トップ ===== */
    @media (max-width:650px){ .hero .stage{width:min(var(--sw,380px),84vw)} }
    .hero.hero-stage{padding-bottom:22px}
    .hero.hero-stage::after{content:"";position:absolute;left:0;right:0;bottom:0;height:22px;   /* カードの縁と同じ波で、下の帯と区切る */
      background:radial-gradient(circle at 50% 0,transparent 10.5px,var(--k-bg) 11.5px) 0 0/26px 22px repeat-x}
    /* ===== モコチャカ:遊び方の図(場はトークンを中心に放射状。カードの頭はトークンへ) ===== */
    .mkf{position:relative;flex:none;width:252px;height:182px}
    .mkc{display:block;width:46px;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.18)}
    .mkp{position:absolute;left:calc(var(--cx) - 23px);top:calc(var(--cy) - 32px);width:46px;height:64px;rotate:var(--r)}
    .mkp .mkc{position:absolute;left:0;top:0}
    .mkp .mkc:nth-child(2){translate:1.5px -2px;rotate:3deg}
    .mkp .mkc:nth-child(3){translate:-1.5px -4px;rotate:-2deg}
    .mktok{position:absolute;left:calc(var(--tx) - 18px);top:calc(var(--ty) - 18px);width:36px;z-index:4;filter:drop-shadow(0 3px 4px rgba(0,0,0,.2))}
    .mkdeck{position:absolute;left:0;top:62px;width:46px;height:68px;z-index:5}
    .mkdeck .mkc{position:absolute;left:0;top:0}
    .mkdeck .mkc:nth-child(2){top:-3px}.mkdeck .mkc:nth-child(3){top:-6px}
    .mkcap{position:absolute;left:23px;top:36px;translate:-50% 0;padding:1px 9px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:10.5px;font-weight:800;white-space:nowrap;z-index:6}
    .mkmv{position:absolute;left:calc(var(--cx) - 23px);top:calc(var(--cy) - 32px);width:46px;height:64px;z-index:6}
    .mkmv .mkc{position:absolute;left:0;top:0}
    .mkbub{position:absolute;padding:3px 11px;border-radius:999px;background:#e8467a;color:#fff;font-size:13px;font-weight:900;white-space:nowrap;letter-spacing:.04em;z-index:7}
    /* 2コマ目:3つの例。カードを横に並べて右に吹き出し */
    .mk2{display:grid;gap:6px;width:100%}
    .mk2 .row{display:flex;align-items:center;justify-content:center;gap:3px}
    .mk2 .mkc{width:40px}
    .mk2 .mkbub{position:relative;margin-left:8px;font-size:12px}
    .mk2 .mkbub::before{content:"";position:absolute;left:-5px;top:50%;translate:0 -50%;border:5px solid transparent;border-right-color:#e8467a;border-left:0}
    /* 3コマ目:モコチャカ!→トークンを取って手札の横へ、山2つが手札の下に入る */
    .mk3 .mkp.take{z-index:2}
    .mkp .mkbk{opacity:0;translate:0 0;rotate:0deg}
    /* 4コマ目:4人の手札。ガブは消える */
    .mk4{display:grid;grid-template-columns:1fr 1fr;gap:10px 6px;width:100%;padding-top:10px}
    .mk4 .pl{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;padding:4px 0}
    .mk4 .lab{position:relative;display:flex;gap:6px;align-items:center;font-size:10.5px;font-weight:800}
    .mk4 .lab b{padding:0 7px;border-radius:999px;background:var(--p-ink);color:#fff}
    .mk4 .hand{display:flex;justify-content:center;height:48px;align-items:flex-end;width:100%}
    .mk4 .hand .mkc{width:32px;margin-left:-14px;box-shadow:0 1px 3px rgba(0,0,0,.18)}
    .mk4 .hand .mkc:first-child{margin-left:0}
    .mk4 .zero{display:grid;place-items:center;width:32px;height:44px;border:2px dashed color-mix(in srgb,var(--p-ink) 40%,transparent);border-radius:4px;font-size:10px;font-weight:800}
    .mk4 .win{position:absolute;left:50%;bottom:calc(100% + 2px);translate:-50% 0;padding:0 7px;white-space:nowrap;border-radius:999px;background:#e8467a;color:#fff;font-size:11px;font-weight:900}
    .mk4 .n{min-width:0}
    @media all{
      /* 1:手札からめくりながら左下の山へ */
      .s1 .mkmv{animation:mkmv 6s cubic-bezier(.4,0,.2,1) infinite}
      @keyframes mkmv{0%,10%{opacity:1;translate:var(--dx) var(--dy);rotate:0deg}42%,86%{opacity:1;translate:0 0;rotate:var(--r)}93%,100%{opacity:0;translate:0 0;rotate:var(--r)}}
      .s1 .mkmv .mkf1{animation:mkfl 6s linear infinite}
      .s1 .mkmv .mkb1{animation:mkbk 6s linear infinite}
      @keyframes mkfl{0%,25.9%{opacity:0}26%,100%{opacity:1}}
      @keyframes mkbk{0%,25.9%{opacity:1}26%,100%{opacity:0}}
      .s1 .mkmv>span{display:block;width:46px;height:64px;position:relative;animation:mksq 6s ease-in-out infinite}
      @keyframes mksq{0%,14%{scale:1 1}26%{scale:0 1}38%,100%{scale:1 1}}
      .s1 .mkbub{animation:mkpop 6s ease infinite}
      @keyframes mkpop{0%,46%{opacity:0;scale:.4}52%{opacity:1;scale:1.12}56%,86%{opacity:1;scale:1}92%,100%{opacity:0;scale:.6}}
      /* 2:1行ずつ */
      .mk2 .row{animation:mkrow 8s cubic-bezier(.3,1.3,.5,1) infinite both;animation-delay:calc(var(--i) * .9s)}
      @keyframes mkrow{0%{opacity:0;translate:-14px 0}6%,78%{opacity:1;translate:0 0}86%,100%{opacity:0;translate:0 0}}
      .mk2 .mkbub{animation:mkb2 8s ease infinite both;animation-delay:calc(var(--i) * .9s)}
      @keyframes mkb2{0%,8%{opacity:0;scale:.4}13%{opacity:1;scale:1.12}16%,78%{opacity:1;scale:1}86%,100%{opacity:0}}
      /* 3:モコチャカ!→トークン→山2つ */
      .s3 .mkbub{animation:mk3b 8s ease infinite}
      @keyframes mk3b{0%,6%{opacity:0;scale:.4}11%{opacity:1;scale:1.12}14%,80%{opacity:1;scale:1}88%,100%{opacity:0;scale:.6}}
      .s3 .mktok{animation:mk3t 8s cubic-bezier(.5,0,.3,1) infinite}
      @keyframes mk3t{0%,14%{translate:0 0;rotate:0deg}16%{rotate:-10deg}18%{rotate:8deg}20%{rotate:0deg}34%,84%{opacity:1;translate:var(--tdx) var(--tdy)}92%,100%{opacity:0;translate:var(--tdx) var(--tdy)}}
      .s3 .mkp.take{animation:mk3p 8s cubic-bezier(.5,0,.3,1) infinite}
      .s3 .mkp.take.t2{animation-name:mk3p2}
      @keyframes mk3p{0%,38%{opacity:1;translate:0 0;rotate:var(--r);scale:1 1}43%{scale:0 1}48%{scale:1 1}58%{opacity:1;translate:var(--pdx) var(--pdy);rotate:0deg}64%,100%{opacity:0;translate:var(--pdx) var(--pdy);rotate:0deg}}
      @keyframes mk3p2{0%,48%{opacity:1;translate:0 0;rotate:var(--r);scale:1 1}53%{scale:0 1}58%{scale:1 1}68%{opacity:1;translate:var(--pdx) var(--pdy);rotate:0deg}74%,100%{opacity:0;translate:var(--pdx) var(--pdy);rotate:0deg}}
      .s3 .mkp.take .mkc{outline:2px solid transparent;animation:mk3o 8s ease infinite}
      .s3 .mkp.take .mkbk{animation:mk3k 8s steps(1) infinite;outline:none}.s3 .mkp.take.t2 .mkbk{animation-name:mk3k2}
      @keyframes mk3k{0%{opacity:0}43%{opacity:1}100%{opacity:1}}
      @keyframes mk3k2{0%{opacity:0}53%{opacity:1}100%{opacity:1}}
      @keyframes mk3o{0%,30%{outline-color:transparent}33%,50%{outline-color:#e8467a}56%,100%{outline-color:transparent}}
      /* 4:ガブが消える→枚数→勝ち */
      .mk4 .pl{animation:mk4p 8s ease infinite both;animation-delay:calc(var(--i) * .25s)}
      @keyframes mk4p{0%{opacity:0;translate:0 8px}6%,86%{opacity:1;translate:0 0}94%,100%{opacity:0}}
      .mk4 .g{animation:mk4g 8s linear infinite}
      @keyframes mk4g{0%,26%{display:block;opacity:1;translate:0 0;filter:none}28%,30%,32%,34%{translate:0 -6px;filter:drop-shadow(0 0 3px #e8467a) drop-shadow(0 0 3px #e8467a)}29%,31%,33%{translate:0 0}36%{display:block;opacity:1}36.5%,100%{display:none;opacity:0}}   /* ガブは跳ねて光ってから、ぱっと消える。残りは真ん中にそろう */
      .mk4 .n .a{animation:mk4a 8s steps(1) infinite}.mk4 .n .b{animation:mk4b 8s steps(1) infinite}
      @keyframes mk4a{0%{display:inline}36.5%,100%{display:none}}
      @keyframes mk4b{0%{display:none}36.5%,100%{display:inline}}
      .mk4 .win{animation:mkpop 8s ease infinite;animation-delay:.6s}
    }
''',
    logo='m_logo_navy.png', logo_size=(1282, 240), logo_alt='モコチャカ MOKOCHAKA',
    logo_buy='m_logo_navy.png', logo_credits='logo_moko.png',
    chara_name=L('モコ', 'Moko'),
    chara_fig='<img class="solo" src="{{img:m_moko.webp}}" alt="モコ">',
    piece_img='m_token.webp', piece_alt='トークン',
    chara_note='',
    catch=L('ねむりは競争だ。', 'Sleep is a race.'),
    intro=L('あなたたちは眠りの浅瀬でモコを数えていました。', 'You were counting Moko in the shallows of sleep.'),
    intro_img=('m_moko.webp', 'モコ', ''),
    summary=L('自分の手札からカードを山に出し、[[上に見えている3枚のカードの動物を数えて素早く名前を呼ぶゲームです。]]',
              'Play cards from your hand onto the piles, and [[count the animals on the 3 cards on top and call their names fast.]]'),
    spec=[(L('人数', 'Players'), L('2〜4人', '2–4')), (L('時間', 'Time'), L('10〜15分', '10–15 min')), (L('年齢', 'Age'), L('6歳から', '6+'))],
    poster='m_stage.png',
    # 遊び方:かんたんルール「ゲームの流れ」「コール」「コールのルール」「トークンの取り合い」から(文はルールのまま、[[ ]]=赤字)
    steps=[
        # 1:手札をめくって、3つのうち好きな場に重ねる(場はトークンを中心に放射状、カードの頭はトークンへ)
        dict(cls='s1', b=L('手札を上から1枚めくって、3つのうち好きな場に重ねます。その後、場のカードを見て[[コール]]を行います。', 'Flip the top card of your hand and stack it on any of the 3 piles. Then look at the cards and make a [[call]].'),
             v='<div class="mkf">' + mkdeck() + mkfield('o1', 'm1', 'p3')
               + '<span class="mkmv" style="--cx:94px;--cy:134px;--r:60deg;--dx:-71px;--dy:-38px"><span><img class="mkc mkb1" src="{{img:mc_ura.webp}}" alt=""><img class="mkc mkf1" src="{{img:mc_p2.webp}}" alt="パカが2匹のカード"></span></span>'
               + '<span class="mkbub" style="right:0;top:4px">' + L('ポメパカ!', 'Pome-Paka!') + '</span></div>'),
        # 2:コールのルール(3つの例。どれもモコチャカにならない場)
        dict(cls='s2', b=L('コールには下記のルールがあります。\n[[・数の多い順に呼ぶ]]\n[[・ポメはかわいいので必ず最初に呼ぶ]]\n[[・ガブの数だけモコを減らす]]', 'Calls have these rules:\n[[· Call in order of most to fewest]]\n[[· Pome is cute, so always call it first]]\n[[· Remove one Moko for each Gabu]]'),
             v='<div class="mk2">'
               '<div class="row" style="--i:0">' + mkc('m3') + mkc('p1') + mkc('m1') + '<span class="mkbub" style="--i:0">' + L('モコパカ!', 'Moko-Paka!') + '</span></div>'
               '<div class="row" style="--i:1">' + mkc('p3') + mkc('o1') + mkc('p1') + '<span class="mkbub" style="--i:1">' + L('ポメパカ!', 'Pome-Paka!') + '</span></div>'
               '<div class="row" style="--i:2">' + mkc('m3') + mkc('g2') + mkc('p2') + '<span class="mkbub" style="--i:2">' + L('パカモコ!', 'Paka-Moko!') + '</span></div></div>'),
        # 3:モコチャカ!→トークンを取る(手札には重ねない)→山を2つ選んで手札の下へ
        dict(cls='s3', b=L('場のカードが条件を満たしたとき、[[「モコチャカ」]]と言いながら[[全員で]]トークンを取り合います。取った人は場の山を2つ選んで獲得し、手札の下に加えます。', 'When the cards meet a condition, [[everyone]] grabs for the token while saying [[“Mokochaka!”]] The one who gets it takes 2 piles and adds them to the bottom of their hand.'),
             v='<div class="mkf mk3">' + mkdeck() + mkfield('m2', 'p2', 'o2', piles=3, take=True)
               + '<span class="mkbub" style="right:0;top:44px">' + L('モコチャカ!', 'Mokochaka!') + '</span></div>'),
        # 4:誰かの手札がなくなったら終了。ガブを除いた手札が最も多い人の勝ち
        dict(cls='s4', b=L('誰かの手札がなくなったらゲーム終了です。[[ガブを除いた]]手札が最も多い人が勝ちです!', 'When someone runs out of cards, the game ends. The player with the most cards [[not counting Gabu]] wins!'),
             v='<div class="mk4">' + mkpl(0, 'P1', ['m1', 'g1', 'p1', 'g2', 'g1'], 5, 2) + mkpl(1, 'P2', ['m2', 'p2', 'g1', 'o1'], 4, 3, True) + mkpl(2, 'P3', [], 0, 0) + mkpl(3, 'P4', ['o2', 'g2', 'm3'], 3, 2) + '</div>'),
    ],
    gallery=[], gallery_todo=[],
    fab_pkg='pkg_moko.webp',
    pkg='pkg_moko.webp', pkg_size=(520, 825),
    contents=L('カード32枚(モコ10枚、パカ10枚、ポメ6枚、ガブ6枚)、アクリルトークン1個、遊び方説明書1枚', '32 cards (Moko 10, Paka 10, Pome 6, Gabu 6), acrylic token, rulebook'),
    price='',
    credits=[(L('ゲームデザイン・アートワーク', 'Game Design & Artwork'), L('ゐするぎ', 'Isurugi'))],
)

# ---- 共通:画像1枚
def pic(name, cls='', st='', alt=''):
    return '<img class="%s" style="%s" src="{{img:%s}}" alt="%s">' % (cls, st, name, alt)
def burst(text, cls='', st=''):   # ギザギザの吹き出し(取説の「3!」「タコ!」と同じ役目)
    return '<span class="burst %s" style="%s"><span>%s</span></span>' % (cls, st, text)
BURST_CSS = '''
    .burst{position:absolute;display:grid;place-items:center;width:62px;height:62px;background:var(--bc,#e8343d);color:#fff;font-size:14px;font-weight:900;line-height:1;white-space:nowrap;
      clip-path:polygon(50% 0,61% 18%,82% 8%,80% 30%,100% 35%,86% 52%,100% 68%,79% 72%,82% 93%,61% 84%,50% 100%,39% 84%,18% 93%,21% 72%,0 68%,14% 52%,0 35%,20% 30%,18% 8%,39% 18%)}
    .burst span{rotate:-8deg}
'''

# ===== イカタコ =====
IKN = {'2': '2', '3': '3', '4': '4', '5': '5', '8': 'タコ(8)', '10': 'イカ(10)', '18': 'イカタコ(18)'}
def icd(k, cls='', st=''):
    return pic('ic_%s.webp' % k, 'icd ' + cls, st, '%sのカード' % IKN.get(k, k))
def iring(n=14, r=64):   # ドーナツ状に並べた山札
    out = []
    for i in range(n):
        a = 360 * i / n
        out.append('<img class="irc" style="--a:%gdeg;--r:%dpx" src="{{img:ic_ura.webp}}" alt="">' % (a, r))
    return '<div class="iring" aria-hidden="true">%s</div>' % ''.join(out)

GAMES['ikatako'] = dict(
    title='イカタコ',
    description='イカタコ:めくられたカードに正しく反応し、できるだけ多くの得点を集めて生還を目指す潜水系リアクションゲーム。1〜6人。パンダキネマ。',
    theme='''
      --glow:150,210,255;
      --band:url({{img:i_band.png}}); --band-h:20px;              /* 帯の模様:泡 */
      --tex-c:url({{img:i_tex_c.png}}); --tex-size:80px 48px;     /* 背景:海溝の石壁 */
      --orb-glow:150,210,255;
      --orn:url({{img:i_squid_sten.png}}); --snum:url({{img:i_squid_sil.png}});   /* 見出しの飾り:ロゴのイカ */
    ''',
    hero_css=BURST_CSS + '''
    .cast img{width:30%;border-radius:6px;box-shadow:0 8px 16px rgba(0,0,0,.25)}
    /* ===== イカタコ:遊び方の図 ===== */
    .icd{display:block;width:46px;border-radius:5px;box-shadow:0 3px 8px rgba(0,0,0,.2)}
    .ia{position:relative;flex:none;width:240px;height:180px}
    .iring{position:absolute;left:50%;top:50%}
    .irc{position:absolute;max-width:none;left:-10px;top:-14px;width:20px;border-radius:2px;transform:rotate(var(--a)) translateY(calc(var(--r) * -1));box-shadow:0 1px 2px rgba(0,0,0,.2)}
    .ia .lf{position:absolute;left:99px;top:61px;--card-w:42px}
    .ia .lf .c{border-radius:4px}
    .s1 .burst{left:var(--x);top:var(--y);width:50px;height:50px;font-size:17px;--bc:#0a4fa0}
    .idg{display:flex;gap:10px;align-items:flex-start;justify-content:center}
    .idg figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:8px}
    .idg .icd{width:56px}
    .idg figcaption{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:11px;font-weight:800;line-height:1.2;text-align:center;white-space:nowrap}
    .idg figcaption b{padding:2px 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:11px}
    .idg figcaption em{font-style:normal;color:#e8343d;font-size:13px;font-weight:900}
    .irow{position:absolute;left:0;right:0;bottom:6px;display:flex;justify-content:center;gap:5px}
    .irow .icd{width:40px}
    .ilabel{position:absolute;left:50%;bottom:-2px;translate:-50% 0;font-size:10px;font-weight:800;opacity:.7;white-space:nowrap}
    .itake{position:absolute;left:99px;top:4px;width:42px}
    .itake .icd{width:42px}
    .s3 .burst{left:150px;top:0;width:52px;height:52px;font-size:17px;--bc:#0a4fa0}
    .iflip{display:block;transform-origin:50% 50%}
    .s4 .burst{left:8px;top:6px;width:64px;height:64px;font-size:15px}
    .itag{position:absolute;left:50%;top:-22px;translate:-50% 0;padding:1px 8px;border-radius:999px;background:#e8343d;color:#fff;font-size:11px;font-weight:800;white-space:nowrap}
    .s4 .irow{bottom:30px}
    .s4 .irow .icd{width:48px}
    /* 協力・ソロ */
    .ideck{position:absolute;left:16px;top:52px;width:46px;height:66px}
    .ideck .icd{position:absolute;left:0;top:0}.ideck .icd:nth-child(2){top:-3px}.ideck .icd:nth-child(3){top:-6px}
    .ipc{position:absolute;display:block}
    .ipc2{display:block}
    .q1 .burst,.q2 .burst,.q3 .burst{position:absolute;width:54px;height:54px;font-size:16px;--bc:#0a4fa0}
    .q3 .burst{--bc:#e8343d;font-size:13px}
    .iplus{position:absolute;left:118px;top:126px;padding:1px 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:11px;font-weight:800}
    .imiss{position:absolute;left:0;right:0;top:66px;display:flex;justify-content:center;gap:16px}
    .ipile{position:relative;display:block;width:40px;height:58px}
    .ipile .icd{position:absolute;left:0;top:0;width:40px}.ipile .icd+.icd{left:5px;top:5px;rotate:6deg}
    .ilab{position:absolute;left:50%;top:138px;translate:-50% 0;font-size:11px;font-weight:800}
    .ito{left:50%;top:auto;bottom:4px;translate:-50% 0}
    .ilab2{position:absolute;padding:1px 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:10.5px;font-weight:800;white-space:nowrap}
    .iempty{display:block;width:40px;aspect-ratio:300/420;border:2px dashed color-mix(in srgb,var(--p-ink) 40%,transparent);border-radius:4px}
    .burst.ibig{position:relative;width:86px;height:86px;font-size:15px}
    .q4 .isum b,.o4 .isum b{font-size:16px}
    .q4 .iend,.q4.step .iend{gap:8px}
    .o1 .irow{bottom:22px}
    @media all{
      .ipc,.ipc2,.ipile{animation:iin 7s cubic-bezier(.3,1.4,.5,1) infinite both;animation-delay:calc(var(--d,0) * .45s)}
      @keyframes iin{0%{opacity:0;translate:0 -18px}7%{opacity:1;translate:0 0}84%{opacity:1;translate:0 0}92%,100%{opacity:0;translate:0 0}}
      .q1 .burst,.q2 .burst,.q3 .burst,.iend .burst,.ito,.iplus{animation:lmark 7s ease infinite both;animation-delay:calc(var(--d,0) * .45s - 1.2s)}
      .o2 .iflip{animation:iflip 6s cubic-bezier(.4,1.5,.5,1) infinite}
    }
    .iminus{position:relative;display:block}
    .iend{display:flex;flex-direction:column;align-items:center;gap:14px;padding-top:18px}
    .irow2{display:flex;gap:4px}
    .irow2 .icd{width:36px}
    .isum{margin:0;font-size:13px;font-weight:900;line-height:1.3;text-align:center}
    .isum em{font-style:normal;color:#e8343d}
    .isum b{font-size:22px;color:#e8343d}
    @media all{
      .s1 .burst{animation:lmark 6s ease infinite;animation-delay:calc(var(--d) * .12s)}
      .idg figure{animation:idrop 7s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .5s)}
      @keyframes idrop{0%{opacity:0;translate:0 -20px}6%{opacity:1;translate:0 0}84%{opacity:1;translate:0 0}92%,100%{opacity:0;translate:0 0}}
      .idg figcaption{animation:icap 7s ease infinite;animation-delay:calc(var(--i) * .5s)}
      @keyframes icap{0%,12%{opacity:0;scale:.4}17%{opacity:1;scale:1.12}20%,84%{opacity:1;scale:1}92%,100%{opacity:0}}
      .itake{animation:itake 6s cubic-bezier(.5,0,.3,1) infinite}
      @keyframes itake{0%{opacity:0;translate:0 -16px}8%,40%{opacity:1;translate:0 0}62%,86%{opacity:1;translate:46px 114px}94%,100%{opacity:0;translate:46px 114px}}
      .s3 .burst{animation:lmark 6s ease infinite;animation-delay:-1.3s}
      .s4 .burst{animation:lmark 6s ease infinite;animation-delay:-1.5s}
      .iflip{animation:iflip 6s cubic-bezier(.4,1.5,.5,1) infinite}
      @keyframes iflip{0%,34%{rotate:0deg}46%,86%{rotate:180deg}94%,100%{rotate:0deg}}
      .itag{animation:lmark 6s ease infinite;animation-delay:.9s}
      .irow2>*{animation:idrop 6s cubic-bezier(.3,1.4,.5,1) infinite;animation-delay:calc(var(--i) * .12s)}
      .isum{animation:icap 6s ease infinite;animation-delay:1.2s}
    }''',
    logo='logo_ikatako.png', logo_size=(1270, 340), logo_alt='イカタコ IKATAKO',
    logo_buy='logo_ikatako.png', logo_credits='logo_ikatako.png',
    chara_name=L('巨大なイカとタコ', 'Giant squid & octopus'),
    chara_fig='<div class="cast">' + ''.join('<img style="--i:%d" src="{{img:ic_%s.webp}}" alt="%s">' % (i, k, a) for i, (k, a) in enumerate([('8', 'タコ'), ('18', 'イカタコ'), ('10', 'イカ')])) + '</div>',
    piece_img='ic_ura.webp', piece_alt='',
    chara_note='',
    catch=L('反射神経で生還せよ', 'Survive on reflexes'),
    intro=L('めくられたカードに正しく反応し、できるだけ多くの得点を集めて生還を目指す潜水系リアクションゲーム!', 'A deep-sea reaction game.'),
    intro_img=('ic_8.webp', '', ''),
    summary=L('イカタコとは山札からカードをめくり、対応するリアクションをしていくゲームです。', 'Flip cards and react.'),
    spec=[], poster='ic_ura.webp',
    # 遊び方:取説の「対戦ルール」から(文は取説のまま、[[ ]] = 赤字)
    steps=[
        dict(cls='s1', b=L('手番のプレイヤーは山札から1枚カードをめくり、場に公開します。場に出たカードに応じたリアクションを全員で行います。', 'The active player flips the top card and reveals it. Everyone reacts to the card.'),
             v='<div class="ia">' + iring() + '<span class="lf" style="--i:0"><img class="c back" src="{{img:ic_ura.webp}}" alt=""><img class="c front" src="{{img:ic_3.webp}}" alt="3のカード"></span>'
               + burst('3!', '', '--x:2px;--y:14px;--d:0') + burst('3!', '', '--x:188px;--y:10px;--d:1') + burst('3!', '', '--x:6px;--y:118px;--d:2') + burst('3!', '', '--x:184px;--y:120px;--d:3') + '</div>'),
        dict(cls='s2', b=L('危険カードは上の方にあるライトがあげる腕と対応しています。[[タコは左手、イカは右手、イカタコは両手]]です。', 'The lights on a danger card show which arm to raise: [[Octopus = left, Squid = right, Ikatako = both]].'),
             v='<div class="idg">' + ''.join('<figure style="--i:%d">%s<figcaption><b>%s</b><em>%s</em></figcaption></figure>' % (i, icd(k), h, c) for i, (k, h, c) in enumerate([
                 ('8', L('左手', 'Left'), L('タコ!', 'Tako!')), ('10', L('右手', 'Right'), L('イカ!', 'Ika!')), ('18', L('両手', 'Both'), L('イカタコ!', 'Ikatako!'))])) + '</div>'),
        dict(cls='s3', b=L('一番リアクションが早かった人は[[得点としてカードを獲得]]し、手元に並べます。間違えた、反応できなかった人は自分の得点のうち任意の1枚を[[減点(上下逆さま)]]にします。', 'The fastest player [[takes the card as points]] and lines it up. Anyone who got it wrong or didn’t react turns one point card [[upside down as a penalty]].'),
             v='<div class="ia"><span class="itake">' + icd('5') + '</span>' + burst('5!') + '<div class="irow">' + icd('2') + icd('4') + '<span style="width:40px"></span></div><span class="ilabel">' + L('得点', 'Points') + '</span></div>'),
        dict(cls='s4', b=L('山札がなくなったらゲームは終了です。得点カードの数字の合計から、減点の合計を引いたものが最終得点です。最終得点が0点以下だった場合は沈没となります。[[生還した中で最も得点の高い人が勝利]]となります。', 'When the deck runs out, the game ends. Your final score is your point cards minus your penalties. At 0 or less, you sink. [[The highest score among the survivors wins.]]'),
             v='<div class="iend"><div class="irow2">' + icd('6u', '', '--i:0') + icd('2', '', '--i:1') + '<span class="iminus" style="--i:2"><span class="iflip">' + icd('3') + '</span><b class="itag">' + L('減点', 'Penalty') + '</b></span>' + icd('4', '', '--i:3') + icd('8', '', '--i:4') + '</div>'
               '<p class="isum">6+2+4+8' + L('(得点)', '') + '<em>-3' + L('(減点)', '') + '</em><br><b>=17' + L('点!', ' pts!') + '</b></p></div>'),
        # ---- 協力ルール(取説「協力ルール」2.ゲームの流れ ①〜④)
        dict(cls='q1', b=L('手番の人は山札から1枚カードをめくり、出たカードの数字を宣言します。ただし、危険カードや特殊カードの場合は処理が変わります。', 'The active player flips a card and declares its number. Danger and special cards work differently.'),
             v='<div class="ia"><div class="ideck">' + icd('ura') + icd('ura') + icd('ura') + '</div><span class="ipc" style="left:108px;top:44px;--d:0">' + icd('2') + '</span>' + burst('2!', '', 'left:170px;top:40px;--d:1') + '</div>'),
        dict(cls='q2', b=L('宣言があっていたら、次の人に手番が移ります。山札からカードをめくり、最初の人と同様に数字を宣言します。このとき、[[前の人が宣言した数字に今出たカードの数字を足さなければいけません。]]これを繰り返します。', 'If it was right, the next player flips and declares too — [[adding this card to the number the previous player declared.]] Keep going.'),
             v='<div class="ia"><div class="ideck">' + icd('ura') + icd('ura') + icd('ura') + '</div><span class="ipc" style="left:100px;top:40px">' + icd('2') + '</span><span class="ipc" style="left:118px;top:54px;--d:2">' + icd('5') + '</span>' + burst('7!', '', 'left:174px;top:44px;--d:3') + '<span class="iplus">2+5</span></div>'),
        dict(cls='q3', b=L('計算を間違えたり、違うアクションをしてしまった場合は[[ミス]]となります。これまでに重ねたカードを1つの山にして端に避けておきます。これを[[ミス山]]といいます。ミス山が3つになったら潜水艇が沈没し、[[ゲームオーバー]]となります。', 'A wrong sum or wrong action is a [[miss]]: set the stacked cards aside as a [[miss pile]]. With 3 miss piles the sub sinks — [[game over]].'),
             v='<div class="ia">' + burst(L('ミス!', 'Miss!'), '', 'left:10px;top:10px;--d:0') + '<div class="imiss">' + ''.join('<span class="ipile" style="--d:%d">%s%s</span>' % (k, icd('ura'), icd(c)) for k, c in enumerate(['8', '10', '18'])) + '</div><span class="ilab">' + L('ミス山', 'Miss piles') + '</span><span class="itag ito" style="--d:3">' + L('ゲームオーバー', 'Game over') + '</span></div>'),
        dict(cls='q4', b=L('ゲームオーバーにならずに、山札を全てめくり切ったらゲームクリアです! この時[[最後に宣言された数字が得点]]となります。できるだけ多くの得点を獲得し、深海から生還しましょう!', 'Flip the whole deck without a game over to clear! [[The last number declared is your score.]] Score as much as you can and make it back from the deep!'),
             v='<div class="iend"><span class="iempty"></span>' + burst(L('クリア!', 'Clear!'), 'ibig', '--d:0') + '<p class="isum">' + L('最後の宣言が得点', 'Last number = score') + '<br><b>' + L('めざせ!100点越え!', 'Aim for 100+!') + '</b></p></div>'),
        # ---- ソロルール(取説「ソロルール」ゲームの流れ ②〜⑤)
        dict(cls='o1', b=L('カードを1枚引き、得点として配置します。2枚目以降は、すでにある得点の右か左、もしくは[[差し込み]]で配置します。[[トラブルカードが出た時は得点とは別に置いてください。]]', 'Draw a card and place it as points — to the right or left of your row, or [[slide it in]] between. [[Trouble cards go to one side.]]'),
             v='<div class="ia"><span class="ipc" style="left:12px;top:4px;--d:3">' + icd('rep') + '</span><span class="ilab2" style="left:62px;top:28px">' + L('トラブルは別に', 'Trouble aside') + '</span><div class="irow">' + icd('3') + icd('4') + '<span class="ipc2" style="--d:1">' + icd('2') + '</span></div><span class="ilabel">' + L('得点', 'Points') + '</span></div>'),
        dict(cls='o2', b=L('サルベージまたはうずしおを引いた場合は特殊行動を行います。うずしお:このカードを配置した時、[[隣接する得点カードを上下逆さまにします。]]得点は減点になり、減点は得点になります。', 'Salvage or Uzushio trigger special actions. Uzushio: [[flip the neighboring point cards upside down]] — points become penalties and vice versa.'),
             v='<div class="ia"><div class="irow">' + icd('3') + '<span class="iminus"><span class="iflip">' + icd('4') + '</span></span><span class="ipc2" style="--d:0">' + icd('6u') + '</span></div><span class="ilab2" style="left:150px;top:26px">' + L('うずしお', 'Uzushio') + '</span></div>'),
        dict(cls='o3', b=L('どんどんカードを引いていき、終了条件を満たすか、[[帰投]]を選択したらゲームを終了し、最終得点を計算します。[[役が成立していたらボーナス点]]を得ることができます。', 'Keep drawing until an end condition is met or you choose to [[return]]. Then total your score — [[sets earn bonus points.]]'),
             v='<div class="iend"><div class="irow2">' + icd('3', '', '--i:0') + icd('3', '', '--i:1') + icd('3', '', '--i:2') + '</div><p class="isum">' + L('狭域', 'Narrow') + '<br><b>+15' + L('点', '') + '</b></p></div>'),
        dict(cls='o4', b=L('得点が確定したら、ソロルール用サマリーの「最終得点評価」の称号を確認しましょう。[[目指せ!深海の覇者!!]]', 'Once your score is set, check your title on the solo summary card. [[Become the ruler of the deep!!]]'),
             v='<div class="iend">' + burst(L('72点!', '72 pts!'), 'ibig', '--d:0') + '<p class="isum">' + L('合計51+役30+帰投2−減点11', '51 + 30 + 2 − 11') + '<br><b>' + L('称号は…?', 'Your title…?') + '</b></p></div>'),
    ],
    gallery=[], gallery_todo=[],
    tabs=[(L('対戦ルール', 'Versus'), '', 0, 4), (L('協力ルール', 'Co-op'), '', 4, 8), (L('ソロルール', 'Solo'), '', 8, 12)],
    fab_pkg='pkg_ikatako.webp', pkg='pkg_ikatako.webp', pkg_size=(520, 825),
    contents=L('', ''), price='', credits=[],
)

# ===== こいこいのぼり 真打 =====
KCN = {'b': '青', 'g': '緑', 'r': '赤', 'k': '黒'}
def kcd(k, cls='', st=''):
    return pic('kc_%s.webp' % k, 'kcd ' + cls, st, ('%sの%s' % (KCN[k[0]], k[1:])) if k[0] in KCN and k != 'ura' else '')
FISH = '<img class="kfish" src="{{img:k_fish.webp}}" alt="おさかなトークン">'
SKY = '<img src="{{img:kc_sl.webp}}" alt="そらカード"><img src="{{img:kc_sr.webp}}" alt="そらカード">'
GAMES['koikoi'] = dict(
    video_tex=True,   # 動画の背景にも模様
    title='こいこいのぼり 真打',
    description='こいこいのぼり 真打:花札の「こいこい」をもとにした、鯉のぼりのカードゲーム。2人用。パンダキネマ。',
    theme='''
      --glow:255,255,255;
      --band:url({{img:k_band.png}}); --band-h:16px;            /* 帯の模様:青海波 */
      --tex-c:url({{img:k_tex_c.png}}); --tex-size:64px 32px;    /* 背景:青海波 */
      --orb-glow:255,255,255;
      --orn:url({{img:k_koi_sten.png}}); --snum:url({{img:k_fish.png}});   /* 見出しの飾り:こいのぼり */
    ''',
    hero_css='''

    .buy-box.buy-box{grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:36px}   /* 横長のパッケージ:パッケージをロゴより大きく */
    .buy-box.buy-box .buy-logo{width:min(220px,100%)}
    @media (max-width:650px){ .buy-box.buy-box{grid-template-columns:1fr} }
    @media (max-width:650px){ .buy-box.buy-box .pkg{width:min(340px,92%)} .buy-box .buy-logo{width:min(200px,70%)} }
    .snum.snum{width:68px;height:40px;font-size:22px}   /* 番号の下のおさかな:横長なので大きく */
    /* ===== こいこいのぼり:遊び方の図 ===== */
    .kcd{display:block;width:38px;border-radius:3px;box-shadow:0 2px 6px rgba(0,0,0,.18)}
    .kcap{position:absolute;padding:1px 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:10px;font-weight:800;white-space:nowrap}
    .kbub{position:absolute;padding:2px 10px;border-radius:999px;background:#e8343d;color:#fff;font-size:12px;font-weight:900;white-space:nowrap;z-index:3}
    /* 1:手札と山札からペア */
    .ka{position:relative;flex:none;width:240px;height:182px}
    .ka>.kcd,.ka .kmv{position:absolute}
    .ka .kmv{z-index:2}
    .ka .kmv .kcd{position:absolute;left:0;top:0}
    /* 2:役の一覧 */
    .kyaku{display:flex;flex-direction:column;gap:9px}
    .kyaku .row{display:flex;align-items:center;gap:10px}
    .kyaku .cs{display:flex;width:128px}
    .kyaku .kcd{width:28px;margin-right:-4px}
    .kyaku p{margin:0;padding:2px 10px;border-radius:999px;background:#e8343d;color:#fff;font-size:11px;font-weight:900;white-space:nowrap}
    /* 3・4:そらカードとおさかなトークン */
    .ksk{position:relative;flex:none;width:234px;display:flex;flex-direction:column;align-items:center;gap:8px}
    .ksora{position:relative;display:flex;gap:2px}
    .ksora>img{width:116px;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.18)}
    .ksora>img.kfish{position:absolute;left:var(--fx,100px);top:24px;width:34px;border-radius:0;box-shadow:none;z-index:2;filter:drop-shadow(0 0 1.5px #fff) drop-shadow(0 1px 2px rgba(0,0,0,.4))}
    .kside{display:flex;justify-content:space-between;width:100%;margin-top:-4px}
    .kside span{padding:0 8px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:10px;font-weight:800}
    .kchoice{display:flex;gap:8px}
    .kchoice b{padding:3px 12px;border-radius:999px;background:#fff;color:var(--p-ink);border:2px solid var(--p-ink);font-size:13px;font-weight:900}
    .kmsg{position:relative;width:100%;height:34px}
    .kmsg p{position:absolute;inset:0;margin:0;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:800;line-height:1.35;color:var(--p-ink);text-align:center}
    .kmsg p em{font-style:normal;color:#e8343d}
    .kround{position:relative;height:22px;width:100%}
    .kround b{position:absolute;left:50%;translate:-50% 0;padding:2px 12px;border-radius:999px;background:var(--p-ink);color:#fff;font-size:12px;font-weight:900;white-space:nowrap}
    .ksk .kwin{right:22px;bottom:86px}
    @media all{
      /* 1:手札→ペア、山札をめくる→ペア */
      .s1 .kmv.h{animation:kmh 10s cubic-bezier(.5,0,.3,1) infinite both}
      @keyframes kmh{0%,8%{translate:0 0;opacity:1}24%,90%{translate:var(--dx) var(--dy);opacity:1}96%{translate:var(--dx) var(--dy);opacity:0}96.1%,100%{translate:0 0;opacity:0}}
      .s1 .kmv.d{animation:kmd 10s cubic-bezier(.5,0,.3,1) infinite both}
      @keyframes kmd{0%,44%{translate:0 0;opacity:1;scale:1 1}48%{scale:0 1;translate:0 -6px}52%{scale:1 1;translate:0 -10px}68%,90%{translate:var(--dx) var(--dy);opacity:1;scale:1 1}96%{translate:var(--dx) var(--dy);opacity:0}96.1%,100%{translate:0 0;opacity:0}}
      .s1 .kmv.d .back{animation:kback 10s steps(1) infinite}
      .s1 .kmv.d .front{animation:kfront 10s steps(1) infinite}
      @keyframes kback{0%,47.9%{opacity:1}48%,96%{opacity:0}96.1%,100%{opacity:1}}
      @keyframes kfront{0%,47.9%{opacity:0}48%,96%{opacity:1}96.1%,100%{opacity:0}}
      .s1 .kbub.p1{animation:kp1 10s ease infinite both}
      .s1 .kbub.p2{animation:kp2 10s ease infinite both}
      @keyframes kp1{0%,24%{opacity:0;scale:.3}27%{opacity:1;scale:1.18}30%,90%{opacity:1;scale:1}95%,100%{opacity:0;scale:.6}}
      @keyframes kp2{0%,68%{opacity:0;scale:.3}71%{opacity:1;scale:1.18}74%,90%{opacity:1;scale:1}95%,100%{opacity:0;scale:.6}}
      /* 2:役が1つずつ */
      .kyaku .row{animation:kdrop 9s cubic-bezier(.3,1.4,.5,1) infinite both;animation-delay:calc(var(--i) * .9s)}
      @keyframes kdrop{0%{opacity:0;translate:0 -14px}6%{opacity:1;translate:0 0}80%{opacity:1;translate:0 0}88%,100%{opacity:0;translate:0 0}}
      /* 3:あがり と こいこい */
      .s4 .kchoice b{animation:kc1 10s steps(1) infinite both}
      .s4 .kchoice b+b{animation-name:kc2}
      @keyframes kc1{0%,49.9%{background:#e8343d;color:#fff;border-color:#e8343d}50%,100%{background:#fff;color:var(--p-ink);border-color:var(--p-ink)}}
      @keyframes kc2{0%,49.9%{background:#fff;color:var(--p-ink);border-color:var(--p-ink)}50%,100%{background:#e8343d;color:#fff;border-color:#e8343d}}
      .s4 .kmsg p{animation:km1 10s steps(1) infinite both}
      .s4 .kmsg p+p{animation-name:km2}
      @keyframes km1{0%,49.9%{opacity:1}50%,100%{opacity:0}}
      @keyframes km2{0%,49.9%{opacity:0}50%,100%{opacity:1}}
      .s4 .kfish{animation:kf3 10s cubic-bezier(.5,0,.3,1) infinite both}
      @keyframes kf3{0%,12%{left:100px;opacity:1}26%,46%{left:126px;opacity:1}49.9%{left:126px;opacity:0}50%,100%{left:100px;opacity:1}}
      /* 4:3局のつなひき */
      .s5 .kfish{animation:kf4 12s cubic-bezier(.5,0,.3,1) infinite both}
      @keyframes kf4{0%,6%{left:100px;opacity:1}16%,30%{left:126px}40%,54%{left:55px}66%,92%{left:163px;opacity:1}97%{left:163px;opacity:0}97.1%,100%{left:100px;opacity:0}}
      .s5 .kround b{animation:kr1 12s steps(1) infinite both}
      .s5 .kround b+b{animation-name:kr2}
      .s5 .kround b+b+b{animation-name:kr3}
      @keyframes kr1{0%,33.2%{opacity:1}33.3%,100%{opacity:0}}
      @keyframes kr2{0%,33.2%{opacity:0}33.3%,63.2%{opacity:1}63.3%,100%{opacity:0}}
      @keyframes kr3{0%,63.2%{opacity:0}63.3%,96.9%{opacity:1}97%,100%{opacity:0}}
      .s5 .kwin{animation:kp4 12s ease infinite both}
      @keyframes kp4{0%,68%{opacity:0;scale:.3}71%{opacity:1;scale:1.18}74%,92%{opacity:1;scale:1}97%,100%{opacity:0;scale:.6}}
    }''',
    logo='koikoilogo.png', logo_size=(1009, 522), logo_alt='こいこいのぼり 真打 KOIKOINOBORI SHINUCHI',
    logo_buy='koikoilogo.png', logo_credits='koikoilogo.png',
    chara_name='', chara_fig='<img class="solo" src="{{img:k_koi.webp}}" alt="">', piece_img='kc_ura.webp', piece_alt='', chara_note='',
    catch=L('あげろ!こいのぼり', 'Raise the carp streamers!'),
    intro=L('花札の『こいこい』をもとにした、鯉のぼりのカードゲーム。', 'A carp-streamer card game based on the hanafuda game Koi-Koi.'),
    intro_img=('k_koi.webp', '', ''),
    summary=L('同じ色のこいのぼりをペアで獲得し、役を作ることを目指します。', 'Collect same-colored carp streamers in pairs to make sets.'),
    spec=[], poster='kc_ura.webp',
    # 遊び方:取説の表(1・2)と「ゲームの進め方」から(文は取説のまま、[[ ]] = 赤字・見出し)
    steps=[
        dict(cls='s1', b=L('手札から1枚選び、場に出します。続けて山札を上から1枚めくります。どちらも[[場に同じ色があれば、ペアで獲得します。]]', 'Play 1 card from your hand, then flip the top card of the deck. Either way, [[if the table has the same color, take them as a pair.]]'),
             v='<div class="ka">' + kcd('b1', '', 'left:35px;top:0') + kcd('g3', '', 'left:79px;top:0') + kcd('r1', '', 'left:123px;top:0') + kcd('k5', '', 'left:167px;top:0')
               + '<span class="kcap" style="left:0;top:24px">' + L('場札', 'Table') + '</span>'
               + kcd('b5', '', 'left:50px;top:98px') + kcd('k3', '', 'left:80px;top:98px')
               + '<span class="kmv h" style="left:20px;top:98px;--dx:117px;--dy:-78px;width:38px;height:63px">' + kcd('r3') + '</span>'
               + kcd('ura', '', 'left:184px;top:104px') + kcd('ura', '', 'left:184px;top:101px')
               + '<span class="kmv d" style="left:184px;top:98px;--dx:-91px;--dy:-78px;width:38px;height:63px">' + kcd('ura', 'back') + kcd('g1', 'front') + '</span>'
               + '<span class="kcap" style="left:44px;top:166px">' + L('手札', 'Hand') + '</span><span class="kcap" style="left:184px;top:166px">' + L('山札', 'Deck') + '</span>'
               + '<span class="kbub p1" style="left:156px;top:76px">' + L('ペア!', 'Pair!') + '</span><span class="kbub p2" style="left:68px;top:76px">' + L('ペア!', 'Pair!') + '</span></div>'),
        dict(cls='s3', b=L('獲得したカードで役を作ります。\n[[1:5枚(1点)\n3:4枚(3点)\n5:色の異なる3枚(5点)]]', 'Make sets with the cards you took.\n[[1: five cards (1 pt)\n3: four cards (3 pts)\n5: three different colors (5 pts)]]'),
             v='<div class="kyaku">'
               + '<div class="row" style="--i:0"><span class="cs">' + kcd('b1') + kcd('r1') + kcd('g1') + kcd('k1') + kcd('r1') + '</span><p>' + L('1:5枚(1点)', '1: five (1 pt)') + '</p></div>'
               + '<div class="row" style="--i:1"><span class="cs">' + kcd('g3') + kcd('g3') + kcd('k3') + kcd('b3') + '</span><p>' + L('3:4枚(3点)', '3: four (3 pts)') + '</p></div>'
               + '<div class="row" style="--i:2"><span class="cs">' + kcd('b5') + kcd('r5') + kcd('k5') + '</span><p>' + L('5:色の異なる3枚(5点)', '5: 3 colors (5 pts)') + '</p></div></div>'),
        dict(cls='s4', b=L('役が成立したら[[「あがり」か「こいこい」]]を宣言します。', 'When you make a set, declare [[“Agari” or “Koi-Koi.”]]'),
             v='<div class="ksk"><div class="kchoice"><b>' + L('あがり', 'Agari') + '</b><b>' + L('こいこい', 'Koi-Koi') + '</b></div>'
               + '<div class="kmsg"><p><span>' + L('得点を確定!', 'Lock in your points!') + '</span><em>' + L('トークンを引き寄せて局を終了', 'Pull the token and end the hand') + '</em></p>'
               + '<p><span>' + L('局を続行! 次も先に役を作れば', 'Keep going! Make the next set first:') + '</span><em>' + L('成功:合計+2点 / 失敗:相手が獲得', 'Success: +2 / Fail: opponent scores') + '</em></p></div>'
               + '<div class="ksora">' + SKY + FISH + '</div><div class="kside"><span>' + L('相手', 'Opp.') + '</span><span>' + L('自分', 'You') + '</span></div></div>'),
        dict(cls='s5', b=L('得点に応じてトークンを自分側に引き寄せます。これを3局行い、[[3局終了時、トークンが自分側にあるプレイヤーの勝利です。]]', 'Pull the token toward you by your score. Play 3 hands; [[after 3 hands, the player with the token on their side wins.]]'),
             v='<div class="ksk"><div class="kround"><b>' + L('第1局 自分 +1点', 'Hand 1: You +1') + '</b><b>' + L('第2局 相手 +5点', 'Hand 2: Opp. +5') + '</b><b>' + L('第3局 自分 +10点', 'Hand 3: You +10') + '</b></div>'
               + '<div class="ksora">' + SKY + FISH + '</div><div class="kside"><span>' + L('相手', 'Opp.') + '</span><span>' + L('自分', 'You') + '</span></div><span class="kbub kwin">' + L('勝ち!', 'Win!') + '</span></div>'),
    ],
    gallery=[], gallery_todo=[],
    fab_pkg='mini_koikoi.webp', pkg='mini_koikoi.webp', pkg_size=(900, 529),
    contents=L('', ''), price='', credits=[],
)

# ===== BASH&SMASH =====
def scd(k, cls='', st=''):
    alt = '' if 'back' in k else ('%sの%s' % ('赤' if k[0] == 'r' else '青', k[1:]))
    return pic('bc2_%s.webp' % k, 'scd ' + cls, st, alt)
def sduel(a, b, ta='', tb='', extra=''):
    return '<div class="sduel"><span class="sside a">%s%s</span><b class="svs">VS</b><span class="sside b">%s%s</span>%s</div>' % (scd(a), ta, scd(b), tb, extra)

GAMES['bash'] = dict(
    video_tex=True,   # 動画の背景にも模様
    title='BASH&SMASH',
    description='BASH&SMASH(バッシュ&スマッシュ):手札から1枚出すだけの、格闘ゲーム風の読み合いゲーム。2人用。パンダキネマ。',
    theme='''
      --glow:255,220,120;
      --band:url({{img:s_band.png}}); --band-h:20px;            /* 帯の模様:星(星トークン) */
      --tex-c:url({{img:s_tex_c.png}}); --tex-size:24px 24px;    /* 背景:取説の市松 */
      --orb-glow:255,220,120;
      --orn:url({{img:s_star_sten.png}}); --snum:url({{img:s_star_sil.png}});   /* 見出しの飾り:星 */
    ''',
    hero_css=BURST_CSS + '''

    .buy-box.buy-box{grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:36px}   /* 横長のパッケージ:パッケージをロゴより大きく */
    .buy-box.buy-box .buy-logo{width:min(220px,100%)}
    @media (max-width:650px){ .buy-box.buy-box{grid-template-columns:1fr} }
    @media (max-width:650px){ .buy-box.buy-box .pkg{width:min(340px,92%)} .buy-box .buy-logo{width:min(200px,70%)} }
    /* ===== BASH&SMASH:遊び方の図 ===== */
    .scd{display:block;width:56px;border-radius:5px;box-shadow:0 3px 8px rgba(0,0,0,.22)}
    .sduel{position:relative;display:flex;align-items:center;justify-content:center;gap:12px;padding-top:18px}
    .sside{position:relative;display:block}
    .svs{font-size:22px;font-style:italic;font-weight:900;color:var(--p-ink)}
    .shit{position:absolute;left:50%;top:-24px;translate:-50% 0;padding:1px 8px;border-radius:4px;background:#e8343d;color:#fff;font-size:13px;font-weight:900;font-style:italic;white-space:nowrap}
    .shit.parry{background:#1574c4}
    .srush{position:absolute;left:50%;top:50%;translate:-50% -50%;padding:4px 14px;rotate:-6deg;background:#ffd23f;color:#1b2228;font-size:20px;font-weight:900;font-style:italic;box-shadow:0 3px 0 #1b2228;white-space:nowrap}
    .s3 .sside .scd+.scd{position:absolute;left:14px;top:12px}   /* 下のカードが見えるように少しずらす */
    .swin{display:flex;flex-direction:column;align-items:center;gap:10px}
    .swin img{width:200px;border-radius:6px;box-shadow:0 3px 8px rgba(0,0,0,.22)}
    .swin .syw{width:170px;border-radius:0;box-shadow:none}
    /* 遊び方の番号の星を少し大きく */
    .snum{width:60px;height:58px;padding-top:6px;font-size:24px}
    @media all{
      .s1 .sside,.s2 .sside{animation:sslam 6s cubic-bezier(.3,1.4,.5,1) infinite}
      .sside.a{--sx:-40px}.sside.b{--sx:40px}
      @keyframes sslam{0%{opacity:0;translate:var(--sx) 0}10%,86%{opacity:1;translate:0 0}94%,100%{opacity:0;translate:0 0}}
      .s1 .shit,.s2 .shit{animation:lmark 6s ease infinite;animation-delay:-.9s}
      .s3 .sside{animation:sslam 8s cubic-bezier(.3,1.4,.5,1) infinite}
      .s3 .scd+.scd{animation:s3b 8s cubic-bezier(.3,1.4,.5,1) infinite}
      @keyframes s3b{0%,50%{opacity:0;translate:0 -30px}58%,86%{opacity:1;translate:0 0}94%,100%{opacity:0}}
      .srush{animation:srush 8s ease infinite}
      @keyframes srush{0%,14%{opacity:0;scale:.3}20%{opacity:1;scale:1.2}24%,44%{opacity:1;scale:1}50%,100%{opacity:0;scale:.6}}
      .s3 .shit{animation:s3hit 8s ease infinite}
      @keyframes s3hit{0%,60%{opacity:0;scale:.3}66%{opacity:1;scale:1.15}70%,86%{opacity:1;scale:1}94%,100%{opacity:0}}
      .swin img{animation:kdrop2 6s cubic-bezier(.3,1.4,.5,1) infinite}
      @keyframes kdrop2{0%{opacity:0;translate:0 -24px}8%{opacity:1;translate:0 0}84%{opacity:1;translate:0 0}92%,100%{opacity:0;translate:0 0}}
      .swin .syw{animation:lmark 6s ease infinite;animation-delay:-.6s}
    }''',
    logo='bashlogo_4C.png', logo_size=(620, 490), logo_alt='BASH&SMASH! バッシュ&スマッシュ',
    logo_buy='bashlogo_4C.png', logo_credits='bashlogo_4C.png',
    chara_name=L('バッシュ', 'Bash'), chara_fig='<img class="solo" src="{{img:s_pbash.webp}}" alt="バッシュ">', piece_img='', piece_alt='', chara_note='',
    catch=L('読みきれ。叩き込め!', 'Read them. Strike hard!'),
    intro=L('大都市、グリッドシティでは至るところでバトルが行われていた。', 'In the metropolis of Grid City, battles were everywhere.'),
    intro_img=('s_pbash.webp', '', ''),
    summary=L('やることはただ1つ。手札から1枚出すだけ。', 'There is only one thing to do: play one card.'),
    spec=[], poster='sc_wbash.webp',
    # 遊び方:取説の表(1・2)と「4. ラッシュの発生」「ラウンド、ゲームの終了」から(文は取説のまま、[[ ]] = 赤字・見出し)
    steps=[
        dict(cls='s1', b=L('[[同時にカードを出し合う!]]\n数の大きい方がヒットになる!勝った数字が得点。', '[[Play cards at the same time!]]\nThe bigger number is a hit! The winning number is your score.'),
             v=sduel('r3', 'b5', '', '<b class="shit">HIT!</b>')),
        dict(cls='s2', b=L('[[裏向きで出すとパリィ!]]\n相手の出した数字に関係なく得点を奪うことができる!', '[[Play face down to Parry!]]\nYou take the points no matter what number your opponent played!'),
             v=sduel('rback', 'b4', '<b class="shit parry">Parry!</b>')),
        dict(cls='s3', b=L('お互いがヒット(攻め)で出した[[カードの合計が10になったとき、ラッシュが発生します。]]ラッシュ中はルールが反転し、小さい数字がヒット成功となります!', 'When both players attack and [[the cards add up to 10, a Rush begins.]] During a Rush the rule flips, and the smaller number hits!'),
             v='<div class="sduel"><span class="sside a">' + scd('r6') + scd('r1') + '<b class="shit">HIT!</b></span><b class="svs">VS</b><span class="sside b">' + scd('b4') + scd('b2') + '</span><span class="srush">RUSH!</span></div>'),
        dict(cls='s4', b=L('手札がなくなったら、そのラウンドは終了です。それぞれが獲得した得点を合計し、得点の高いプレイヤーがラウンドの勝者となります。[[先に2ラウンド先取したプレイヤーがゲームの勝者です。]]', 'When hands run out, the round ends. Add up your points; the higher score wins the round. [[The first player to win 2 rounds wins the game.]]'),
             v='<div class="swin"><img src="{{img:sc_wbash.webp}}" alt="勝利セリフ(バッシュ)"><img class="syw" src="{{img:s_youwin.webp}}" alt="YOU WIN!"></div>'),
    ],
    gallery=[], gallery_todo=[],
    fab_pkg='mini_bash.webp', pkg='mini_bash.webp', pkg_size=(900, 529),
    contents=L('', ''), price='', credits=[],
)

SEATS = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='76' height='64'%3E%3Cpath d='M8 64V20a14 14 0 0 1 14-14h32a14 14 0 0 1 14 14v44z' fill='black'/%3E%3C/svg%3E\")"

TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#1b2228">
  <title>{{title}} | PANDA KINEMA</title>
  <meta name="description" content="{{description}}">
  <meta property="og:title" content="{{title}} | PANDA KINEMA">
  <meta property="og:type" content="website">
  <meta property="og:description" content="{{description}}">
  <meta name="twitter:card" content="summary_large_image">
{{ogp_meta}}
  <style>
    :root{--bg:#1b2228;--line:#3a464f;--text:#f4f4f0;--muted:#949494;--soft-text:#c9c9c5;
      --sans:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP","Noto Sans CJK JP",sans-serif;
      --cond:"DIN Condensed","Avenir Next Condensed","Arial Narrow","Helvetica Neue",var(--sans)}
    @supports not (text-box:trim-both cap alphabetic){ :root{--cond:"Avenir Next Condensed","DIN Condensed","Arial Narrow","Helvetica Neue",var(--sans)} }
    /* ===== 作品ごとの色(メインカラー・アクセントカラーから自動) ===== */
    .key{{{theme}}}

    *{box-sizing:border-box}
    html{scroll-behavior:smooth;scroll-padding-top:calc(76px + env(safe-area-inset-top,0px))}
    body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);-webkit-font-smoothing:antialiased;font-feature-settings:"palt";text-rendering:optimizeLegibility;overflow-x:clip}
    a{color:inherit;text-decoration:none}
    img{display:block;max-width:100%;height:auto}
    a:focus-visible,button:focus-visible{outline:2px solid currentColor;outline-offset:4px}
    .wrap{width:min(1100px,calc(100% - 40px));margin-inline:auto}

    /* ヘッダー:トップページと同じ形 */
    .site-header{position:sticky;top:0;z-index:40;padding-top:env(safe-area-inset-top,0px);background:#000;transition:background .3s ease}
    .site-header.scrolled{background:rgba(27,34,40,.62);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
    .site-header .bar{display:flex;align-items:center;gap:clamp(14px,2.6vw,34px);min-height:56px;padding-inline:max(16px,3vw)}
    .brand{flex:none;display:flex;align-items:center;height:28px}
    .brand img{height:30px;width:auto}
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
    /* 作品ページは、サイトの黒い下地の上に載った1枚のレイヤー。幅は --page-max まで、その外は下地の黒 */
    :root{--page-max:min(1440px,calc(clamp(600px,calc(100svh - 56px),1200px) * 1.4283))}   /* トップの絵(2001×1401)を画面の高さで見せたときの幅まで。その外は黒 */
    main.key{position:relative;max-width:var(--page-max);margin-inline:auto;overflow-x:clip}
    .pill{display:inline-block;margin:0;padding:.42em 1.15em .46em;border-radius:999px;font-weight:800;line-height:1.25;letter-spacing:.03em}
    .sec-h{margin-bottom:22px;background:var(--sec-bg);color:var(--sec-ink);font-size:clamp(17px,1.9vw,21px)}
    .pan-h{background:var(--pan-bg);color:var(--pan-ink);font-size:16px}
    /* 見出し:英字ラベル+ピル。左右の飾りだけ作品ごとに差し替え */
    .sec-head{display:flex;flex-direction:column;align-items:center;gap:10px;margin:0 0 24px;text-align:center}
    .en{margin:0;font-size:11px;font-weight:800;letter-spacing:.34em;opacity:.72}
    .sec-head .en{padding-left:.34em}
    .sec-row{display:flex;align-items:center;gap:16px}
    .sec-row::before,.sec-row::after{display:var(--orn-d,block);content:"";flex:none;width:26px;height:26px;background:var(--orn-c,currentColor);
      -webkit-mask:var(--orn) center/contain no-repeat;mask:var(--orn) center/contain no-repeat}
    .sec-head .sec-h{margin:0}
    .btn{display:inline-flex;align-items:center;gap:.6em;padding:13px 26px;border-radius:999px;background:var(--accent);color:var(--on-accent);font-size:14px;font-weight:800;letter-spacing:.04em;transition:translate .15s ease,box-shadow .15s ease}
    .btn:hover{translate:0 -2px;box-shadow:0 6px 16px rgba(0,0,0,.18)}
    .panel{background:#fff;color:var(--p-ink);border-radius:20px;padding:28px 30px}
    .panel .btn{background:var(--p-ink);color:#fff}
    /* BOOTHで購入:土台がメインカラー、文字がアクセントカラー。枠線はメインビジュアルの上のときだけ */
    .btn.buy,.panel .btn.buy,.fab.buy{background:var(--buy-bg,var(--accent));color:var(--buy-ink,var(--on-accent))}
    .hero .btn.buy{box-shadow:inset 0 0 0 2px var(--buy-ink,transparent)}
    .hero.ink-set .btn.buy{background:transparent;color:var(--hero-ink);box-shadow:inset 0 0 0 2px var(--hero-ink)}
    .spec{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 24px;margin:0}
    .spec div{display:flex;align-items:baseline;gap:7px}
    .spec dt{font-size:12px;opacity:.75}
    .spec dd{margin:0;font-size:17px;font-weight:800}

    /* ===== 1. メインビジュアル(パッケージの絵をそのまま大きく) ===== */
    .hero{position:relative;isolation:isolate;display:flex;flex-direction:column;min-height:clamp(600px,calc(100vh - 56px),1200px);min-height:clamp(600px,calc(100svh - 56px),1200px);overflow:hidden}
    .hero-art{position:absolute;inset:0;z-index:-1;will-change:transform}
    .hero-copy{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;padding:24px 20px 40px}
    .hero-main{margin-top:auto;display:flex;flex-direction:column;align-items:center;padding-top:24px}
    .hero h1{margin:0}
    .billing{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:14px 28px;margin-top:26px}
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      .hero h1{animation:rise .9s cubic-bezier(.2,.8,.2,1) .45s both}
      .billing{animation:rise .8s ease .8s both}
      @keyframes rise{from{opacity:0;translate:0 16px}}
    }
    /* メインビジュアル(編集画面の「メインビジュアル」):絵を全面に敷く/模様の上に部品を重ねる/閉じたカード */
    .hero .logo{position:relative;width:min(var(--lw,460px),86vw)}
    .hero.hero-cover .logo{width:min(calc(var(--lar,3) * clamp(130px,22vh,250px)),66vw,820px)}   /* トップ画像のときは画面の高さに合わせて大きく */
    .hero.hero-cover{color:var(--lt)}
    .hero.hero-cover .art{width:100%;height:100%;object-fit:cover;object-position:var(--art-pos,50% 50%);transform:scale(var(--zoom,1));transform-origin:var(--art-pos,50% 50%)}
    .hero.hero-cover{color:var(--hero-ink,var(--lt))}
    /* 全面に敷いた絵+部品:絵と同じ切り取り方の箱の中に部品を置く(どの画面でも絵とぴったり重なる) */
    .art-wrap{position:absolute;inset:0;container-type:size;overflow:hidden}
    .art-box{position:absolute;top:0;height:100cqh;width:calc(100cqh * var(--ar));left:calc((100cqw - 100cqh * var(--ar)) * var(--fx))}
    .art-fill{position:absolute;inset:0;background-repeat:repeat-x;background-size:auto 100cqh;background-position:calc((100cqw - 100cqh * var(--ar)) * var(--fx)) 0}
    .art-fill.edge{background:var(--edge-l) left top/50.5% 100% no-repeat,var(--edge-r) right top/50.5% 100% no-repeat}
    .hero.hero-cover .hero-art{will-change:auto}
    .art-box .art-bg{position:absolute;inset:0;width:100%;height:100%}
    .art-box .aly{position:absolute;left:var(--x);top:var(--y);width:var(--w);max-width:none;rotate:var(--r,0deg)}
    @media all{
      .aly.m-spin{animation:hfade .8s ease var(--dl) both,aspin var(--sp) linear infinite}
      .aly.m-spin-r{animation:hfade .8s ease var(--dl) both,aspin var(--sp) linear infinite reverse}
      @keyframes aspin{to{rotate:calc(var(--r,0deg) + 360deg)}}
    }
    .hero.hero-cover.light .hero-art::after{display:none}   /* 明るい絵はぼかさない */
    .hero.hero-cover .hero-art::after{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,color-mix(in srgb,var(--k-bg) 45%,transparent),transparent 16%,transparent 52%,color-mix(in srgb,var(--k-bg) 86%,transparent) 82%,var(--k-bg))}
    .hero.hero-stage{color:var(--hero-ink,var(--k-ink))}
    .hero.hero-stage .hero-art{background:var(--hero-bg,var(--k-bg)) var(--pat,none) center top/var(--pat-size,auto)}
    .hero.hero-stage .hero-main{margin-block:auto}
    .stage{position:relative;width:min(var(--sw,380px),58vw);margin:0 auto -5%}
    .stage .ly0{position:relative;display:block;width:100%}
    .stage:has(.ly){margin-top:clamp(36px,7vw,96px)}   /* 上にはみ出す部品の分 */
    .stage .ly{position:absolute;left:var(--x);top:var(--y);width:var(--w);rotate:var(--r,0deg)}
    .stage .card-face{border-radius:14px;box-shadow:0 26px 40px -18px rgba(0,0,0,.5)}
    /* 閉じたカードをフルサイズで:画面の高さいっぱい、左右は画像の端の色、下に人数・購入 */
    .hero.hero-full{background:var(--hero-bg);color:var(--hero-ink)}
    .hero.hero-full .hero-art{bottom:118px;display:flex;justify-content:center;
      background:var(--edge-l) left top/50.5% 100% no-repeat,var(--edge-r) right top/50.5% 100% no-repeat}
    .hero.hero-full .card-full{height:100%;width:auto;max-width:none;aspect-ratio:var(--card-ar)}
    .hero.hero-full .billing{margin-top:0}
    .hero.hero-full .hero-copy{padding-bottom:30px}
    @media all{ .hero.hero-full .card-full{animation:artin 2.2s cubic-bezier(.2,.7,.2,1) both} }
    @media (max-width:650px){ .hero.hero-full{min-height:calc(100vw * var(--card-ar-inv,1.41) + 190px)} .hero.hero-full .hero-art{bottom:190px} .hero.hero-full .card-full{width:100%;height:auto} }
    .stage:has(.card-face){width:min(var(--sw,300px),62vw);margin:0 auto}
    .sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生 */
      .hero.hero-cover .art{animation:artin 3s cubic-bezier(.2,.7,.2,1) both}
      @keyframes artin{from{opacity:0;scale:1.07}}
      .m-rise{animation:hrise .8s cubic-bezier(.3,1.5,.5,1) var(--dl,.1s) both}
      .m-pop{animation:hpop .55s cubic-bezier(.3,1.8,.5,1) var(--dl,.5s) both,hbob 2.8s ease-in-out var(--bd,1.2s) infinite alternate}
      .m-float{animation:hfade .6s ease var(--dl,.3s) both,hbob 2.8s ease-in-out var(--bd,1.2s) infinite alternate}
      .m-hop{animation:hrise .8s cubic-bezier(.3,1.5,.5,1) var(--dl,.1s) both,lhop2 3.6s cubic-bezier(.3,.6,.4,1) var(--bd,1.2s) infinite}
      .m-fade{animation:hfade .8s ease var(--dl,.2s) both}
      @keyframes hrise{from{opacity:0;translate:0 30px}}
      @keyframes hpop{from{opacity:0;scale:.3}}
      @keyframes hfade{from{opacity:0}}
      @keyframes hbob{to{translate:0 -10px}}
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
    .vdots button{display:flex;align-items:center;gap:8px;padding:6px 14px;border:0;border-radius:999px;background:transparent;color:var(--k-ink);font:inherit;font-size:13px;font-weight:700;opacity:.6;cursor:pointer}
    .vdots button::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
    .vdots button[aria-current="true"]{opacity:1;background:var(--sec-bg);color:var(--sec-ink)}   /* 見出しと同じツートン */
    @media all{  /* 端末の「動きを減らす」設定に関係なく再生(パララックスと模様の横流れだけは設定に従う) */
      .js .cinema .vposter img{filter:brightness(.35);transition:filter 1.2s ease .5s}
      .js .cinema.on .vposter img{filter:none}
    }

    /* ===== 帯:背景の色と帯・見出しの色を交互に ===== */
    .band{position:relative;padding:68px 0 72px}
    .band.tex{padding:86px 0 90px}
    .band>.wrap{position:relative;z-index:1}
    .band-c{z-index:2;background:var(--b2-bg);color:var(--b2-ink);--orn-c:currentColor;
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
    /* キャラの大きさが違っても名前の高さがそろうように、絵の枠の高さを固定して下にそろえる */
    .chara-slide .fig-wrap{height:var(--fh,230px);display:flex;align-items:flex-end;justify-content:center}
    .chara-slide .solo{width:auto;max-width:100%;max-height:100%}
    .chara-slide .tupa{flex:none}
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
    .chara-note{font-size:13.5px;line-height:1.8;font-weight:500;word-break:auto-phrase}
    .chara-name:empty{display:none}
    .chara-name{display:inline-block;padding:.32em 1.3em .36em;border-radius:999px;background:var(--b2-ink);color:var(--b2-bg);font-size:20px;font-weight:900;letter-spacing:.12em}
    .chara h2{margin:0 0 20px;font-size:clamp(24px,3.1vw,34px);font-weight:900;letter-spacing:.02em;line-height:1.35}
    .story>p:not(.en){margin:0;font-size:15.5px;line-height:2.05;max-width:34em;font-weight:500;word-break:auto-phrase}
    .story .en{margin-bottom:12px;padding-left:.34em}

    /* ===== 4. どんなゲーム?(目的の要約+図) ===== */
    .summary{margin:0 auto 26px;max-width:44em;font-size:16px;line-height:1.95;font-weight:500;text-align:center;word-break:auto-phrase}
    .summary em,.story em,.chara-note em{font-style:normal;font-weight:900;}
    .band-c{--hl-deco:var(--hl2-deco,none)}
    .summary em{font-style:normal;color:var(--hl)}
    .band-c em{font-style:normal;color:var(--hl2)}   /* 太字にしたところ(もう1色の帯の上) */
    /* 横に流れるカード(画面の端まで。左端は本文の幅にそろえる) */
    .flow{--gut:max(20px,calc((min(100vw,var(--page-max)) - 1100px) / 2));--card:320px;--gap:46px;margin-inline:calc(50% - min(50vw,var(--page-max) / 2))}
    .steps{list-style:none;margin:0;display:flex;gap:var(--gap);overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;scroll-padding-inline:var(--gut);
      padding:8px 20px 16px var(--gut);scrollbar-width:none;counter-reset:step;cursor:grab}
    .steps::-webkit-scrollbar{display:none}
    .steps.drag{cursor:grabbing;scroll-snap-type:none;user-select:none}
    .step{counter-increment:step;position:relative;flex:0 0 var(--card);scroll-snap-align:start;display:flex;flex-direction:column;gap:12px;padding:16px 16px 16px;border-radius:20px;background:#fff;color:var(--p-ink)}
    .step:not(:last-child)::after{content:"";position:absolute;left:calc(100% + (var(--gap) - 14px) / 2);top:calc(50% - 10px);border-style:solid;border-width:10px 0 10px 14px;border-color:transparent transparent transparent var(--k-ink)}
    .step-head{flex:1;display:flex;flex-direction:column;align-items:center;gap:10px}
    .snum{display:grid;place-items:center;width:48px;height:46px;padding-top:0;background:var(--p-ink);color:#fff;
      -webkit-mask:var(--snum) center/contain no-repeat;mask:var(--snum) center/contain no-repeat;border-radius:var(--snum-r,0);font:900 22px/1 Georgia,"Times New Roman",serif}
    .snum b{font:inherit;translate:var(--snum-x,0px) var(--snum-y,0px)}   /* 番号の位置(編集画面で微調整) */
    .step-lead{flex:1;display:grid;place-items:center;margin:0 4px;font-size:15px;line-height:1.7;font-weight:600;text-align:center;word-break:auto-phrase;text-wrap:pretty}
    .step-lead em{font-style:normal;font-weight:900;color:#d4242b}   /* 取説の赤字 */
    .viz{--card-w:66px;position:relative;display:flex;align-items:center;justify-content:center;height:206px;padding:12px;border-radius:14px;background:var(--soft);overflow:hidden}
    .ptabs{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:0 0 20px}
    .ptabs button{padding:8px 18px;border:2px solid var(--k-ink);border-radius:999px;background:transparent;color:var(--k-ink);font:inherit;font-size:14px;font-weight:800;cursor:pointer}
    .ptabs button[aria-selected="true"]{background:var(--sec-bg);border-color:var(--sec-bg);color:var(--sec-ink)}
    .steps[hidden]{display:none}
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
    .ltw{--cw:36px;--step:20px;position:relative;padding:6px 6px 6px 24px;border-radius:9px;background:#2b9fd9}
    .ltower{position:relative;width:var(--cw);height:calc(var(--cw) * 1.4 + (var(--n) - 1) * var(--step))}
    .lt{position:absolute;left:0;bottom:calc(var(--i) * var(--step));width:var(--cw);border-radius:4px;box-shadow:0 -2px 5px rgba(0,0,0,.2)}
    .lt.fall{opacity:.3}
    .ruler{position:absolute;left:0;bottom:6px;width:24px;margin:0;padding:0;list-style:none}
    .ruler li{position:absolute;left:0;right:0;bottom:calc(var(--i) * var(--step) + 1px);color:#fff;font:900 12px/20px Georgia,serif;text-align:center}
    .manual-link{display:flex;flex-direction:column;align-items:center;gap:12px;margin-top:30px;text-align:center}
    .manual-link p{margin:0;font-size:14px;font-weight:700;opacity:.85}
    /* フォトギャラリー */
    /* ギャラリー:1枚ずつ。◀▶・点・横スワイプで切り替え、押すと大きく */
    .gal{position:relative;max-width:920px;margin:0 auto}
    .gtrack{overflow:hidden;border-radius:18px;touch-action:pan-y}
    .grail{display:flex;transform:translate3d(calc(var(--gi,0) * -100% + var(--gdx,0px)),0,0);transition:transform .45s cubic-bezier(.2,.8,.2,1)}
    .grail.drag{transition:none}
    .gslide{flex:0 0 100%;margin:0;display:flex;flex-direction:column;align-items:center;gap:14px}
    .gitem{display:block;width:100%;height:min(62vh,560px);padding:18px;border:0;border-radius:18px;background:#fff;cursor:zoom-in}
    .gitem img{width:100%;height:100%;object-fit:contain}
    .gph{display:grid;place-items:center;width:100%;height:min(62vh,560px);border:2px dashed color-mix(in srgb,var(--b2-ink) 35%,transparent);border-radius:18px;font-size:14px;font-weight:700;opacity:.8}
    .gslide figcaption{font-size:14px;font-weight:800;text-align:center}
    .gnav{position:absolute;top:calc(min(62vh,560px) / 2);translate:0 -50%;display:grid;place-items:center;width:46px;height:46px;padding:0;border:0;border-radius:50%;background:var(--b2-ink);cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.2);transition:opacity .2s ease}
    .gnav::before{content:"";border-style:solid;border-color:transparent}
    .gnav.prev{left:-23px}.gnav.next{right:-23px}
    .gnav.prev::before{border-width:8px 12px 8px 0;border-right-color:var(--b2-bg);margin-right:3px}
    .gnav.next::before{border-width:8px 0 8px 12px;border-left-color:var(--b2-bg);margin-left:3px}
    .gnav[disabled]{opacity:0;pointer-events:none}
    .gnav:hover{scale:1.06}
    .gdots{display:flex;justify-content:center;gap:8px;margin-top:16px}
    .gdots button{width:9px;height:9px;padding:0;border:0;border-radius:50%;background:var(--b2-ink);opacity:.3;cursor:pointer}
    .gdots button[aria-current="true"]{opacity:1}
    .gal:not(:has(.gslide+.gslide))~.gdots,.gal:not(:has(.gslide+.gslide)) .gnav{display:none}
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

    /* 関連コンテンツ */
    .rel-row{justify-content:safe center;gap:18px}
    .rel-row .bg-card{height:260px;box-shadow:0 14px 26px -16px rgba(0,0,0,.45)}
    /* リンクのカード(OGPの画像+タイトル+サイト名) */
    .bg-link{display:flex;flex-direction:column;aspect-ratio:auto;width:300px;background:#fff;color:#1b2228;text-align:left}
    .bl-img{display:block;width:100%;aspect-ratio:1.91/1;object-fit:cover;background:#e9ecee}
    .bg-link>.bl-img{height:auto;flex:none}
    .bl-t{flex:1;display:flex;flex-direction:column;justify-content:space-between;gap:8px;padding:12px 14px 14px}
    .bl-t b{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden;font-size:14px;line-height:1.55}
    .bl-t small{font-size:11.5px;font-weight:700;opacity:.55}
    /* 関連コンテンツの作品・ツール:開いたカードの中身を、リンクのカードと同じ形に */
    .rel-row .bg-card,.rel-row .bg-link{height:auto;min-height:260px;aspect-ratio:auto}
    .rel-row li{display:flex}   /* 横に並ぶカードの高さをそろえる */
    .ro-vis{display:flex;align-items:center;justify-content:center;gap:6%;width:100%;aspect-ratio:1.91/1;padding:12px 16px;overflow:hidden}
    .ro-pkg{width:auto;height:88%;max-width:42%;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(0,0,0,.25))}
    .ro-logo{display:block;width:48%;max-height:70%;object-fit:contain;-webkit-mask:var(--lg) center/contain no-repeat;mask:var(--lg) center/contain no-repeat}
    img.ro-logo{-webkit-mask:none;mask:none}
    .ro-name{font-size:17px;font-weight:900;line-height:1.3}
    .ro-tool .ro-shot{width:44%;height:auto;max-height:86%;object-fit:contain;border-radius:4px;box-shadow:0 6px 12px rgba(0,0,0,.3)}
    .ro-tool .bt-tupa{width:22%;margin:0}
    .ro-intro{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;margin-top:-2px;font-size:12px;font-weight:600;line-height:1.6;opacity:.8}
    .rel-open .bl-t{justify-content:flex-start}
    .rel-open .bl-t small{margin-top:auto}

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
    .bg-card>img{width:100%;height:100%;object-fit:cover}
    .bg-tool{display:flex;flex-direction:column}
    .bg-tool .bt-shot{width:100%;aspect-ratio:1;object-fit:cover}
    .bt-tupa{position:relative;display:block;width:52%;aspect-ratio:1164/1562;margin:16% auto 4%}
    .bt-tupa .tb{position:absolute;left:0;bottom:0;width:100%}
    .bt-tupa .to{position:absolute;left:50%;top:0;width:30.4%;translate:-50% 0;filter:drop-shadow(0 0 6px rgba(27,185,238,.7))}
    .bt-name{display:flex;align-items:center;justify-content:center;flex:1;padding:8px 10px;font-size:13px;font-weight:900;line-height:1.35;text-align:center}
    .bt-title{width:100%;height:auto}
    .bg-new{position:absolute;left:50%;top:8px;translate:-50% 0;display:inline-flex;align-items:center;height:20px;padding:0 7px;border-radius:4px;background:#e8343d;color:#fff;font-size:11px;font-weight:800;letter-spacing:.08em;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.3)}
    .bg-new{height:24px;padding:0 10px;font-family:var(--cond);font-size:16px;font-weight:700;letter-spacing:.08em}
    .site-footer{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:56px;padding:22px 0 calc(28px + env(safe-area-inset-bottom,0px));background:radial-gradient(circle,rgba(205,210,212,.7) 1.6px,transparent 2px) 0 0/16px 4px repeat-x;font-size:12px;color:#cdd2d4}
    .site-footer a{font-family:var(--cond);font-size:14px;letter-spacing:.08em}

    /* ===== 追従するBOOTHボタン(メインビジュアルと購入欄が見えていない間だけ) ===== */
    .fab{position:fixed;right:max(18px,env(safe-area-inset-right,0px));bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:30;
      display:flex;align-items:center;gap:.5em;min-height:48px;padding:0 22px 0 70px;border:0;border-radius:999px;
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
      .js .step{opacity:0;translate:0 28px;transition:opacity .5s ease,translate .6s cubic-bezier(.2,.8,.2,1)}
      .js .step.on{opacity:1;translate:0 0}
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
      .brand img{height:26px}
      .site-nav{gap:12px;font-size:14px}
      html{scroll-padding-top:calc(66px + env(safe-area-inset-top,0px))}
      .hero{min-height:clamp(540px,calc(100svh - 56px),900px)}
      .hero.hero-cover .logo{width:min(calc(var(--lar,3) * 120px),88vw)}
      .hero-copy{padding:16px 14px 30px}
      .hero.hero-stage{min-height:0}
      .hero.hero-stage .hero-main{margin-block:36px 0}
      .billing{flex-direction:column;gap:14px;width:100%}
      .billing .btn{width:100%;justify-content:center}
      .screen-band{padding:14px 0}
      .cinema .vplayer{width:100%}
      .gitem,.gph{height:min(56vh,420px);padding:12px}
      .gnav{top:calc(min(56vh,420px) / 2);width:38px;height:38px}
      .gnav.prev{left:6px}.gnav.next{right:6px}
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
      .chara-slide .fig-wrap{--fh:180px}
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
      .buy-box{grid-template-columns:1fr;gap:22px;padding:24px 18px}
      .buy-box .pkg{width:min(160px,50%);margin-inline:auto}
      .buy-box .btn{display:flex;justify-content:center}
      .credits{padding-top:64px}
      .roll{gap:14px}
      .roll div{grid-template-columns:1fr;gap:2px}
      .roll dt,.roll dd{text-align:center}
      .bg-card{height:180px}
      .rel-row .bg-card{height:200px}
      .rel-row .bg-link{width:min(260px,72vw)}
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
  <section class="hero {{hero_cls}}" style="{{hero_style}}" aria-labelledby="title">
    {{hero_art}}
    <div class="hero-copy">
      <div class="hero-main">
        {{hero_visual}}
        <h1 id="title"{{h1_cls}}><img class="logo" src="{{img:{{logo}}}}" alt="{{logo_alt}}" width="{{logo_w}}" height="{{logo_h}}"></h1>
        <div class="billing">
          <dl class="spec">
{{spec_html}}
          </dl>
          <a class="btn buy" href="{{booth}}" target="_blank" rel="noopener">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
        </div>
      </div>
    </div>
  </section>

  <!-- 2. 動画:画面幅いっぱいの黒帯をスクリーンに(data-yt に YouTube の動画IDを入れると再生できる) -->
  <section class="cinema reveal-cinema{{video_tex}}" id="video" aria-labelledby="video-title"{{video_hidden}}{{st_video}}>
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
  <section class="band band-c chara" id="story" aria-labelledby="intro-title"{{st_story}}>
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
  <section class="band tex" id="rules" aria-labelledby="rules-title"{{st_rules}}>
    <div class="gband top" aria-hidden="true"></div><div class="gband bottom" aria-hidden="true"></div>
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">HOW TO PLAY</p><div class="sec-row"><h2 class="pill sec-h" id="rules-title">{{L:どんなゲーム?|What kind of game?}}</h2></div></header>
      <p class="summary">{{summary}}</p>
{{tabs_html}}
      <div class="flow reveal-flow">
{{steps_html}}
        <div class="flow-ui" hidden><button class="fnav prev" type="button" aria-label="前のカード">‹</button><div class="flow-bar" aria-hidden="true"><span></span></div><button class="fnav next" type="button" aria-label="次のカード">›</button></div>
      </div>
      <div class="manual-link reveal"><p>{{L:くわしいルールは遊び方説明書で|Full rules are in the rulebook}}</p><a class="btn" lang="ja" href="{{manual_ja}}" target="_blank" rel="noopener">遊び方説明書を読む <span aria-hidden="true">↗</span></a><a class="btn" lang="en" href="{{manual_en}}" target="_blank" rel="noopener">Read the rulebook <span aria-hidden="true">↗</span></a></div>
    </div>
  </section>

  <section class="band band-c" id="photo" aria-labelledby="photo-title"{{st_photo}}>
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">GALLERY</p><div class="sec-row"><h2 class="pill sec-h" id="photo-title">{{L:ギャラリー|Gallery}}</h2></div></header>
      <div class="gal reveal">
        <div class="gtrack" tabindex="0" aria-label="ギャラリー(横に切り替え)"><div class="grail">
{{gallery_html}}
        </div></div>
        <button class="gnav prev" type="button" aria-label="前の写真"></button><button class="gnav next" type="button" aria-label="次の写真"></button>
      </div>
      <div class="gdots">{{gdots_html}}</div>
    </div>
  </section>

  <section class="band tex buy" id="buy" aria-label="購入"{{st_buy}}>
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
        <a class="btn buy" href="{{booth}}" target="_blank" rel="noopener">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
      </div>
    </div>
    </div>
  </section>

  <!-- 関連コンテンツ(編集画面の「関連コンテンツ」で選んだものだけ。なければ出ない) -->
{{related_html}}
  <dialog class="lb" aria-label="写真"><img alt=""><button class="lb-x" type="button" aria-label="閉じる">×</button></dialog>

  <a class="fab buy" href="{{booth}}" target="_blank" rel="noopener"><img src="{{img:{{fab_pkg}}}}" alt="" width="44" height="67">{{L:BOOTHで購入|Buy on BOOTH}} <span aria-hidden="true">↗</span></a>
</main>

<!-- 5. クレジット -->
<section class="credits wrap reveal-credits" aria-label="クレジット">
  <img class="credits-logo" src="{{img:{{logo_credits}}}}" alt="{{logo_alt}}" loading="lazy">
  <dl class="roll">
{{credits_html}}
  </dl>
</section>

<!-- 6. CONTENTS:ほかのボードゲーム → ツール(トップと同じカード・少し小さめ) -->
<div class="wrap"><div class="dotline" aria-hidden="true"></div></div>
<section class="lineup-sec" id="lineup" aria-labelledby="lineup-title">
  <div class="wrap">
    <h2 class="lineup-h" id="lineup-title"><span class="cap">CONTENTS</span></h2>
    <ul class="bg-row">
{{lineup_html}}
    </ul>
  </div>
</section>

<div class="wrap"><footer class="site-footer"><span>©2015-2026 Panda Kinema</span><a href="#"><span class="cap">BACK TO TOP ↑</span></a></footer></div>

<script>
(function(){
  var shd=document.querySelector(".site-header"); function shs(){ shd.classList.toggle("scrolled",scrollY>4) } addEventListener("scroll",shs,{passive:true}); shs();
  var root=document.documentElement, motion=!window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var done=false; function lit(){ if(done) return; done=true; requestAnimationFrame(function(){ root.classList.add("lit") }) }
  var hero=[].slice.call(document.querySelectorAll(".hero img")), left=hero.filter(function(i){return !i.complete}).length;
  if(!left) lit(); else hero.forEach(function(i){ if(!i.complete){ i.addEventListener("load",function(){ if(--left<=0) lit() }); i.addEventListener("error",lit) } });
  setTimeout(lit,1500);

  /* スクロール:見えたら再生、画面の外に出たら戻す(戻ってきたらもう一度) */
  var els=[].slice.call(document.querySelectorAll(".reveal,.reveal-credits,.reveal-cinema,.reveal-chara,.reveal-flow"));
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){ var k=0; es.forEach(function(e){
      var t=e.target;
      if(e.isIntersecting && e.intersectionRatio>=.18){
        if(t.classList.contains("reveal-flow")){   /* 遊び方のカード:まとめて左から順に(横にスクロールしても揺れない) */
          [].forEach.call(t.querySelectorAll(".step"),function(c,i){ clearTimeout(c._t); c._t=setTimeout(function(){ c.classList.add("on") },i*180) });
        } else t.classList.add("on");
      } else if(!e.isIntersecting){ clearTimeout(t._t); t.classList.remove("on");
        if(t.classList.contains("reveal-flow")) [].forEach.call(t.querySelectorAll(".step"),function(c){ clearTimeout(c._t); c.classList.remove("on") }) }
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
  var flows=[].slice.call(document.querySelectorAll(".flow .steps")), flow=flows[0];
  if(flow){
    var ui=document.querySelector(".flow-ui"), fb=ui.querySelector(".flow-bar span"), fp=ui.querySelector(".prev"), fn=ui.querySelector(".next");
    function fsync(){ var max=flow.scrollWidth-flow.clientWidth; ui.hidden=max<4; if(max<4) return;
      fb.style.setProperty("--w",(flow.clientWidth/flow.scrollWidth*100)+"%"); fb.style.setProperty("--l",(flow.scrollLeft/flow.scrollWidth*100)+"%");
      fp.disabled=flow.scrollLeft<4; fn.disabled=flow.scrollLeft>max-4 }
    function step(){ var c=flow.querySelector(".step"); return c.offsetWidth+parseFloat(getComputedStyle(flow).columnGap||0) }
    fp.addEventListener("click",function(){ flow.scrollBy({left:-step(),behavior:"smooth"}) });
    fn.addEventListener("click",function(){ flow.scrollBy({left:step(),behavior:"smooth"}) });
    window.addEventListener("resize",fsync);
    var sx0=0, sl0=0, moved=false, down=false;
    flows.forEach(function(f){
      f.addEventListener("scroll",function(){ if(f===flow) requestAnimationFrame(fsync) },{passive:true});
      f.addEventListener("pointerdown",function(e){ if(e.pointerType!=="mouse"||e.button!==0) return; down=true; moved=false; sx0=e.clientX; sl0=flow.scrollLeft });
      f.addEventListener("click",function(e){ if(moved){ e.preventDefault(); e.stopPropagation(); moved=false } },true);
      f.addEventListener("dragstart",function(e){ e.preventDefault() });
    });
    window.addEventListener("pointermove",function(e){ if(!down) return; var dx=e.clientX-sx0; if(!moved&&Math.abs(dx)>5){ moved=true; flow.classList.add("drag") } if(moved) flow.scrollLeft=sl0-dx });
    window.addEventListener("pointerup",function(){ if(!down) return; down=false; if(moved){ var l=flow.scrollLeft; flow.classList.remove("drag"); flow.scrollLeft=l; flow.scrollBy({left:0}) } });
    /* 遊び方のタブ(イカタコの対戦・協力・ソロなど) */
    [].forEach.call(document.querySelectorAll(".ptabs button"),function(t,k,all){ t.addEventListener("click",function(){
      [].forEach.call(all,function(x,j){ x.setAttribute("aria-selected",j===k?"true":"false") });
      flows.forEach(function(f,j){ f.hidden=j!==k }); flow=flows[k]; flow.scrollLeft=0; fsync() }) });
    fsync();
  }

  /* ギャラリー:1枚ずつ切り替え(◀▶・点・スワイプ・矢印キー)。かならず1枚ぶんずつ止まる */
  var gt=document.querySelector(".gtrack");
  if(gt){
    var gr=gt.querySelector(".grail"), gs=[].slice.call(gr.children), gd=[].slice.call(document.querySelectorAll(".gdots button")), gp=document.querySelector(".gnav.prev"), gn=document.querySelector(".gnav.next"), gc=0;
    function ggo(i){ gc=Math.max(0,Math.min(gs.length-1,i)); gr.style.setProperty("--gi",gc); gr.style.setProperty("--gdx","0px");
      gd.forEach(function(d,k){ d.setAttribute("aria-current",k===gc?"true":"false") }); gp.disabled=gc<=0; gn.disabled=gc>=gs.length-1;
      gs.forEach(function(sl,k){ if(k===gc) sl.removeAttribute("aria-hidden"); else sl.setAttribute("aria-hidden","true") }) }
    gp.addEventListener("click",function(){ ggo(gc-1) }); gn.addEventListener("click",function(){ ggo(gc+1) });
    gd.forEach(function(d,k){ d.addEventListener("click",function(){ ggo(k) }) });
    gt.addEventListener("keydown",function(e){ if(e.key==="ArrowRight"){ e.preventDefault(); ggo(gc+1) } if(e.key==="ArrowLeft"){ e.preventDefault(); ggo(gc-1) } });
    var gx=null, gy=0, gdx=0, gmode=0, gmoved=false;
    gt.addEventListener("pointerdown",function(e){ if(e.pointerType==="mouse"&&e.button!==0) return; gx=e.clientX; gy=e.clientY; gdx=0; gmode=0; gmoved=false });
    window.addEventListener("pointermove",function(e){ if(gx===null) return; var dx=e.clientX-gx, dy=e.clientY-gy;
      if(!gmode){ if(Math.abs(dx)>8&&Math.abs(dx)>Math.abs(dy)){ gmode=1; gr.classList.add("drag") } else if(Math.abs(dy)>8){ gmode=2 } }
      if(gmode===1){ gdx=dx; if((gc===0&&dx>0)||(gc===gs.length-1&&dx<0)) gdx=dx/3; gr.style.setProperty("--gdx",gdx+"px"); gmoved=true } });
    function gend(){ if(gx===null) return; gx=null; gr.classList.remove("drag"); if(gmode===1){ var th=Math.min(80,gt.clientWidth*.18); ggo(gdx<-th?gc+1:(gdx>th?gc-1:gc)) } gmode=0 }
    window.addEventListener("pointerup",gend); window.addEventListener("pointercancel",gend);
    gt.addEventListener("click",function(e){ if(gmoved){ e.preventDefault(); e.stopPropagation(); gmoved=false } },true);
    gt.addEventListener("dragstart",function(e){ e.preventDefault() });
    /* トラックパッドの横スクロール:ひと区切りで1枚 */
    var gw=0, gwt=null;
    gt.addEventListener("wheel",function(e){ if(Math.abs(e.deltaX)<=Math.abs(e.deltaY)) return; e.preventDefault(); if(gwt) return; gw+=e.deltaX;
      if(Math.abs(gw)>30){ ggo(gc+(gw>0?1:-1)); gw=0; gwt=setTimeout(function(){ gwt=null },500) } },{passive:false});
    ggo(0);
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

def rich(t):
    """編集画面のリッチテキスト(Markdown)を HTML に。太字(**〜**)と [[〜]] が強調の色になる。改行・段落は <br>"""
    t = H.escape(str(t or '').replace('\r\n', '\n').strip(), quote=False)
    t = re.sub(r'\\\n|  +\n', '\n', t)                                   # Markdown の改行
    t = re.sub(r'\\([^\n])', lambda m: '\x00%d\x01' % ord(m.group(1)), t)   # \! などのエスケープ
    t = re.sub(r'\*\*(.+?)\*\*|__(.+?)__|\[\[(.+?)\]\]', lambda m: '<em>%s</em>' % (m.group(1) or m.group(2) or m.group(3)), t, flags=re.S)
    t = re.sub(r'\x00(\d+)\x01', lambda m: chr(int(m.group(1))), t)
    return re.sub(r'\n+', '<br>', t)
def rich_L(s):   # {{L:日本語|英語}} の両方を rich に
    s = str(s or '')
    m = re.fullmatch(r'\{\{L:(.*?)\|(.*)\}\}', s, flags=re.S)
    return L(rich(m.group(1)), rich(m.group(2))) if m else rich(s)
def hl(t):   # [[ ]] = 取説の赤字(強調)
    return re.sub(r'\[\[(.+?)\]\]', r'<em>\1</em>', t)

def yt(v):   # YouTube のURLでもIDでもOK
    v = str(v or '').strip()
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})', v)
    return m.group(1) if m else v

def tool_art(t):   # ツールの絵(トップの PLAY&TOOLS と同じもの)。画像はトップの画像の置き場から
    if t.get('thumb') or t.get('image'):
        return '<img class="bt-shot" src="../../img/%s" alt="" loading="lazy">' % imgname(t.get('thumb') or t.get('image'))
    if t['key'] == 'moji':
        return '<span class="bt-tupa"><img class="tb" src="../../img/b_tupa_body.webp" alt=""><img class="to" src="../../img/b_tupa_orb.webp" alt=""></span>'
    return ''
def tool_title(t):
    if t.get('title_image'):
        return '<img class="bt-title" src="../../img/%s" alt="%s" loading="lazy">' % (imgname(t['title_image']), H.escape(t['name']))
    return H.escape(t['name'])

def card_href(x):   # トップのカードのリンク先を、作品ページから見た場所に
    u = str(x.get('page') or '')
    if u.startswith('http'):
        return u
    if u.startswith('games/'):
        return '../' + u[len('games/'):]
    return u or '../../#board'

def game_card(x):   # トップと同じボードゲームのカード
    e = H.escape
    return '      <li><a class="bg-card" href="%s"%s><img src="../../img/%s" alt="%s" loading="lazy">%s</a></li>' % (
        card_href(x), ' target="_blank" rel="noopener"' if str(x.get('page') or '').startswith('http') else '', imgname(x['front']), e(x['name']),
        '<span class="bg-new"><span class="cap">NEW</span></span>' if x.get('new') else '')
def tool_card(t):   # トップと同じツールのカード(閉じたカードの画像があればそれ、なければ 絵+タイトル。背景=メインカラー、文字=アクセントカラー)
    e = H.escape
    new = '<span class="bg-new"><span class="cap">NEW</span></span>' if t.get('new') else ''
    c = {'main': t.get('main') or '#163f53', 'accent': t.get('accent') or '#ffffff', 'white': '#ffffff', 'black': '#000000'}
    sel = str(t.get('bg') or 'main')
    cbg = c.get(sel, c['main'])
    cfg = c['accent'] if sel == 'main' else (c['main'] if sel == 'accent' else max((c['main'], c['accent']), key=lambda x: contrast(x, cbg)))
    if t.get('front'):
        return '      <li><a class="bg-card" href="%s" target="_blank" rel="noopener"><img src="../../img/%s" alt="%s" loading="lazy">%s</a></li>' % (e(t['url']), imgname(t['front']), e(t['name']), new)
    return '      <li><a class="bg-card bg-tool" href="%s" target="_blank" rel="noopener" style="background:%s;color:%s">%s<span class="bt-name">%s</span>%s</a></li>' % (
        e(t['url']), e(cbg), e(cfg), tool_art(t), tool_title(t), new)
OGP_CACHE = None
def link_card(x):   # リンク(note の記事など):ページのOGPからタイトル・画像・サイト名を読んでカードに
    global OGP_CACHE
    import ogp
    if OGP_CACHE is None:
        OGP_CACHE = ogp.load_cache()
    e = H.escape
    url = str(x['url']).strip()
    info = ogp.get(url, OGP_CACHE) or {}
    title = str(x.get('title') or info.get('title') or url)
    pic = imgname(x['image']) if x.get('image') else ''
    if pic:
        src = '../../img/' + pic
    else:
        im = info.get('image') or ''
        src = ('../../img/' + im) if im.startswith('links/') else im
    site = info.get('site') or re.sub(r'^www\.', '', url.split('/')[2] if '//' in url else url)
    return '      <li><a class="bg-card bg-link" href="%s" target="_blank" rel="noopener">%s<span class="bl-t"><b>%s</b><small>%s ↗</small></span></a></li>' % (
        e(url), ('<img class="bl-img" src="%s" alt="" loading="lazy">' % e(src)) if src else '<span class="bl-img bl-none"></span>', e(title), e(site))

def card_colors(x):   # カードの(背景, 文字):「背景の色」がメインならアクセント、アクセントならメイン、白・黒なら読みやすい方
    c = {'main': x.get('main') or '#163f53', 'accent': x.get('accent') or '#ffffff', 'white': '#ffffff', 'black': '#000000'}
    sel = str(x.get('bg') or 'main')
    bg = c.get(sel, c['main'])
    fg = c['accent'] if sel == 'main' else (c['main'] if sel == 'accent' else max((c['main'], c['accent']), key=lambda v: contrast(v, bg)))
    return bg, fg, c

def open_card(x, tool=False):
    """関連コンテンツのカード:トップの「開いたカード」と同じ中身(色・パッケージ・ロゴ)を、noteなどのリンクのカードと同じ形で"""
    e = H.escape
    bg, fg, c = card_colors(x)
    logo = x.get('title_image') if tool else x.get('logo')
    lsel = str(x.get('logo_color') or ('original' if tool else 'accent'))
    lc = '' if lsel == 'original' else c.get(lsel, fg)
    if logo:
        from PIL import Image
        with Image.open(os.path.join(WEB, imgname(logo))) as im:
            lw, lh = im.size
        lg = ('<span class="ro-logo" role="img" aria-label="%s" style="--lg:url(../../img/%s);aspect-ratio:%d/%d;background:%s"></span>' % (e(x['name']), imgname(logo), lw, lh, lc)) if lc else \
             '<img class="ro-logo" src="../../img/%s" alt="%s">' % (imgname(logo), e(x['name']))
    else:
        lg = '<span class="ro-name">%s</span>' % e(x['name'])
    if tool:
        shot = x.get('image') or x.get('thumb')
        art = ('<img class="ro-shot" src="../../img/%s" alt="">' % imgname(shot)) if shot else tool_art(x)
        href, label, extra = x['url'], 'PLAY&amp;TOOLS ↗', ' target="_blank" rel="noopener"'
        intro = x.get('intro_ja') or ''
    else:
        art = '<img class="ro-pkg" src="../../img/%s" alt="">' % imgname(x['pkg'])
        href = card_href(x); label = 'BOARD GAME'
        extra = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        intro = x.get('intro_ja') or ''
    intro = L(e(str(intro)).replace('\n', ''), e(str(x.get('intro_en') or intro)).replace('\n', ' '))
    return ('      <li><a class="bg-card bg-link rel-open" href="%s"%s><span class="ro-vis%s" style="background:%s;color:%s">%s%s</span>'
            '<span class="bl-t"><b>%s</b><span class="ro-intro">%s</span><small>%s</small></span></a></li>') % (
        e(href), extra, ' ro-tool' if tool else '', e(bg), e(fg), art, lg, e(x['name']), intro, label)

def related_html(g, key):   # 関連コンテンツ:選んだ作品・ツールのカード。なければ何も出さない
    tools = {t['key']: t for t in g['tools']}
    cards = [open_card(tools[k], True) if k in tools else open_card(g['games'][k]) for k in g['related'] if k != key and (k in tools or k in g['games'])]
    cards += [link_card(x) for x in g['related_links']]
    if not cards:
        return ''
    return '''  <section class="band band-c related" id="related" aria-labelledby="related-title">
    <div class="wrap">
      <header class="sec-head reveal"><p class="en" aria-hidden="true">RELATED</p><div class="sec-row"><h2 class="pill sec-h" id="related-title">{{L:関連コンテンツ|Related}}</h2></div></header>
      <ul class="bg-row rel-row reveal">
%s
      </ul>
    </div>
  </section>''' % '\n'.join(cards)

def render(key):
    g = apply(key); e = H.escape
    br = lambda t: t.replace('\n', '<br>')
    groups = g.get('tabs') or [('', '', 0, len(g['steps']))]
    def li(n, st):
        return '''          <li class="step %s">
            <div class="step-head"><span class="snum" aria-label="ステップ%d"><b>%d</b></span><p class="step-lead"><span>%s</span></p></div>
            <div class="viz">%s</div>
          </li>''' % (st.get('cls', ''), n + 1, n + 1, rich_L(st['b']), st['v'])
    steps = '\n'.join('        <ol class="steps" tabindex="0" aria-label="遊び方の流れ(横にスクロール)"%s>\n%s\n        </ol>' % (
        '' if k == 0 else ' hidden', '\n'.join(li(n, st) for n, st in enumerate(g['steps'][a:b]))) for k, (_, _, a, b) in enumerate(groups))
    tabs_html = ''
    if g.get('tabs'):   # 遊び方が複数あるとき:タブで切り替え
        tabs_html = '      <div class="ptabs reveal" role="tablist">%s</div>' % ''.join(
            '<button type="button" role="tab" aria-selected="%s">%s</button>' % ('true' if k == 0 else 'false', lab) for k, (lab, _, _, _) in enumerate(groups))
    credits = '\n'.join('    <div style="--i:%d"><dt>%s</dt><dd>%s</dd></div>' % (i, e(a), e(b)) for i, (a, b) in enumerate(g['credits']))
    v = dict(
        header_logo=imgname(g['site'].get('header_logo') or 'brand.png'),
        title=e(g['title']), description=e(g['description']), theme=g['theme'], booth=e(g['booth']), seats=SEATS,
        hero_cls=g['hero_cls'], hero_art=g['hero_art'], hero_visual=g['hero_visual'], hero_css=g['hero_css'], hero_style=g['hero_style'], h1_cls=g['h1_cls'],
        logo=g['logo'], logo_w=g['logo_size'][0], logo_h=g['logo_size'][1], logo_alt=e(g['logo_alt']),
        logo_buy=g['logo_buy'], logo_credits=g['logo_credits'], poster=g['poster'],
        catch=br(e(g['catch'])), intro=rich_L(g['intro']), intro_img=g['intro_img'][0], intro_alt=e(g['intro_img'][1]), intro_cls=g['intro_img'][2],
        summary=rich_L(g['summary']),
        spec_html='\n'.join('            <div><dt>%s</dt><dd>%s</dd></div>' % (e(a), e(b)) for a, b in g['spec']),
        steps_html=steps, tabs_html=tabs_html, **{'st_' + k: g.get('sec_style', {}).get(k, '') for k in ('video', 'story', 'rules', 'photo', 'buy')}, manual_ja=e(g['manual_ja']), manual_en=e(g['manual_en']),
        gallery_html='\n'.join(['          <figure class="gslide"><button class="gitem" type="button" aria-label="%sを大きく見る"><img src="{{img:%s}}" alt="%s" loading="lazy"></button><figcaption>{{L:%s|%s}}</figcaption></figure>' % (e(t), f, e(t), e(t), e(te)) for f, t, te, c in g.get('gallery', [])]
                                + ['          <figure class="gslide"><div class="gph">{{L:%s(準備中)|%s (coming soon)}}</div></figure>' % (e(t), e(te)) for t, te in g.get('gallery_todo', [])]),
        gdots_html=''.join('<button type="button" aria-label="%d枚目"%s></button>' % (i + 1, ' aria-current="true"' if i == 0 else '') for i in range(len(g.get('gallery', [])) + len(g.get('gallery_todo', [])))),
        pkg=g['pkg'], pkg_w=g['pkg_size'][0], pkg_h=g['pkg_size'][1], contents=br(e(g['contents'])),
        price_html=('<p class="price">%s<small>{{L:BOOTH価格|on BOOTH}}</small></p>' % e(g['price'])) if g['price'] else '',
        credits_html=credits,
        chara_html=g.get('chara_html') or ('<div class="chara-slides"><div class="chara-slide cur"><div class="fig-wrap">%s</div><figcaption><span class="chara-name">%s</span><span class="chara-note">%s</span></figcaption></div></div>' % (g.get('chara_fig', ''), e(g.get('chara_name', '')), e(g.get('chara_note', '')).replace('\n', '<br>'))),
        piece_img=g.get('piece_img', ''), piece_alt=e(g.get('piece_alt', '')),
        chara_note=e(g.get('chara_note', '')).replace('\n', '<br>'),
        fab_pkg=g.get('fab_pkg', 'bibilu_pkg_sm.webp'),
        videos_html='\n'.join('          <figure class="vslide" data-yt="%s" data-title="%s"><button class="vposter" type="button"><img src="%s" alt="" loading="lazy"><span class="vplay" aria-hidden="true">▶</span><span class="vmeta">%s%s</span></button></figure>' % (
            e(yt(v.get('youtube'))), e(str(v.get('kind_ja') or '')), ('../../img/' + imgname(v['poster'])) if v.get('poster') else uri(g['poster']), LL(v, 'kind'), '' if v.get('youtube') else '<span class="vsoon">{{L:準備中|Coming soon}}</span>') for v in g['videos']),
        vdots_html=''.join('<button type="button"%s>%s</button>' % (' aria-current="true"' if i == 0 else '', LL(v, 'kind')) for i, v in enumerate(g['videos'])),
        lineup_html='\n'.join([game_card(x) for x in g['games'].values() if x['key'] != key] + [tool_card(t) for t in g['tools']]),
        related_html=related_html(g, key),
        video_hidden='' if g['videos'] else ' hidden',
        video_tex=' tex' if g.get('video_tex') else '',
        ogp_meta=('  <meta property="og:url" content="https://pandakinema.github.io/new/games/%s/">\n  <meta property="og:image" content="https://pandakinema.github.io/new/img/%s">' % (key, imgname(g['ogp_image']))) if g.get('ogp_image') else '',
    )
    s = TEMPLATE
    for _ in range(3):
        s = re.sub(r'\{\{(?!img:)(\w+)\}\}', lambda m: str(v[m.group(1)]), s)
    s = re.sub(r'\{\{L:(.*?)\|(.*?)\}\}', r'<span lang="ja">\1</span><span lang="en">\2</span>', s)
    s = re.sub(r'\{\{img:([\w.\-/]+)\}\}', lambda m: uri(m.group(1)), s)
    s = re.sub(r'\.\./\.\./img/([\w.\-/]+\.(?:png|webp|jpg|jpeg|gif|svg|mp4))', lambda m: '../../img/' + media.path(m.group(1)), s)   # 名前だけで書いた画像をフォルダの中の場所に
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)[:5]
    return s

if __name__ == '__main__':
    for key in GAMES:
        out = os.path.join(ROOT, 'new', 'games', key, 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from build import bust
        open(out, 'w', encoding='utf-8').write(bust(render(key), {'../../img/': TOP_IMG}))
        print(out, os.path.getsize(out))
    if OGP_CACHE is not None:
        import ogp
        ogp.save_cache(OGP_CACHE)
