"""kit.py - the one command a course builder runs.

    python _build/kit.py <kit-id>            build (or rebuild) one kit from courses/<code>/<kit>.spec.json
    python _build/kit.py --all               build every kit whose spec (or bundled files) changed
    python _build/kit.py <kit-id> --force    rebuild even if nothing changed

For each kit: hash the spec + its bundled files; skip if the sidecar already carries
that hash (a rebuilt cartridge is a new binary blob in git history, so we only
commit one when the content actually changed); otherwise build_kit.py -> cartridge
+ sidecar, verified. Then make_catalog.py and check_repo.py run over the whole repo.
Exit 1 if anything fails. Nothing here touches Canvas.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as L  # noqa: E402

PY = sys.executable


def label_for(kit_id):
    code = L.KIT_ID.match(kit_id).group('code')
    for d, c in L.load_courses(include_fixtures=True):
        if str(c.get('code')) == code:
            for k in c.get('kits', []):
                if k.get('id') == kit_id:
                    return k.get('label') or kit_id
            raise SystemExit('courses/%s/course.json does not list kit %s; add it to "kits" first' % (code, kit_id))
    raise SystemExit('no courses/%s/course.json for kit %s' % (code, kit_id))


def build_one(kit_id, force=False, root=None):
    spec = L.spec_path_for(kit_id)
    sha = L.spec_sha(spec)
    side = L.sidecar_path(kit_id) if root is None else os.path.join(root, 'cartridges', kit_id + '.json')
    if not force and os.path.exists(side):
        prev = L.read_json(side)
        if prev.get('spec_sha') == sha and os.path.exists(L.cartridge_path(kit_id) if root is None else os.path.join(root, 'cartridges', kit_id + '.imscc')):
            print('%s: unchanged (spec_sha %s), skipping' % (kit_id, sha[:12]))
            return False
    cmd = [PY, os.path.join(L.HERE, 'build_kit.py'), spec, kit_id, '--label', label_for(kit_id), '--spec-sha', sha]
    if root:
        cmd += ['--root', root]
    print('>', kit_id, 'building from', os.path.relpath(spec, L.ROOT))
    r = subprocess.run(cmd, cwd=L.ROOT)
    if r.returncode:
        raise SystemExit('%s: build failed' % kit_id)
    return True


def all_kits():
    out = []
    for d, c in L.load_courses():
        for k in c.get('kits', []):
            if os.path.exists(os.path.join(d, k['id'] + '.spec.json')):
                out.append(k['id'])
    return out


def main():
    argv = [a for a in sys.argv[1:]]
    force = '--force' in argv
    argv = [a for a in argv if a != '--force']
    if not argv:
        print(__doc__); sys.exit(2)
    kits = all_kits() if argv == ['--all'] else argv
    built = [k for k in kits if build_one(k, force)]
    print('built %d of %d kit(s)' % (len(built), len(kits)))
    for step in ('make_catalog.py', 'check_repo.py'):
        r = subprocess.run([PY, os.path.join(L.HERE, step)], cwd=L.ROOT)
        if r.returncode:
            sys.exit(r.returncode)
    if built:
        print('\nNext: stage ONLY your paths, e.g.')
        code = L.KIT_ID.match(built[0]).group('code')
        print('  git add courses/%s cartridges/%s.imscc cartridges/%s.json catalog.json .github/CODEOWNERS' % (code, built[0], built[0]))


if __name__ == '__main__':
    main()
