# 画像の置き場(new/img)。作品ごとのフォルダに分けてあります
#   site/ … サイト全体(ヘッダーのロゴなど)   bibilu/ trico/ … 作品ごと(parts/ は遊び方の図の部品)
#   tools/ … ツール   links/ … 関連リンクのカード画像(自動)   unused/ … 今は使っていない画像
# 画像の欄の値は「img/trico/foo.png」の形。名前だけ(foo.png)でも、どのフォルダにあっても見つけます
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'new', 'img')
_index = None

def index():
    global _index
    if _index is None:
        _index = {}
        for d, _, fs in os.walk(IMG):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), IMG).replace(os.sep, '/')
                if not rel.startswith('unused/') or f not in _index:
                    _index.setdefault(f, rel)
    return _index

def path(v):
    """画像の欄の値(img/trico/foo.png、/new/img/foo.png、foo.png など)を new/img からの場所に"""
    v = str(v or '').strip().lstrip('/').split('?')[0]
    for pre in ('new/games/img/', 'new/img/', 'games/img/', 'img/'):
        if v.startswith(pre):
            v = v[len(pre):]
            break
    if not v or os.path.isfile(os.path.join(IMG, v)):
        return v
    b = os.path.basename(v)
    if b not in index():   # 「foo-1.png」(同じ名前で上げ直した画像)が元の「foo.png」にまとめられたあとでも見つける
        m = re.match(r'^(.*)-\d+(\.[A-Za-z0-9]+)$', b)
        if m and (m.group(1) + m.group(2)) in index():
            b = m.group(1) + m.group(2)
    return index().get(b, v)

def full(v):
    return os.path.join(IMG, path(v))
