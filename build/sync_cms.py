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

# 作品ページ:content/pages/<key>.yml ごとに1つずつ(欄は最初のページと同じ)
def pages_block(s):
    a = s.index('      - name: page_')
    b = s.index('\n  - name: tools')
    items = s[a:b]
    m = re.search(r'        fields:[^\n]*\n(.*?)(?=\n      - name: page_|\Z)', items, flags=re.S)
    fields = m.group(1).rstrip('\n')
    names = {g['key']: g['name'] for g in games}
    keys = sorted((f[:-4] for f in os.listdir(os.path.join(ROOT, 'content', 'pages')) if f.endswith('.yml')),
                  key=lambda k: list(names).index(k) if k in names else 99)
    out = []
    for k in keys:
        fk = fields
        out.append('      - name: page_%s\n        label: %s\n        type: file\n        path: content/pages/%s.yml\n        format: yaml\n        fields:\n%s\n' % (k, q(names.get(k, k)), k, fk))
    return s[:a] + ''.join(out) + s[b:]
s0 = s
s = pages_block(s)
def fill(m):
    line, name = m.group(0), m.group(1)
    vals = ', '.join('{ value: %s, label: %s }' % (q(v), q(l)) for v, l in sets[name])
    return re.sub(r'values: \[[^\]]*\]', 'values: [ %s ]' % vals, line, count=1)
s2 = re.sub(r'^.*# AUTO:(\w+)\s*$', fill, s, flags=re.M)
if s2 != s0:
    open(p, 'w', encoding='utf-8').write(s2)
    print('.pages.yml を更新しました')
else:
    print('変更なし')
