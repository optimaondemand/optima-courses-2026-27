"""kitlib.py - shared helpers for the optima-courses-2026-27 build tools.

Repo layout this encodes:
  courses/<code>/course.json            registry entry (one per course, hand-edited by its owner)
  courses/<code>/<kit>.spec.json        the cc.py spec for one kit (the contract, see docs/SPEC.md)
  courses/<code>/files/...              files the spec bundles into the cartridge
  cartridges/<kit>.imscc + <kit>.json   built cartridge + sidecar (generated, never hand-edited)
  catalog.json                          light index the widget loads first (generated)
  .github/CODEOWNERS                    generated from course.json owners

Folders under courses/ whose name starts with "_" are fixtures: built by the gate,
never listed in the catalog.
"""
import glob
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
COURSES = os.path.join(ROOT, 'courses')
CARTRIDGES = os.path.join(ROOT, 'cartridges')

KIT_ID = re.compile(r'^(?P<code>[A-Za-z0-9.]+)-(?P<part>s[12]|q[1-4]|full|t[1-3])$')
CPALMS = re.compile(r'^\d{7}$')
CARTRIDGE_WARN_BYTES = 10 * 1024 * 1024
CARTRIDGE_FAIL_BYTES = 25 * 1024 * 1024
REPO_WARN_BYTES = 800 * 1024 * 1024      # GitHub Pages serves at most 1 GB


def read_json(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def write_json(path, data):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write('\n')


def course_dirs(include_fixtures=False):
    out = []
    for d in sorted(glob.glob(os.path.join(COURSES, '*'))):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        if name.startswith('_') and not include_fixtures:
            continue
        out.append(d)
    return out


def load_courses(include_fixtures=False):
    """[(dir, course.json dict)] for every course folder. Raises on a folder with no course.json."""
    out = []
    for d in course_dirs(include_fixtures):
        p = os.path.join(d, 'course.json')
        if not os.path.exists(p):
            raise SystemExit('courses/%s has no course.json' % os.path.basename(d))
        out.append((d, read_json(p)))
    return out


def spec_path_for(kit_id, include_fixtures=True):
    m = KIT_ID.match(kit_id)
    if not m:
        raise SystemExit('kit id %r is not <code>-<s1|s2|q1..q4|t1..t3|full>' % kit_id)
    for d in course_dirs(include_fixtures):
        p = os.path.join(d, kit_id + '.spec.json')
        if os.path.exists(p):
            return p
    raise SystemExit('no courses/*/%s.spec.json' % kit_id)


def spec_sha(spec_path):
    """sha256 over the spec file and every bundled file it names, so a changed
    PDF or a changed sentence both count as a changed kit."""
    h = hashlib.sha256()
    with open(spec_path, 'rb') as fh:
        h.update(fh.read())
    spec = read_json(spec_path)
    base = os.path.dirname(os.path.abspath(spec_path))
    for f in spec.get('files', []):
        src = f.get('src') or ''
        p = src if os.path.isabs(src) else os.path.join(base, src)
        h.update(('\n' + f.get('path', '')).encode('utf-8'))
        if os.path.exists(p):
            with open(p, 'rb') as fh:
                h.update(fh.read())
        else:
            h.update(b'<missing>')
    return h.hexdigest()


def sidecar_path(kit_id):
    return os.path.join(CARTRIDGES, kit_id + '.json')


def cartridge_path(kit_id):
    return os.path.join(CARTRIDGES, kit_id + '.imscc')


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return '%.1f %s' % (n, unit) if unit != 'B' else '%d B' % n
        n /= 1024.0
