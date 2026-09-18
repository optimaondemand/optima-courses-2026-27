"""check_repo.py - the repo gate. Run before every commit; the PR workflow runs the same thing.

Rules are an independently evaluated table (no if/continue chain), each printed as
PASS / WARN / FAIL with its evidence. Exit 1 on any FAIL.

  registry    every courses/<code>/ has a valid course.json; code == folder; kit ids well-formed and unique
  specs       every <kit>.spec.json parses, has unique ids, resolvable links, relative file sources that exist
  voice       "facilitator" in student-facing HTML is a WARN with a count (program rule: say teacher)
  cartridges  every sidecar has its cartridge and vice versa; sizes match; spec_sha current; size limits
  catalog     catalog.json and .github/CODEOWNERS are what make_catalog.py would write now
  fixture     courses/_example builds and verifies into a temp folder (proves the toolchain, no real content)
  payload     total served bytes vs the GitHub Pages 1 GB ceiling
  licensed    no cartridge or bundled file carries a licensed (Artstor / agency) image: figures link by
              path and the images travel in the login-gated art pack (art_pack.py), never in this public repo

usage: check_repo.py [--no-fixture]
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as L  # noqa: E402
import cc  # noqa: E402

PY = sys.executable
FACILITATOR = re.compile(r'facilitator', re.I)
WEEKDAY = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday)\b')
results = []


def rule(name, ok, msg, warn=False):
    tag = 'PASS' if ok else ('WARN' if warn else 'FAIL')
    results.append((tag, name, msg))
    print('%s  %-11s %s' % (tag, name, msg))


def html_of(spec):
    parts = [p.get('html', '') for p in spec.get('pages', [])]
    parts += [a.get('html', '') for a in spec.get('assignments', [])]
    parts += [d.get('html', '') for d in spec.get('discussions', [])]
    for q in spec.get('quizzes', []):
        parts.append(q.get('description', ''))
        for qq in q.get('questions', []) or []:
            parts.append(qq.get('text', ''))
            parts += [a.get('text', '') for a in qq.get('answers', []) or []]
    parts.append(spec.get('syllabus_html', ''))
    return '\n'.join(parts)


def check_registry():
    ids, codes, problems = {}, set(), []
    courses = []
    try:
        courses = L.load_courses()
    except SystemExit as e:
        problems.append(str(e))
    for d, c in courses:
        folder = os.path.basename(d)
        code = str(c.get('code', ''))
        if code != folder:
            problems.append('courses/%s: code %r != folder' % (folder, code))
        if not L.CPALMS.match(code):
            problems.append('courses/%s: code is not a 7-digit CPALMS code (allowed, but confirm it is intentional)' % folder)
        if code in codes:
            problems.append('duplicate code %s' % code)
        codes.add(code)
        for k in ('title', 'grade', 'subject', 'kits'):
            if k not in c:
                problems.append('courses/%s/course.json missing %r' % (folder, k))
        for k in c.get('kits', []):
            kid = k.get('id', '')
            if not L.KIT_ID.match(kid) or not kid.startswith(code + '-'):
                problems.append('courses/%s: bad kit id %r' % (folder, kid))
            if kid in ids:
                problems.append('kit id %s appears in courses/%s and courses/%s' % (kid, ids[kid], folder))
            ids[kid] = folder
        for p in os.listdir(d):
            if p.endswith('.spec.json') and p[:-10] not in {k.get('id') for k in c.get('kits', [])}:
                problems.append('courses/%s/%s is not listed in course.json "kits"' % (folder, p))
    hard = [p for p in problems if 'not a 7-digit' not in p]
    soft = [p for p in problems if 'not a 7-digit' in p]
    rule('registry', not hard, '%d courses, %d kits registered%s' % (len(courses), len(ids), ('; ' + '; '.join(hard)) if hard else ''))
    if soft:
        rule('registry', False, '; '.join(soft), warn=True)
    return courses


def check_specs(courses):
    n, problems, fac, weekdays = 0, [], [], []
    for d, c in courses:
        folder = os.path.basename(d)
        for k in c.get('kits', []):
            sp = os.path.join(d, k['id'] + '.spec.json')
            if not os.path.exists(sp):
                continue
            n += 1
            try:
                spec = L.read_json(sp)
            except Exception as e:
                problems.append('%s: %s' % (k['id'], e)); continue
            if str(spec.get('course', {}).get('code')) != str(c.get('code')):
                problems.append('%s: spec course.code %r != %s' % (k['id'], spec.get('course', {}).get('code'), c.get('code')))
            for f in spec.get('files', []):
                src = f.get('src') or ''
                if os.path.isabs(src) or src.startswith('..') or '\\' in src:
                    problems.append('%s: file src must be a relative forward-slash path inside courses/%s/: %r' % (k['id'], folder, src))
                elif not os.path.exists(os.path.join(d, src)):
                    problems.append('%s: bundled file missing: courses/%s/%s' % (k['id'], folder, src))
            try:
                cart = cc.Cartridge(spec)
                # resolve links in every html body without writing anything
                for p in spec.get('pages', []):
                    cart.links(p.get('html', ''), 'page %s' % p['id'])
                for a in spec.get('assignments', []):
                    cart.links(a.get('html', ''), 'assignment %s' % a['id'])
                for dd in spec.get('discussions', []):
                    cart.links(dd.get('html', ''), 'discussion %s' % dd['id'])
                for q in spec.get('quizzes', []):
                    cart.links(q.get('description', ''), 'quiz %s' % q['id'])
                for m in spec.get('modules', []):
                    for it in m.get('items', []):
                        t, ref = it.get('type'), it.get('ref')
                        coll = {'page': cart.pages, 'assignment': cart.assignments, 'quiz': cart.quizzes,
                                'discussion': cart.discussions, 'file': cart.files}.get(t)
                        if coll is not None and ref not in coll:
                            cart.errors.append('module %s item references unknown %s %r' % (m['id'], t, ref))
                        if t not in ('page', 'assignment', 'quiz', 'discussion', 'file', 'url', 'header'):
                            cart.errors.append('module %s item has unknown type %r' % (m['id'], t))
                fronts = [p for p in spec.get('pages', []) if p.get('front_page')]
                if not fronts:
                    cart.warnings.append('no front_page page (build_kit adds a placeholder Course Home)')
                problems += ['%s: %s' % (k['id'], e) for e in cart.errors]
            except Exception as e:
                problems.append('%s: spec did not load into cc.Cartridge: %s' % (k['id'], e))
                continue
            body = html_of(spec)
            hits = len(FACILITATOR.findall(body))
            if hits:
                fac.append('%s (%d)' % (k['id'], hits))
            wd = len(WEEKDAY.findall(body))
            if wd:
                weekdays.append('%s (%d)' % (k['id'], wd))
    rule('specs', not problems, '%d spec(s) load, link and resolve%s' % (n, ('; ' + '; '.join(problems[:12]) + (' ...' if len(problems) > 12 else '')) if problems else ''))
    rule('voice', not fac, 'no "facilitator" in student text' if not fac else '"facilitator" in student text: ' + ', '.join(fac), warn=True)
    rule('voice', not weekdays, 'no weekday names in student text' if not weekdays else 'weekday names in student text (weeks, not weekdays): ' + ', '.join(weekdays), warn=True)


def check_cartridges(courses):
    specs = {}
    for d, c in courses:
        for k in c.get('kits', []):
            sp = os.path.join(d, k['id'] + '.spec.json')
            if os.path.exists(sp):
                specs[k['id']] = sp
    problems, warns, total = [], [], 0
    sidecars = {os.path.basename(p)[:-5] for p in os.listdir(L.CARTRIDGES) if p.endswith('.json') and not p.startswith('_')} if os.path.isdir(L.CARTRIDGES) else set()
    zips = {os.path.basename(p)[:-6] for p in os.listdir(L.CARTRIDGES) if p.endswith('.imscc') and not p.startswith('_')} if os.path.isdir(L.CARTRIDGES) else set()
    for kid in sorted(sidecars | zips):
        if kid not in sidecars:
            problems.append('%s.imscc has no sidecar' % kid); continue
        if kid not in zips:
            problems.append('%s.json has no cartridge' % kid); continue
        side = L.read_json(L.sidecar_path(kid))
        size = os.path.getsize(L.cartridge_path(kid)); total += size
        if side.get('bytes') != size:
            problems.append('%s: sidecar bytes %s != cartridge %s' % (kid, side.get('bytes'), size))
        if kid not in specs:
            problems.append('%s: built cartridge has no spec in courses/ (orphan)' % kid)
        elif side.get('spec_sha') != L.spec_sha(specs[kid]):
            problems.append('%s: cartridge is STALE (spec or a bundled file changed); run python _build/kit.py %s' % (kid, kid))
        if size > L.CARTRIDGE_FAIL_BYTES:
            problems.append('%s is %s (limit %s): move heavy media to the lesson repo on GitHub Pages' % (kid, L.human(size), L.human(L.CARTRIDGE_FAIL_BYTES)))
        elif size > L.CARTRIDGE_WARN_BYTES:
            warns.append('%s is %s' % (kid, L.human(size)))
        try:
            with zipfile.ZipFile(L.cartridge_path(kid)) as z:
                if 'imsmanifest.xml' not in z.namelist():
                    problems.append('%s: no imsmanifest.xml' % kid)
        except zipfile.BadZipFile:
            problems.append('%s: not a zip' % kid)
    rule('cartridges', not problems, '%d cartridge(s), %s%s' % (len(zips), L.human(total), ('; ' + '; '.join(problems)) if problems else ''))
    if warns:
        rule('cartridges', False, 'large: ' + ', '.join(warns), warn=True)
    return total


LICENSED = re.compile(rb'Artstor Collection|about\.jstor\.org/terms|Scala|Art Resource, NY|Bridgeman Images|Magnum Photos', re.I)


def check_licensed(courses):
    """Licensed images never sit on the public store. Two independent looks: (1) every
    web_resources entry in every cartridge, and every source under courses/<code>/files/,
    is scanned for the licence strings Artstor and the agencies embed in image metadata;
    (2) no cartridge carries an entry under its art-pack folder at all, whatever the bytes
    say. Figures declared in a spec are fine: cc.py writes only a path link for them."""
    problems, scanned, figures = [], 0, 0
    if os.path.isdir(L.CARTRIDGES):
        for fn in sorted(os.listdir(L.CARTRIDGES)):
            if not fn.endswith('.imscc') or fn.startswith('_'):
                continue
            kid = fn[:-6]
            side = L.read_json(L.sidecar_path(kid)) if os.path.exists(L.sidecar_path(kid)) else {}
            folder = ((side.get('art_pack') or {}).get('folder') or 'art').strip('/') + '/'
            figures += (side.get('art_pack') or {}).get('figures') or 0
            try:
                with zipfile.ZipFile(L.cartridge_path(kid)) as z:
                    for n in z.namelist():
                        if not n.startswith('web_resources/'):
                            continue
                        scanned += 1
                        rel = n[len('web_resources/'):]
                        if rel.startswith(folder):
                            problems.append('%s carries %s (the art-pack folder; images ship only in the art pack)' % (kid, n))
                        elif LICENSED.search(z.read(n)[:400000]):
                            problems.append('%s: %s carries a licence statement (Artstor/agency image in a public cartridge)' % (kid, n))
            except zipfile.BadZipFile:
                pass
    for d, c in courses:
        fdir = os.path.join(d, 'files')
        if os.path.isdir(fdir):
            for dp, _, fns in os.walk(fdir):
                for fn in fns:
                    scanned += 1
                    with open(os.path.join(dp, fn), 'rb') as fh:
                        if LICENSED.search(fh.read(400000)):
                            problems.append('%s carries a licence statement; remove it, declare it as a figure' % os.path.relpath(os.path.join(dp, fn), L.ROOT))
    rule('licensed', not problems, '%d bundled file(s) scanned, %d figure(s) link by path, no licensed image in the store%s'
         % (scanned, figures, ('; ' + '; '.join(problems[:8]) + (' ...' if len(problems) > 8 else '')) if problems else ''))


def check_catalog():
    r = subprocess.run([PY, os.path.join(L.HERE, 'make_catalog.py'), '--check'], capture_output=True, text=True, encoding='utf-8', cwd=L.ROOT)
    rule('catalog', r.returncode == 0, (r.stdout + r.stderr).strip().replace('\n', ' | '))


def check_fixture():
    fx = os.path.join(L.COURSES, '_example')
    specs = [p for p in os.listdir(fx) if p.endswith('.spec.json')] if os.path.isdir(fx) else []
    if not specs:
        rule('fixture', False, 'courses/_example has no spec; the toolchain is unproven'); return
    kid = specs[0][:-10]
    tmp = tempfile.mkdtemp(prefix='kitfixture-')
    sys.path.insert(0, L.HERE)
    import kit as K
    try:
        K.build_one(kid, force=True, root=tmp)
        side = L.read_json(os.path.join(tmp, 'cartridges', kid + '.json'))
        with zipfile.ZipFile(os.path.join(tmp, 'cartridges', kid + '.imscc')) as z:
            names = z.namelist()
            front = z.read(side['front_page']).decode('utf-8')
            ok = ('$CANVAS_COURSE_REFERENCE$/modules' in front and '$CANVAS_OBJECT_REFERENCE$/modules/' in front
                  and any(n.startswith('web_resources/') for n in names)
                  and len(side['graded_items']) == 4 and side['weighted'] is True)
        rule('fixture', ok, '%s built + verified in %s: %d items, %d graded, front page links resolved' % (kid, tmp, side['items'], len(side['graded_items'])))
    except SystemExit as e:
        rule('fixture', False, 'fixture build failed: %s' % e)


def main():
    courses = check_registry()
    check_specs(courses)
    total = check_cartridges(courses)
    check_licensed(courses)
    check_catalog()
    if '--no-fixture' not in sys.argv:
        check_fixture()
    rule('payload', total < L.REPO_WARN_BYTES, 'served cartridges total %s of the %s Pages ceiling' % (L.human(total), L.human(L.REPO_WARN_BYTES)), warn=True)
    fails = [r for r in results if r[0] == 'FAIL']
    print('\n%d PASS, %d WARN, %d FAIL' % (sum(1 for r in results if r[0] == 'PASS'), sum(1 for r in results if r[0] == 'WARN'), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
