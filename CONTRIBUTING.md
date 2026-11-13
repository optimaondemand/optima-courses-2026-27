# Contributing a course

This repo is what the Course Kit widget reads. Every course you add here becomes a
one-file Canvas import a teacher can fetch, customize and load without anyone
arranging it in Canvas. About ten builders share it; the rules below keep 130+ course
folders from colliding.

## Before your first commit

1. You need collaborator access from the maintainer (jdrexel@optimaed.com) and your
   own GitHub account. Commits are attributed by account; do not use the shared
   `optimaondemand` login for content work.
2. Clone the repo beside your other Optima checkouts. Python 3.9+ standard library
   is all the tooling needs. There are no dependencies to install.
3. Read `docs/SPEC.md` once. The spec is the contract; everything else is generated.

## One course = one folder you own

```
courses/<CPALMS code>/
  course.json              title, grade, subject, owner (your GitHub username), kits
  <code>-s1.spec.json      one spec per kit (semester, quarter or full-year)
  <code>-s2.spec.json
  files/                   only the files the specs bundle (syllabus, manual, a PDF)
```

Register the course first, even before any kit is written: a `course.json` with kits
listed and no specs shows the course in the widget as **pending**, which tells
teachers it is coming. Kit ids are `<code>-s1`, `<code>-s2`, `<code>-q1`..`q4`,
`<code>-t1`..`t3`, `<code>-full`, or one module, `<code>-m1`..`m99`. Titles for modules and items come from the
course's module maps (or the deployed Canvas course if one exists), never from taste.

**Honors and standard** are separate CPALMS codes, so they are separate course
folders. The widget lists them side by side and links one to the other from the
course card; it reads the level out of the title ("English 1 Honors"). If a title
does not say, add `"level": "Honors"` (or `"Standard"`) and, when two titles differ
in more than the level word, the same `"family": "English 1"` to both course.json files.

**Live and On-Demand.** One kit normally serves both section types. When a course
really ships two versions, give each kit its own id with a suffix, `<code>-s1-live`
and `<code>-s1-od` (or set `"mode": "live"` / `"od"` on the kit entry), and the
widget shows a Live / On-Demand switch in its kit step. Kits without a mode stay
visible under both.

**One module, or an alternate edition.** A kit can hold a single module,
`<code>-m3`, and an alternate build of content that already ships can carry the
`-sparkle` edition suffix, e.g. `<code>-m3-sparkle`: the integrated-week redesign of
Module 3, listed in the widget beside the original module it is an alternate for.
Teachers mix and order modules freely, so student-facing titles and text in a
one-module kit carry **no module number**: module titles read "King Arthur · Week 1",
never "Module 3 · Week 1". The number lives in `course.json` only, as planning labels
the widget shows teachers: `"label": "King Arthur · Sparkle"`, `"unit": "King Arthur"`,
`"replaces": "Module 3"` (the module of the semester kit this one stands in for).

Put your GitHub username in `owner`. `make_catalog.py` writes it into
`.github/CODEOWNERS`, so pull requests touching your folder request your review.

## Build, gate, commit

```
python _build/kit.py 1001040-s2          # builds cartridges/1001040-s2.imscc + .json, regenerates catalog.json, runs the gate
git add courses/1001040 cartridges/1001040-s2.imscc cartridges/1001040-s2.json catalog.json .github/CODEOWNERS
git commit -m "M/J Language Arts 2: Semester 2 kit"
git push
```

- **Stage explicit paths. Never `git add -A` or `git add .`** Other builders' work in
  progress may be in your working tree; a blanket add commits it under your name.
- `kit.py` skips a kit whose spec and files have not changed, so a rebuild does not
  add a new binary blob to history for nothing. `--force` overrides.
- The gate (`_build/check_repo.py`) must print `0 FAIL` before you commit. It is also
  what the pull-request workflow runs, once the maintainer installs it. A `WARN` is
  information for you: "facilitator" or weekday names in student text, a cartridge
  over 10 MB.
- Work on a branch named for the course (`1001040-s2`) and open a pull request when
  the course is already live and you are changing it. Direct pushes to `main` are fine
  for a course that is not yet ready in the widget.
- Never edit `catalog.json`, `.github/CODEOWNERS` or anything in `cartridges/` by hand.
  They are generated; the gate fails if they drift.

## The submission checklist

`kit.py` ends by printing a checklist for each kit you named: `[x]` met, `[ ]` flagged
with the item ids that caused it, `[~]` allowed but noted, `[?]` could not be checked,
`[!]` **required and unmet**. Clear each `[ ]` line, or say in the commit message why it
stands.

**Four criteria block.** A kit with a `[!]` line cannot ship: `kit.py` exits 1, and GitHub
runs the same check on every push and pull request, fails it, and comments the blocked
lines on your commit.

- Whole-lesson read-aloud player at the top of every lesson page
- Tabbed lessons open each tab at the top
- Gradebook groups created
- Every graded item is in a gradebook group

```
python _build/checklist.py 1001040-s2            # one kit, any time, builds nothing
python _build/checklist.py 1001040-s2 --online   # also requests every lesson embed URL
python _build/checklist.py --all                 # one line per kit in the store
python _build/checklist.py 1001040-s2 --gate     # what GitHub runs: exit 1 if a required line is unmet
```

| Criterion | Flagged when |
|---|---|
| Course registered | `course.json` lacks title, grade, subject, owner or the kit's label |
| Spec names its build folder | the spec has no `source` note |
| Cartridge built from the current spec | no cartridge, or the spec changed since the build |
| Cartridge 10 MB or under | the `.imscc` is larger |
| No more than one front page | two or more pages carry `front_page` |
| Every item sits in a module | a page, assignment, quiz or discussion is in no module, or a module is empty |
| Lesson pages carry Mark as done | a published module page has no `completion` |
| Graded items carry a week | a graded item has no week, so the date step cannot place it |
| Gradebook groups created | the gradebook has one group or none, or still holds "Imported Assignments". **Groups are the minimum every builder sets.** |
| Every graded item is in a gradebook group | a graded item names no group |
| Gradebook weights preset (optional) | never flagged. `[~]` notes that no weights are preset; that is allowed, and the teacher sets them in the Optimizer |
| Group weights add up to 100 | weighting is on and the weights do not total 100 |
| Teacher module ships unpublished | a module with "Teacher" in its title is published |
| Says "teacher" | "facilitator" appears in any title, body, question or rubric |
| Names weeks, never weekdays | Monday to Friday appears; a weekday inside a problem or a vocabulary item is yours to judge |
| No placeholders | `[VERIFY]`, `[ARTICLE PLACEHOLDER]`, `[IMAGE: ...]`, `[TBD ...]`, TBD, TODO, lorem ipsum |
| No `<style>` or `<script>` | either tag sits in item HTML (Canvas strips both) |
| No live Canvas URL | a link points at `...instructure.com/courses/<n>` instead of a `{{token}}` |
| Lessons embedded, not linked out | a GitHub Pages link is not the new-tab line under that same lesson's embed |
| No World Economic Forum sources | weforum.org or the name appears |
| ELA: no Wikipedia links | an ELA course links to wikipedia.org |
| Lesson embeds use https | an `<iframe>` source is not https |
| Standards file present | `courses/<code>/standards.json` does not exist yet |
| Every lesson embed URL answers | an embed URL does not return 200 |
| Whole-lesson read-aloud player at the top of every lesson | a lesson page has no `id="optima-read-aloud"` player, or more than the lesson header sits above it. This is the player that reads the whole lesson; voiced clips and ElevenLabs segments do not count. Every lesson page needs it, shared pages such as independent reading and practice pages included |
| Tabbed lessons open each tab at the top | a lesson with tabs changes tab without `scrollIntoView` on a top anchor, so the student lands at the bottom of the next tab. `window.scrollTo` alone is flagged: it moves only the lesson's frame, not the Canvas page |

The last three read the live lesson pages, so they need the network. `kit.py` always
runs them; `checklist.py` runs them with `--online`. Push the lesson repo before you
build the kit, or they read the old pages.

To add a criterion, add one function and one row to `CRITERIA` in `_build/checklist.py`.

## Changing a kit that teachers already imported

Cartridge identifiers are derived from `course.code + kind + id`, so a rebuilt kit
re-imported into the same Canvas course updates items in place. Keep every `id`
stable. Change titles, HTML, points and order freely. If you must remove an item, the
teacher's course keeps its copy until they delete it; say so in the commit message.

## Optional: prove the import

```
python _build/import_test.py cartridges/1001040-s2.imscc "ZZ Kit test 1001040-s2 (delete me)"
```

Creates a scratch course on optimaoaoteam, imports the cartridge, prints migration
issues and quiz question counts. Needs the Canvas token in the shared tokens file.
Delete the scratch course afterwards. Tell teachers to import as a **Canvas Course
Export Package** and to leave "Import existing quizzes as New Quizzes" **unchecked**;
that box empties every ungraded survey.

## What does not belong here

- Lesson HTML, images, video, fonts, interactive widgets: those live in the course's
  lesson repo on GitHub Pages and are embedded by URL. A spec page body is a short
  wrapper with an `<iframe>`.
- Anything hand-written into `cartridges/` or `catalog.json`.
- Tokens, credentials, student data.
- Course content for years other than 2026-27. Next year gets its own repo.
