# 同じ名前の画像をアップし直したときの差し替え
# Pages CMS は同じ名前のファイルがあると「foo-1.png」のように番号を付けて保存します。
# これを見つけたら、元の「foo.png」をその中身で上書きして「foo-1.png」は消し、content/ の中の「foo-1.png」も「foo.png」に戻します。
# → 設定されている画像はそのままの名前で新しい絵に変わります。GitHub Actions がページを組み立てる前に動かします。
import os, re, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ['new/img', 'new/games/img']

def added_after(newer, older):   # newer が older より後に追加されたか(git の記録で判定。わからなければ True)
    def t(p):
        out = subprocess.run(['git', 'log', '-1', '--format=%ct', '--diff-filter=A', '--', p], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return int(out) if out else None
    a, b = t(newer), t(older)
    return a is None or b is None or a >= b

moved = []
for d in DIRS:
    for path in sorted(glob.glob(os.path.join(ROOT, d, '**', '*'), recursive=True)):
        m = re.match(r'^(.*)-(\d+)(\.[A-Za-z0-9]+)$', path)
        if not m or not os.path.isfile(path):
            continue
        base = m.group(1) + m.group(3)
        if not os.path.exists(base) or not added_after(os.path.relpath(path, ROOT), os.path.relpath(base, ROOT)):
            continue
        os.replace(path, base)
        moved.append((os.path.basename(path), os.path.basename(base)))
        print('差し替え:', os.path.relpath(base, ROOT), '←', os.path.basename(path))

if moved:   # content/ の中の参照も元の名前に
    for y in glob.glob(os.path.join(ROOT, 'content', '**', '*.yml'), recursive=True):
        s = open(y, encoding='utf-8').read(); s2 = s
        for new, old in moved:
            s2 = re.sub(r'(?<![\w.\-])' + re.escape(new) + r'(?![\w.\-])', old, s2)
        if s2 != s:
            open(y, 'w', encoding='utf-8').write(s2)
            print('参照を戻した:', os.path.relpath(y, ROOT))
