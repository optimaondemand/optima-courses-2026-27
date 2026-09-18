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
`<code>-t1`..`t3` or `<code>-full`. Titles for modules and items come from the
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
