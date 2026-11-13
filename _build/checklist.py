"""checklist.py - the submission checklist. One kit, every criterion, MET or FLAGGED with evidence.

    python _build/checklist.py <kit-id> [<kit-id> ...]   checklist for the named kits
    python _build/checklist.py --all                     one summary line per kit, flagged criteria named
    python _build/checklist.py --changed <git-ref>       kits whose course folder differs from <git-ref>
    options:  --online   also read the live lesson pages: every embed answers, the whole-lesson
                         read-aloud player is at the top, tabbed lessons open each tab at the top
              --gate     the blocking run GitHub makes on every push and pull request: reads the
                         live pages and exits 1 when a REQUIRED criterion is unmet or unchecked
              --strict   exit 1 when any criterion is flagged
              --json     machine-readable result on stdout

check_repo.py decides whether the repo is intact (FAIL blocks a commit). This file reads
ONE kit the way a reviewer would and names what is not yet met. Most criteria only flag.
The ids in REQUIRED block: kit.py exits 1 on them and so does the GitHub workflow.

Each criterion is a row in CRITERIA: (id, label, function). A function returns
(state, evidence): state True = met, False = flagged, None = not applicable.
Add a criterion by adding a function and a row; nothing else changes.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as L  # noqa: E402

TAG = re.compile(r'<[^>]+>')
FACILITATOR = re.compile(r'facilitator', re.I)
WEEKDAY = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday)s?\b')
PLACEHOLDER = re.compile(
    r'\[(?:VERIFY|TODO|TBD|PLACEHOLDER|ARTICLE PLACEHOLDER|INSERT|LINK|IMAGE|SOURCE|CITATION)\b[^\]]*\]'
    r'|lorem ipsum|\bTODO\b|\bTBD\b', re.I)
STYLE_SCRIPT = re.compile(r'<\s*(style|script)\b', re.I)
CANVAS_URL = re.compile(r'https?://[a-z0-9.\-]+\.instructure\.com/courses/\d+', re.I)
WEFORUM = re.compile(r'weforum\.org|World Economic Forum', re.I)
WIKIPEDIA = re.compile(r'https?://[a-z]+\.(?:m\.)?wikipedia\.org', re.I)
LESSON_LINK = re.compile(r'<a\b[^>]*href="(https?://[a-z0-9\-]+\.github\.io/[^"]*)"', re.I)
IFRAME = re.compile(r'<iframe\b[^>]*\bsrc="([^"]+)"', re.I)
ELA = re.compile(r'english|language arts|ela\b|literature|reading|writing', re.I)


class Kit(object):
    """Everything one kit's criteria read, loaded once."""

    def __init__(self, kit_id):
        self.id = kit_id
        self.code = L.KIT_ID.match(kit_id).group('code')
        self.dir = os.path.join(L.COURSES, self.code)
        self.course = L.read_json(os.path.join(self.dir, 'course.json'))
        self.entry = next((k for k in self.course.get('kits', []) if k.get('id') == kit_id), {})
        self.spec_path = os.path.join(self.dir, kit_id + '.spec.json')
        self.spec = L.read_json(self.spec_path)
        sp = L.sidecar_path(kit_id)
        self.side = L.read_json(sp) if os.path.exists(sp) else None
        self.fields = list(self._fields())

    def _fields(self):
        """(where, text) for every string a student or teacher will read in Canvas."""
        s = self.spec
        for m in s.get('modules', []):
            yield 'module %s title' % m.get('id'), m.get('title') or ''
            for it in m.get('items', []):
                if it.get('title'):
                    yield 'module %s item %s title' % (m.get('id'), it.get('ref') or it.get('type')), it['title']
        for kind, coll, body in (('page', 'pages', 'html'), ('assignment', 'assignments', 'html'),
                                 ('discussion', 'discussions', 'html'), ('quiz', 'quizzes', 'description')):
            for o in s.get(coll, []):
                yield '%s %s title' % (kind, o.get('id')), o.get('title') or ''
                yield '%s %s' % (kind, o.get('id')), o.get(body) or ''
                for qq in o.get('questions', []) or []:
                    parts = [qq.get('text') or ''] + [a.get('text') or '' for a in qq.get('answers', []) or []]
                    yield 'quiz %s question' % o.get('id'), '\n'.join(parts)
        for r in s.get('rubrics', []):
            parts = [r.get('title') or '']
            for c in r.get('criteria', []) or []:
                parts += [c.get('description') or '', c.get('long_description') or '']
                parts += [x.get('long_description') or '' for x in c.get('ratings', []) or []]
            yield 'rubric %s' % r.get('id'), '\n'.join(parts)
        if s.get('syllabus_html'):
            yield 'syllabus', s['syllabus_html']

    def hits(self, rx, strip=True):
        """[(where, count)] for a pattern over every field; tags stripped unless strip=False."""
        out = {}
        for where, text in self.fields:
            n = len(rx.findall(TAG.sub(' ', text) if strip else text))
            if n:
                out[where] = out.get(where, 0) + n
        return sorted(out.items(), key=lambda kv: (-kv[1], kv[0]))


def cite(pairs, limit=4):
    total = sum(n for _, n in pairs)
    head = ', '.join('%s (%d)' % (w, n) if n > 1 else w for w, n in pairs[:limit])
    more = len(pairs) - limit
    return '%d in %d place(s): %s%s' % (total, len(pairs), head, (', +%d more' % more) if more > 0 else '')


def absent(rx, strip=True):
    def fn(k):
        h = k.hits(rx, strip)
        return (not h, cite(h) if h else '')
    return fn


# ---- registration and build -------------------------------------------------------------

def c_registered(k):
    miss = [f for f in ('title', 'grade', 'subject', 'owner') if not str(k.course.get(f) or '').strip()]
    if not k.entry:
        miss.append('kit entry in "kits"')
    elif not str(k.entry.get('label') or '').strip():
        miss.append('kit label')
    return (not miss, 'course.json is missing: ' + ', '.join(miss) if miss else '')


def c_source(k):
    src = k.spec.get('source')
    ok = bool(src) and bool(json.dumps(src).strip('{}" '))
    return (ok, '' if ok else 'spec has no "source" note saying which build folder it came from')


def c_built(k):
    if k.side is None or not os.path.exists(L.cartridge_path(k.id)):
        return (False, 'no cartridge yet: run python _build/kit.py %s' % k.id)
    if k.side.get('spec_sha') != L.spec_sha(k.spec_path):
        return (False, 'cartridge is older than the spec: run python _build/kit.py %s' % k.id)
    return (True, '')


def c_size(k):
    p = L.cartridge_path(k.id)
    if not os.path.exists(p):
        return (None, '')
    n = os.path.getsize(p)
    return (n <= L.CARTRIDGE_WARN_BYTES, '' if n <= L.CARTRIDGE_WARN_BYTES else '%s; move media to the lesson repo' % L.human(n))


# ---- structure --------------------------------------------------------------------------

def c_front(k):
    n = sum(1 for p in k.spec.get('pages', []) if p.get('front_page'))
    return (n <= 1, '' if n <= 1 else '%d pages carry front_page (at most 1; with none, the build adds Course Home)' % n)


def c_placed(k):
    s = k.spec
    used = {(it.get('type'), it.get('ref')) for m in s.get('modules', []) for it in m.get('items', [])}
    loose = []
    for kind, coll in (('page', 'pages'), ('assignment', 'assignments'), ('quiz', 'quizzes'), ('discussion', 'discussions')):
        for o in s.get(coll, []):
            if (kind, o.get('id')) not in used and not o.get('front_page'):
                loose.append('%s %s' % (kind, o.get('id')))
    empty = ['module %s is empty' % m.get('id') for m in s.get('modules', []) if not m.get('items')]
    bad = empty + loose
    return (not bad, '%d: %s%s' % (len(bad), ', '.join(bad[:4]), ', +%d more' % (len(bad) - 4) if len(bad) > 4 else '') if bad else '')


def c_markdone(k):
    s = k.spec
    front = {p.get('id') for p in s.get('pages', []) if p.get('front_page')}
    hidden = {p.get('id') for p in s.get('pages', []) if p.get('published') is False}
    miss, total = [], 0
    for m in s.get('modules', []):
        if m.get('published') is False:
            continue
        for it in m.get('items', []):
            if it.get('type') != 'page' or it.get('published') is False or it.get('ref') in front | hidden:
                continue
            total += 1
            if not it.get('completion'):
                miss.append(it.get('ref'))
    if not total:
        return (None, '')
    return (not miss, '%d of %d published module pages have no "completion": %s%s'
            % (len(miss), total, ', '.join(map(str, miss[:3])), ' ...' if len(miss) > 3 else '') if miss else '')


def c_weeks(k):
    if k.side is None:
        return (None, '')
    g = [x for x in k.side.get('graded_items', []) if x.get('published') is not False]
    if not g:
        return (None, '')
    miss = [x for x in g if x.get('week') in (None, '')]
    return (not miss, '%d of %d graded items have no week, so the date step cannot place them: %s%s'
            % (len(miss), len(g), ', '.join(str(x.get('title'))[:40] for x in miss[:3]), ' ...' if len(miss) > 3 else '') if miss else '')


def c_weights(k):
    groups = k.spec.get('assignment_groups', [])
    weighted = k.spec.get('course', {}).get('weighted') or any((g.get('weight') or 0) > 0 for g in groups)
    if not weighted:
        return (None, '')
    tot = sum(g.get('weight') or 0 for g in groups)
    return (abs(tot - 100) < 0.01, '' if abs(tot - 100) < 0.01 else 'group weights add up to %g, not 100' % tot)


def c_groups(k):
    s = k.spec
    ids = {g.get('id') for g in s.get('assignment_groups', [])}
    bad = []
    for kind, coll in (('assignment', 'assignments'), ('quiz', 'quizzes'), ('discussion', 'discussions')):
        for o in s.get(coll, []):
            graded = kind == 'assignment' or (kind == 'quiz' and o.get('quiz_type') in ('assignment', 'graded_survey')) \
                or (kind == 'discussion' and o.get('graded'))
            if graded and (o.get('group') not in ids if (o.get('group') or len(ids) != 1) else False):
                bad.append('%s %s' % (kind, o.get('id')))
    return (not bad, '%d graded item(s) name no gradebook group: %s%s' % (len(bad), ', '.join(bad[:4]), ' ...' if len(bad) > 4 else '') if bad else '')


def c_teacher_module(k):
    mods = [m for m in k.spec.get('modules', []) if re.search(r'\bteacher\b', m.get('title') or '', re.I)]
    if not mods:
        return (None, '')
    pub = [m.get('id') for m in mods if m.get('published') is not False]
    return (not pub, 'teacher module(s) ship published: ' + ', '.join(map(str, pub)) if pub else '')


# ---- text -------------------------------------------------------------------------------

def c_wikipedia(k):
    if not ELA.search(str(k.course.get('subject', '')) + ' ' + str(k.course.get('title', ''))):
        return (None, '')
    return absent(WIKIPEDIA, strip=False)(k)


def c_lesson_link(k):
    """A link to a lesson on GitHub Pages is fine only as the open-in-a-new-tab line under
    that same lesson's embed. A lesson reached by link alone is flagged."""
    def bare(u):
        return u.replace('&amp;', '&').split('#')[0].split('?')[0]
    bad = {}
    for where, text in k.fields:
        embedded = {bare(u) for u in IFRAME.findall(text)}
        for u in LESSON_LINK.findall(text):
            if bare(u) not in embedded:
                bad[where] = bad.get(where, 0) + 1
    h = sorted(bad.items(), key=lambda kv: (-kv[1], kv[0]))
    return (not h, cite(h) if h else '')


# ---- lessons and review -----------------------------------------------------------------

def iframes(k):
    out = []
    for where, text in k.fields:
        for u in IFRAME.findall(text):
            out.append((where, u.replace('&amp;', '&')))
    return out


def c_iframe_https(k):
    fr = iframes(k)
    if not fr:
        return (None, '')
    bad = [(w, 1) for w, u in fr if not u.startswith('https://')]
    return (not bad, cite(bad) if bad else '')


LESSON_HOST = re.compile(r'^https://[a-z0-9\-]+\.github\.io/', re.I)
NOT_A_LESSON = re.compile(r'/(?:widgets?|interactives?|games?|simulations?)/|teacher|syllabus', re.I)
# The whole-lesson player (Web Speech, reads the page top to bottom). Voiced clips (<audio>,
# ElevenLabs segments) are a different thing and never satisfy this.
READ_ALOUD = re.compile(r'id="optima-read-aloud"|<script[^>]+src="[^"]*read-aloud[^"]*"', re.I)
READ_ALOUD_AT = re.compile(r'id="optima-read-aloud"', re.I)
TABBED = re.compile(r'class="[^"]*\btab-(?:next|btn|panel)\b|role="tab"|data-tab=', re.I)
SCRIPT_SRC = re.compile(r'<script[^>]+src="([^"]+)"', re.I)
BLOCKS = re.compile(r'<(style|script)\b.*?</\1\s*>', re.I | re.S)
# moves the Canvas page: scrollIntoView on a top anchor (block start is the default)
SCROLL_PAGE = re.compile(r'scrollIntoView\(\s*(?:true)?\s*\)|scrollIntoView\(\s*\{[^}]*block\s*:\s*["\']start', re.I)
# moves only the lesson's own frame
SCROLL_FRAME = re.compile(r'\bscrollTo\(|\bscrollTop\s*=', re.I)
# "At the top" = only the lesson header reads before the player. Measured on 420 live lessons
# 2026-11-12: the header is under 450 characters of visible text on every one.
TOP_CHARS = 800
_FETCHED = {}


def fetch(u):
    """(status, text) for a URL, cached for the run. status is 200, an HTTP code or an error name."""
    import urllib.request
    import time
    if u not in _FETCHED:
        for attempt in (1, 2, 3):
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'optima-kit-checklist'})
                with urllib.request.urlopen(req, timeout=25) as r:
                    _FETCHED[u] = (r.status, r.read().decode('utf-8', 'replace'))
            except Exception as e:  # noqa: BLE001
                _FETCHED[u] = (getattr(e, 'code', None) or type(e).__name__, '')
            code = _FETCHED[u][0]
            if code == 200 or (isinstance(code, int) and code < 500):
                break                      # an answer; a 5xx or a dropped connection gets another try
            time.sleep(1.5 * attempt)
    return _FETCHED[u]


def fetch_all(urls):
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        return dict(zip(urls, ex.map(fetch, urls)))


def lessons(k):
    """Lesson pages a student meets in this kit: GitHub Pages embeds on published items in
    published modules. Widgets, games and teacher documents are not lessons."""
    s = k.spec
    hidden = set()
    for kind, coll in (('page', 'pages'), ('assignment', 'assignments'), ('quiz', 'quizzes'), ('discussion', 'discussions')):
        hidden |= {'%s %s' % (kind, o.get('id')) for o in s.get(coll, []) if o.get('published') is False}
    shown, placed = set(), set()
    for m in s.get('modules', []):
        for it in m.get('items', []):
            key = '%s %s' % (it.get('type'), it.get('ref'))
            placed.add(key)
            if m.get('published') is not False and it.get('published') is not False:
                shown.add(key)
    hidden |= placed - shown
    out = set()
    for where, u in iframes(k):
        u = u.split('#')[0]
        if where not in hidden and LESSON_HOST.match(u) and not NOT_A_LESSON.search(u):
            out.add(u)
    return sorted(out)


def names(urls, limit=3):
    return ', '.join(u.rstrip('/').rsplit('/', 1)[-1] for u in urls[:limit]) + (' ...' if len(urls) > limit else '')


def c_iframe_live(k):
    urls = sorted({u.split('#')[0] for _, u in iframes(k) if u.startswith('https://')})
    if not urls:
        return (None, '')
    got = fetch_all(urls)
    dead = ['%s -> %s' % (u, got[u][0]) for u in urls if got[u][0] != 200]
    return (not dead, '%d of %d embed URLs do not answer 200: %s%s' % (len(dead), len(urls), '; '.join(dead[:3]), ' ...' if len(dead) > 3 else '') if dead else '')


def c_read_aloud(k):
    urls = lessons(k)
    if not urls:
        return (None, '')
    got = fetch_all(urls)
    live = [u for u in urls if got[u][0] == 200]
    if not live:
        return ('?', 'no lesson could be read (offline, or none is published yet); not checked')
    missing, low = [], []
    for u in live:
        html = got[u][1]
        if not READ_ALOUD.search(html):
            missing.append(u); continue
        body = BLOCKS.sub('', html[html.lower().find('<body'):])
        m = READ_ALOUD_AT.search(body)
        if m and len(re.sub(r'\s+', ' ', TAG.sub(' ', body[:m.start()]))) > TOP_CHARS:
            low.append(u)
    parts = []
    if missing:
        parts.append('%d of %d lessons have no whole-lesson read-aloud player: %s' % (len(missing), len(live), names(missing)))
    if low:
        parts.append('%d have the player below the top of the lesson: %s' % (len(low), names(low)))
    return (not parts, '; '.join(parts))


def c_tab_scroll(k):
    """Static read of the lesson's own script. A tab change should bring the top of the lesson
    into view with scrollIntoView, which moves the Canvas page. window.scrollTo moves only the
    lesson's frame, and Canvas embeds are as tall as the lesson, so the student stays at the bottom."""
    from urllib.parse import urljoin
    urls = lessons(k)
    if not urls:
        return (None, '')
    got = fetch_all(urls)
    tabbed = [u for u in urls if got[u][0] == 200 and TABBED.search(got[u][1])]
    if not tabbed:
        return (None, '') if any(got[u][0] == 200 for u in urls) else ('?', 'no lesson could be read; not checked')
    none, frame = [], []
    for u in tabbed:
        js = got[u][1]
        for src in SCRIPT_SRC.findall(js):
            full = urljoin(u, src)
            if LESSON_HOST.match(full):
                js += fetch(full)[1]
        if SCROLL_PAGE.search(js):
            continue
        (frame if SCROLL_FRAME.search(js) else none).append(u)
    parts = []
    if none:
        parts.append('%d of %d tabbed lessons change tabs with no return to the top: %s' % (len(none), len(tabbed), names(none)))
    if frame:
        parts.append('%d scroll only inside the lesson frame (scrollTo), which does not move the Canvas page: %s' % (len(frame), names(frame)))
    return (not parts, '; '.join(parts))


def graded_count(k):
    s = k.spec
    return (len(s.get('assignments', []))
            + sum(1 for q in s.get('quizzes', []) if q.get('quiz_type') in ('assignment', 'graded_survey'))
            + sum(1 for d in s.get('discussions', []) if d.get('graded')))


def c_gb_groups(k):
    if not graded_count(k):
        return (None, '')
    g = [str(x.get('title') or '') for x in k.spec.get('assignment_groups', [])]
    if len(g) < 2:
        return (False, 'the gradebook has %s; create the course\'s groups and put every graded item in one'
                % ('one group, "%s"' % g[0] if g else 'no groups'))
    if 'Imported Assignments' in g:
        return (False, 'a stock group, "Imported Assignments", is still in the gradebook')
    return (True, '')


def c_gb_preset(k):
    groups = k.spec.get('assignment_groups', [])
    if not graded_count(k) or not groups:
        return (None, '')
    if k.spec.get('course', {}).get('weighted') or any((x.get('weight') or 0) > 0 for x in groups):
        return (True, '')
    return ('note', 'no group weights preset. Allowed: the groups are the minimum, and the teacher can set weights in the Optimizer')


def c_standards(k):
    ok = os.path.exists(os.path.join(k.dir, 'standards.json'))
    return (ok, '' if ok else 'courses/%s/standards.json not present (standards audit not recorded for this course)' % k.code)


CRITERIA = [
    ('registered',  'Course registered: title, grade, subject, owner, kit label', c_registered),
    ('source',      'Spec names the build folder it came from',                    c_source),
    ('built',       'Cartridge built from the current spec',                       c_built),
    ('size',        'Cartridge 10 MB or under',                                    c_size),
    ('front-page',  'No more than one front page',                                 c_front),
    ('placed',      'Every item sits in a module; no empty module',                c_placed),
    ('mark-done',   'Lesson pages carry Mark as done',                             c_markdone),
    ('weeks',       'Graded items carry a week',                                   c_weeks),
    ('gb-groups',   'Gradebook groups created',                                    c_gb_groups),
    ('groups',      'Every graded item is in a gradebook group',                   c_groups),
    ('gb-preset',   'Gradebook weights preset (optional)',                         c_gb_preset),
    ('weights',     'Group weights add up to 100',                                 c_weights),
    ('teacher-mod', 'Teacher module ships unpublished',                            c_teacher_module),
    ('teacher',     'Says "teacher", never "facilitator"',                         absent(FACILITATOR)),
    ('weekdays',    'Names weeks, never weekdays',                                 absent(WEEKDAY)),
    ('placeholder', 'No placeholders or [VERIFY] notes',                           absent(PLACEHOLDER)),
    ('style-script', 'No <style> or <script> in item HTML',                        absent(STYLE_SCRIPT, strip=False)),
    ('canvas-url',  'No URL pasted from a live Canvas course',                     absent(CANVAS_URL, strip=False)),
    ('lesson-link', 'Lessons are embedded, not linked out to GitHub',              c_lesson_link),
    ('weforum',     'No World Economic Forum sources',                             absent(WEFORUM, strip=False)),
    ('wikipedia',   'ELA: no Wikipedia links',                                     c_wikipedia),
    ('iframe-https', 'Lesson embeds use https',                                    c_iframe_https),
    ('standards',   'Standards file present',                                      c_standards),
]
# These read the live lesson pages, so they need the network. kit.py always runs them.
ONLINE = [
    ('iframe-live', 'Every lesson embed URL answers',                              c_iframe_live),
    ('read-aloud',  'Whole-lesson read-aloud player at the top of every lesson',   c_read_aloud),
    ('tab-scroll',  'Tabbed lessons open each tab at the top',                     c_tab_scroll),
]


# The criteria that block. Everything else flags. Ruled by the maintainer 2026-11-12: the
# whole-lesson reader on every lesson page, tabbed lessons open each tab at the top, gradebook
# groups created, every graded item in one.
REQUIRED = ('read-aloud', 'tab-scroll', 'gb-groups', 'groups')


def blocked(res):
    """Rows that stop this kit: a required criterion unmet, or one that could not be checked."""
    return [r for r in res['rows'] if (r['id'] in REQUIRED and r['state'] in (False, '?')) or r['id'] == 'load']


def run(kit_id, online=False):
    try:
        k = Kit(kit_id)
    except Exception as e:  # noqa: BLE001
        return {'kit': kit_id, 'label': '', 'rows': [{'id': 'load', 'label': 'Kit loads', 'state': False, 'evidence': str(e)}]}
    rows = []
    for cid, label, fn in CRITERIA + (ONLINE if online else []):
        try:
            state, ev = fn(k)
        except Exception as e:  # noqa: BLE001
            state, ev = False, 'check could not run: %s: %s' % (type(e).__name__, e)
        rows.append({'id': cid, 'label': label, 'state': state, 'evidence': ev})
    return {'kit': kit_id, 'label': '%s - %s' % (k.course.get('title', ''), k.entry.get('label') or kit_id), 'rows': rows}


def counts(res):
    met = sum(1 for r in res['rows'] if r['state'] is True)
    flagged = sum(1 for r in res['rows'] if r['state'] is False)
    return met, flagged, len(res['rows']) - met - flagged


def show(res):
    print('\nCHECKLIST  %s  %s' % (res['kit'], res['label']))
    for r in res['rows']:
        # [x] met   [ ] flagged   [~] allowed, noted   [?] could not be checked    -  does not apply
        box = {True: '[x]', False: '[ ]', None: ' - ', 'note': '[~]', '?': '[?]'}[r['state']]
        if r['id'] in REQUIRED and r['state'] in (False, '?'):
            box = '[!]'
        print(' %s %s%s%s' % (box, r['label'], '' if r['state'] is not None else '  (does not apply)',
                              '   REQUIRED' if box == '[!]' else ''))
        if r['state'] in (False, 'note', '?') and r['evidence']:
            print('       -> %s' % r['evidence'])
    met, flagged, other = counts(res)
    print(' %d met, %d flagged%s' % (met, flagged, (', %d other' % other) if other else ''))
    b = blocked(res)
    if b:
        print(' BLOCKED  %s cannot ship until every [!] line is met: %s' % (res['kit'], '; '.join(r['label'] for r in b)))


def all_kits():
    return [k['id'] for d, c in L.load_courses() for k in c.get('kits', [])
            if os.path.exists(os.path.join(d, k['id'] + '.spec.json'))]


def changed_kits(ref):
    r = subprocess.run(['git', 'diff', '--name-only', ref, '--', 'courses', 'cartridges'], capture_output=True, text=True, cwd=L.ROOT)
    if r.returncode:
        raise SystemExit('checklist: cannot compare against %r: %s' % (ref, r.stderr.strip()))
    paths = r.stdout.splitlines()
    # A spec or cartridge names its kit. Anything else in a course folder (course.json, files/)
    # touches every kit of that course; standards.json touches none.
    named, codes = set(), set()
    for p in paths:
        parts = p.split('/')
        if parts[0] == 'cartridges' and len(parts) == 2:
            named.add(os.path.splitext(parts[1])[0])
        elif parts[0] == 'courses' and len(parts) >= 3:
            if parts[2].endswith('.spec.json'):
                named.add(parts[2][:-len('.spec.json')])
            elif parts[2] != 'standards.json':
                codes.add(parts[1])
    return [k for k in all_kits() if k in named or L.KIT_ID.match(k).group('code') in codes]


def main():
    try:
        sys.stdout.reconfigure(errors='replace')
    except Exception:  # noqa: BLE001
        pass
    argv = sys.argv[1:]
    flags = {a for a in argv if a in ('--online', '--strict', '--json', '--all', '--gate')}
    if '--gate' in flags:
        flags.add('--online')
    rest = [a for a in argv if a not in flags]
    if '--changed' in rest:
        i = rest.index('--changed')
        kits = changed_kits(rest[i + 1])
    elif '--all' in flags:
        kits = all_kits()
    else:
        kits = rest
    if not kits and '--changed' not in rest:
        print(__doc__); sys.exit(2)
    results = [run(k, '--online' in flags) for k in kits]
    if '--json' in flags:
        print(json.dumps(results, indent=1))
    elif '--all' in flags:
        tally = {}
        for res in results:
            met, flagged, _ = counts(res)
            bad = [r['id'] for r in res['rows'] if r['state'] is False]
            for b in bad:
                tally[b] = tally.get(b, 0) + 1
            print('%-22s %2d met  %2d flagged  %s%s' % (res['kit'], met, flagged, 'BLOCKED  ' if blocked(res) else '', ' '.join(bad)))
        print('\n%d kit(s); %d with nothing flagged' % (len(results), sum(1 for r in results if not counts(r)[1])))
        for cid, n in sorted(tally.items(), key=lambda kv: -kv[1]):
            print('  %-13s flagged in %d kit(s)' % (cid, n))
    else:
        for res in results:
            show(res)
    if not kits:
        print('checklist: no kit changed against that ref')
    stopped = [r['kit'] for r in results if blocked(r)]
    if '--gate' in flags:
        print('\nGATE: %s' % ('%d kit(s) blocked: %s' % (len(stopped), ' '.join(stopped)) if stopped else 'passed'))
        sys.exit(1 if stopped else 0)
    sys.exit(1 if '--strict' in flags and any(counts(r)[1] for r in results) else 0)


if __name__ == '__main__':
    main()
