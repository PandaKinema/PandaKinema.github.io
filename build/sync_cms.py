# 編集画面(.pages.yml)の「一覧から選ぶ」欄の選択肢を、今のデータからつくり直す
# 「# AUTO:works」などの印が付いた行の values を書きかえます。GitHub Actions が保存のたびに動かします
import os, re, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    with open(os.path.join(ROOT, 'content', n + '.yml'), encoding='utf-8') as f:
        return yaml.safe_load(f) or []
def q(v):
    return '"%s"' % str(v).replace('\\', '\\\\').replace('"', '\\"')
games, tools = load('games'), load('tools')
sets = {
    'games': [(g['key'], g['name']) for g in games],
    'works': [(g['key'], g['name']) for g in games] + [(t['key'], t['name']) for t in tools],
    'categories': [(c['name'], c['name']) for c in load('categories') if c.get('name')],
    'roles': [(r['name'], r['name']) for r in load('roles') if r.get('name')],
}
p = os.path.join(ROOT, '.pages.yml')
s = open(p, encoding='utf-8').read()
def fill(m):
    line, name = m.group(0), m.group(1)
    vals = ', '.join('{ value: %s, label: %s }' % (q(v), q(l)) for v, l in sets[name])
    return re.sub(r'values: \[[^\]]*\]', 'values: [ %s ]' % vals, line, count=1)
s2 = re.sub(r'^.*# AUTO:(\w+)\s*$', fill, s, flags=re.M)
if s2 != s:
    open(p, 'w', encoding='utf-8').write(s2)
    print('.pages.yml を更新しました')
else:
    print('変更なし')
