"""art_pack.py - build the login-gated companion cartridge that carries a kit's figure images.

    python _build/art_pack.py <kit-id> [--root DIR] [--out DIR] [--spec PATH]

The kit's spec declares figures on pages, assignments and discussions (see cc.py). The
public cartridge renders each figure as a Canvas-native <img> that links to
course files/<folder>/<file> BY PATH and never contains the image. This script builds
the other half: a files-only .imscc holding exactly those images in a Files folder that is
hidden from the Files tab (the files themselves stay available: Canvas resolves a path link
only to an available file, so a hidden file would break every figure), that a teacher imports into the same course from a login-gated store (SharePoint).

Why two cartridges: the images are Artstor (Images on JSTOR) content. Paid access is
not a right to republish, and the kit store is a public GitHub Pages site. Canvas
course files are served only to enrolled users, which is inside the licence's
permitted use. So the images must reach Canvas without ever touching the public repo.

Output (never inside this repo):
    <out>/<kit>-art-pack.imscc        the cartridge
    <out>/<kit>-art-pack.json         manifest: every file, its source, bytes, rights statement found
    <out>/<kit>-art-pack.html         contact sheet for a human spot-check
--root  where figure `src` paths are read from; defaults to spec art_pack.root under OneDrive.
--out   defaults to OneDrive\\Claude's Workshop\\Art Packs.
Images are downscaled to 1200px on the long side (JPEG q86; PNG kept when it has alpha).
"""
import base64
import datetime
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cc  # noqa: E402
import kitlib as L  # noqa: E402

MAX_PX = 1200
RIGHTS_PATTERNS = (
    ('artstor-collection', re.compile(rb'Artstor Collection|about\.jstor\.org/terms', re.I)),
    ('commercial-agency', re.compile(rb'Scala|Art Resource|Bridgeman|Magnum Photos|Getty Images', re.I)),
    ('open-cc0', re.compile(rb'creativecommons\.org/publicdomain/zero|CC0', re.I)),
)


def onedrive_base():
    for k in ('OneDriveCommercial', 'OneDrive'):
        v = os.environ.get(k)
        if v and os.path.isdir(v):
            return v
    return os.path.join(os.path.expanduser('~'), 'OneDrive - OptimaEd')


def rights_of(data):
    head = data[:400000]
    found = []
    for cls, rx in RIGHTS_PATTERNS:
        m = rx.search(head)
        if m:
            found.append(cls)
    m = re.search(rb'Rights:\s*([^<\n\r]{10,300})', head)
    stmt = m.group(1).decode('utf-8', 'ignore').strip() if m else ''
    if not stmt:
        m = re.search(rb'<dc:rights>.*?<rdf:li[^>]*>([^<]{10,300})</rdf:li>', head, re.S)
        stmt = m.group(1).decode('utf-8', 'ignore').strip() if m else ''
    return (found[0] if found else 'none-found'), stmt


def downscale(data, want_ext):
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    im.load()
    w, h = im.size
    scale = min(1.0, MAX_PX / float(max(w, h)))
    if scale < 1.0:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    out = io.BytesIO()
    if want_ext == '.png' or has_alpha:
        if want_ext != '.png':
            raise ValueError('image has transparency; name the figure file .png')
        im.save(out, 'PNG', optimize=True)
    else:
        if im.mode != 'RGB':
            im = im.convert('RGB')
        im.save(out, 'JPEG', quality=86, optimize=True, progressive=True)
    return out.getvalue(), im.size


def thumb_b64(data):
    from PIL import Image
    im = Image.open(io.BytesIO(data)); im.load()
    im.thumbnail((240, 240))
    if im.mode != 'RGB':
        im = im.convert('RGB')
    o = io.BytesIO(); im.save(o, 'JPEG', quality=70)
    return base64.b64encode(o.getvalue()).decode('ascii')


def main():
    argv = sys.argv[1:]
    def opt(name):
        if name in argv:
            i = argv.index(name); v = argv[i + 1]; del argv[i:i + 2]; return v
        return None
    root_opt, out_opt, spec_opt = opt('--root'), opt('--out'), opt('--spec')
    if len(argv) != 1:
        print(__doc__); sys.exit(2)
    kit = argv[0]
    spec_path = spec_opt or L.spec_path_for(kit)
    spec = L.read_json(spec_path)
    cart = cc.Cartridge(spec)
    if cart.errors:
        sys.exit('spec errors:\n  ' + '\n  '.join(cart.errors))
    if not cart.figures:
        sys.exit('%s declares no figures; nothing to pack' % kit)
    root = root_opt or cart.art.get('root') or ''
    if root and not os.path.isabs(root):
        root = os.path.join(onedrive_base(), root)
    out_dir = out_opt or os.path.join(onedrive_base(), "Claude's Workshop", 'Art Packs')
    os.makedirs(out_dir, exist_ok=True)
    if os.path.abspath(out_dir).startswith(os.path.abspath(L.ROOT)):
        sys.exit('refusing to write the art pack inside the public store (%s)' % out_dir)

    files, manifest, missing, warns = [], [], [], []
    for name, f in sorted(cart.figures.items()):
        src = f.get('src') or name
        p = src if os.path.isabs(src) else os.path.join(root, src)
        if not os.path.exists(p):
            missing.append('%s -> %s' % (name, p)); continue
        raw = open(p, 'rb').read()
        cls, stmt = rights_of(raw)
        ext = os.path.splitext(name)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            missing.append('%s: figure file must end in .jpg or .png' % name); continue
        try:
            data, size = downscale(raw, '.png' if ext == '.png' else '.jpg')
        except Exception as e:
            missing.append('%s: %s' % (name, e)); continue
        if cls != 'artstor-collection':
            warns.append('%s: rights statement found = %s (%s)' % (name, cls, (stmt or 'none')[:90]))
        files.append({'path': f['path'], 'bytes': data, 'hidden_folder': True})
        manifest.append({'file': name, 'path': f['path'], 'src': os.path.relpath(p, root) if root and p.startswith(root) else p,
                         'source_bytes': len(raw), 'bytes': len(data), 'px': list(size),
                         'rights_class': cls, 'rights_statement': stmt, 'title': f.get('title'),
                         'artist': f.get('artist'), 'date': f.get('date'), 'thumb': thumb_b64(data)})
    if missing:
        sys.exit('art pack NOT built; %d figure source(s) unusable:\n  ' % len(missing) + '\n  '.join(missing))

    title = '%s - art pack (%s)' % (spec['course']['title'], kit)
    pack_spec = {'course': {'title': title, 'code': spec['course'].get('code'), 'files_only': True,
                            'version': 'art-pack ' + datetime.date.today().isoformat(),
                            'date': datetime.date.today().isoformat()},
                 'files': files}
    out = os.path.join(out_dir, '%s-art-pack.imscc' % kit)
    rep = cc.build(pack_spec, out)

    # verify the zip we just wrote
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        web = [n for n in names if n.startswith('web_resources/')]
        assert len(web) == len(files), (len(web), len(files))
        assert 'course_settings/files_meta.xml' in names, names
        assert 'imsmanifest.xml' in names
        assert not any(n.startswith('wiki_content/') for n in names)
        for fl in files:
            assert z.read('web_resources/' + fl['path']) == fl['bytes']
        fm = z.read('course_settings/files_meta.xml').decode('utf-8')
        folders = {f['path'].rsplit('/', 1)[0] for f in files}
        assert fm.count('<folder path=') == len(folders) and fm.count('<hidden>true</hidden>') == len(folders), fm[:400]
        assert '<file identifier=' not in fm, 'a hidden FILE breaks the path link the kit page uses'

    man = {'kit': kit, 'built': datetime.datetime.now().isoformat(timespec='seconds'), 'cartridge': os.path.basename(out),
           'bytes': rep['bytes'], 'folder': cart.art_folder, 'root': root, 'figures': len(files),
           'rights_classes': {c: sum(1 for m in manifest if m['rights_class'] == c) for c in {m['rights_class'] for m in manifest}},
           'warnings': warns, 'files': [{k: v for k, v in m.items() if k != 'thumb'} for m in manifest]}
    with open(os.path.join(out_dir, '%s-art-pack.json' % kit), 'w', encoding='utf-8') as fh:
        json.dump(man, fh, indent=1, ensure_ascii=False)

    # contact sheet
    uses = {}
    for coll in ('pages', 'assignments', 'discussions'):
        for o in spec.get(coll, []):
            for f in o.get('figures') or []:
                uses.setdefault(f.get('file'), []).append(o.get('title') or o.get('id'))
    cards = []
    for m in manifest:
        cards.append(
            '<div class="c"><img src="data:image/jpeg;base64,%s" alt=""><div class="t"><b><i>%s</i></b>%s%s<br><span class="s">%s &middot; %dx%d &middot; %s KB</span>'
            '<br><span class="s">%s</span><br><span class="u">%s</span></div></div>'
            % (m['thumb'], cc.x(m['title'] or ''), (', ' + cc.x(str(m['artist']))) if m['artist'] else '', (', ' + cc.x(str(m['date']))) if m['date'] else '',
               cc.x(m['file']), m['px'][0], m['px'][1], m['bytes'] // 1024, cc.x(m['rights_class'] + ': ' + (m['rights_statement'] or 'no statement found')[:110]),
               cc.x(' / '.join(uses.get(m['file'], [])))))
    html = ('<!doctype html><meta charset="utf-8"><title>%s</title><style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#0E1C42}'
            '.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}.c{border:1px solid #D0D9E8;border-radius:8px;padding:10px}'
            '.c img{width:100%%;height:180px;object-fit:contain;background:#f4f6fa}.t{font-size:13px;margin-top:6px}.s{color:#666;font-size:12px}.u{color:#2a6;font-size:12px}</style>'
            '<h1>%s</h1><p>%d images, %s. Not for distribution: this sheet exists so a person can check the pack before it goes to SharePoint.</p>%s<div class="g">%s</div>'
            % (cc.x(title), cc.x(title), len(files), L.human(rep['bytes']),
               ('<p style="color:#b00">%s</p>' % '<br>'.join(cc.x(w) for w in warns)) if warns else '', ''.join(cards)))
    with open(os.path.join(out_dir, '%s-art-pack.html' % kit), 'w', encoding='utf-8') as fh:
        fh.write(html)

    print(json.dumps({k: man[k] for k in ('kit', 'cartridge', 'bytes', 'folder', 'figures', 'rights_classes')}, indent=1))
    for w in warns:
        print('WARN', w)
    print('written to', out_dir)


if __name__ == '__main__':
    main()
