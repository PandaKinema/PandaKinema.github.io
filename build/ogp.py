# 関連コンテンツの「リンク」(note の記事など)を、ページのOGP(タイトル・画像・サイト名)からカードにする
# 一度読んだものは build/ogp_cache.json に覚えておき、画像は new/img/links/ に保存します(GitHub Actions が保存)
import hashlib, html as H, json, os, re, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'build', 'ogp_cache.json')
IMG = os.path.join(ROOT, 'new', 'img', 'links')
UA = 'Mozilla/5.0 (compatible; PandaKinemaBot/1.0; +https://pandakinema.github.io/)'

def _get(url, limit=3_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ja,en;q=0.8'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read(limit), r.headers.get_content_charset() or 'utf-8', r.geturl()

def parse(page, base):
    """HTML から og:title / og:image / og:site_name を取り出す"""
    meta = {}
    for tag in re.findall(r'<meta\b[^>]*>', page, flags=re.I):
        a = dict((k.lower(), H.unescape(v2 or v1)) for k, v1, v2 in re.findall(r'([\w:-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', tag))
        a = {k: (v if v else '') for k, v in a.items()}
        key = (a.get('property') or a.get('name') or '').lower()
        if key and 'content' in a and key not in meta:
            meta[key] = a['content'].strip()
    title = meta.get('og:title') or meta.get('twitter:title')
    if not title:
        m = re.search(r'<title[^>]*>(.*?)</title>', page, flags=re.S | re.I)
        title = H.unescape(m.group(1)).strip() if m else ''
    image = meta.get('og:image') or meta.get('twitter:image') or ''
    if image:
        image = urllib.parse.urljoin(base, image)
    site = meta.get('og:site_name') or urllib.parse.urlparse(base).netloc
    return {'title': re.sub(r'\s+', ' ', title), 'image': image, 'site': site}

def load_cache():
    try:
        return json.load(open(CACHE, encoding='utf-8'))
    except (OSError, ValueError):
        return {}

def get(url, cache):
    """url のカード情報 {title, image(保存した画像の名前 or URL), site}。読めなければ None"""
    if url in cache:
        return cache[url]
    try:
        body, cs, final = _get(url)
        info = parse(body.decode(cs, 'replace'), final)
    except Exception as ex:   # 読めなかったときは次の組み立てでもう一度
        print('OGPを読めませんでした:', url, ex)
        return None
    if info['image']:
        try:
            data, _, _ = _get(info['image'], 8_000_000)
            ext = os.path.splitext(urllib.parse.urlparse(info['image']).path)[1].lower()
            ext = ext if ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif') else '.jpg'
            name = 'links/' + hashlib.md5(url.encode()).hexdigest()[:12] + ext
            os.makedirs(IMG, exist_ok=True)
            open(os.path.join(IMG, os.path.basename(name)), 'wb').write(data)
            info['image'] = name
        except Exception as ex:
            print('OGPの画像を保存できませんでした:', info['image'], ex)
    cache[url] = info
    return info

def save_cache(cache):
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
