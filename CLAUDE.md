# CLAUDE.md — optima-courses-2026-27

You are working in the content store the Optima Course Kit widget reads. Ten
curriculum builders share it; each owns course folders. Your job in this repo is one
of three things: register a course, author or update a kit spec, or build and ship a
kit. Read `docs/SPEC.md` before writing a spec and `CONTRIBUTING.md` before committing.

## What "deploy to Canvas" means now

It means **kit it**. No script here writes to Canvas. When a builder asks to "arrange
the course in Canvas", "deploy", "push to Canvas" or "make it available to teachers":

1. Confirm the course code, the kit (semester/quarter), and the **authoritative build
   folder** (ask which of 03_Development / 04_Final is current; they differ).
2. Register in `courses/<code>/course.json` if absent. Titles and grade/subject come
   from the CPALMS listing; `owner` is the builder's GitHub username.
3. Produce `courses/<code>/<kit>.spec.json` from the build folder. Module and item
   **titles and order come from the course's module maps** (or the deployed Canvas
   course if one exists), never from taste. Points and groups come from the course's
   own rules; ask if they are not written down.
4. Copy only the files the spec bundles into `courses/<code>/files/` (syllabus,
   teacher manual, at most a reference PDF). Never copy lesson media here.
5. `python _build/kit.py <kit>` until the gate prints `0 FAIL`.
6. Optionally `python _build/import_test.py cartridges/<kit>.imscc "ZZ Kit test <kit> (delete me)"`
   and read the migration issues. Delete the scratch course.
7. Stage explicit paths, commit under the builder's own account, push. Pages rebuilds
   in about a minute; the widget shows the kit as READY.

## Hard rules

- **Never `git add -A` or `git add .`** Other builders' uncommitted work may be in the
  tree. Stage `courses/<code>`, `cartridges/<kit>.imscc`, `cartridges/<kit>.json`,
  `catalog.json`, `.github/CODEOWNERS`.
- Never hand-edit `cartridges/`, `catalog.json`, `.github/CODEOWNERS`.
- Never rename an `id` in a spec whose kit is live: identifiers derive from ids and a
  rename orphans the teacher's Canvas item.
- No course content from outside 2026-27, no tokens, no student data.
- File `src` paths are relative, forward-slash, inside `courses/<code>/files/`.
- No `<style>` or `<script>` in HTML bodies (Canvas strips them). Interactive lessons
  are an `<iframe>` to the course's lesson repo on GitHub Pages.
- Student-facing text: say **teacher**, never facilitator; name **weeks**, never
  weekdays; no teacher notes, standards codes or answer rationales in student fields.
  Teacher material goes in an unpublished Teacher Resources module.
- Do not fabricate texts or content. A spec wraps what the course build already
  contains; if a lesson, quiz or rubric is missing from the build folder, say so and
  stop rather than inventing it.

## How the pieces fit

`courses/<code>/<kit>.spec.json` (the contract) -> `_build/cc.py` (Canvas-flavoured
Common Cartridge 1.1, deterministic ids, `{{link tokens}}` rewritten on import) ->
`cartridges/<kit>.imscc` + `<kit>.json` sidecar (front page path, module gids, every
graded item's XML path) -> `catalog.json` (light index; the widget fetches the sidecar
on selection) -> GitHub Pages -> widget patches home page, dates, points, groups,
published state inside the zip in the browser -> teacher imports one file.

`_build/kit.py` skips kits whose spec + files hash matches the sidecar's `spec_sha`,
so history only grows when content changes. `_build/check_repo.py` is a table of
independent rules and prints evidence for each; treat any `FAIL` as blocking and any
`WARN` as something to tell the builder.

## Producing a spec from a build folder

There is no one parser: build folders follow different conventions per course family.
For 7th ELA, `optima-course-kit/_build/folder_to_spec.py` + `recipes/` reads the
course's own deploy harness. For a course with no harness, read the module maps and
the `.md` quiz/discussion/rubric specs and write the JSON directly, then run the gate.
Whatever the route, the spec is what is reviewed, so keep ids readable
(`p_m3_lesson_2`, `q_m3_checkup`) and put a `source` note in the spec saying where it
came from.

Canvas quirks that matter when reading a live course as reference: quiz
`points_possible` reads 0 for API-built quizzes (sum the questions); every graded quiz
and discussion has a shadow assignment; import with "as New Quizzes" empties surveys.

## Verification standard

A printed "ok" is not evidence. Before reporting a kit as ready: the gate printed
`0 FAIL`; the sidecar's counts match what the build folder contains; the cartridge is
under 10 MB or you have said why not; and if an import test ran, it reported zero
issues and the quiz question counts you expected. Report warnings verbatim.

## Maintainer-only

Enabling the PR gate: `_build/workflow-gate.yml` -> `.github/workflows/gate.yml` via
the GitHub web UI (the shared account's token lacks the `workflow` scope). Adding a
contributor: repo Settings -> Collaborators, or
`PUT /repos/optimaondemand/optima-courses-2026-27/collaborators/<username>` with the PAT.
Switching the widget to this store: `DEFAULT_BASE` in `optima-course-kit/index.html`.
