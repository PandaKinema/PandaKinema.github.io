# 同じ名前の画像をアップし直したときの差し替え(GitHub Actions がページを組み立てる前に動かします)
# ・同じフォルダに同じ名前でアップすると、Pages CMS は「foo-1.png」のように番号を付けて保存します
# ・別のフォルダ(たとえば画像のいちばん上)に同じ名前でアップすると、別のファイルになります
# どちらの場合も、元の「trico/foo.png」を新しい中身で上書きし、新しく増えたファイルは消して、
# content/ の中の参照も元の場所に戻します → 設定されている画像が、そのままの名前で新しい絵に変わります
import os, re, subprocess
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
SKIP = ('unused/', 'links/')

def added(rel):   # git に追加された時刻(まだ記録がなければ今)
    out = subprocess.run(['git', 'log', '-1', '--format=%ct', '--diff-filter=AR', '--', 'img/' + rel],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return int(out) if out else 10 ** 12

groups = defaultdict(list)   # 「foo.png」ごとに、同じ名前(番号付きも含む)のファイルを集める
for d, _, fs in os.walk(IMG):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), IMG).replace(os.sep, '/')
        if rel.startswith(SKIP):
            continue
        m = re.match(r'^(.*)-(\d+)(\.[A-Za-z0-9]+)$', f)
        base = m.group(1) + m.group(3) if m else f
        groups[base].append(rel)

moved = []   # (消したファイル, 残した場所)
for base, rels in groups.items():
    if len(rels) < 2:
        continue
    plain = [r for r in rels if os.path.basename(r) == base]
    if not plain:
        continue
    keep = min(plain, key=added)              # いちばん古くからある場所を残す
    newest = max(rels, key=added)             # いちばん新しくアップしたものの中身を使う
    if newest != keep:
        os.replace(os.path.join(IMG, newest), os.path.join(IMG, keep))
        print('差し替え: img/%s ← %s' % (keep, newest))
    for r in rels:
        if r != keep and os.path.exists(os.path.join(IMG, r)):
            os.remove(os.path.join(IMG, r))
        if r != keep:
            moved.append((r, keep))

if moved:   # content/ の中の参照も残した場所に
    for d, _, fs in os.walk(os.path.join(ROOT, 'content')):
        for f in fs:
            if not f.endswith('.yml'):
                continue
            y = os.path.join(d, f)
            s = open(y, encoding='utf-8').read(); s2 = s
            for old, keep in moved:
                s2 = re.sub(r'(?<![\w.\-/])img/' + re.escape(old) + r'(?![\w.\-])', 'img/' + keep, s2)
            if s2 != s:
                open(y, 'w', encoding='utf-8').write(s2)
                print('参照を戻した:', os.path.relpath(y, ROOT))
