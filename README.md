# Optima courses 2026-27

The content store behind the **Course Kit** widget
(https://optimaondemand.github.io/optima-course-kit/). A teacher types a CPALMS code,
picks the kit for their section, fills in a home page, sets dates and gradebook
choices, and downloads one Canvas cartridge. Everything the widget offers comes from
this repo, served by GitHub Pages at

    https://optimaondemand.github.io/optima-courses-2026-27/

Canvas is no longer a step in distribution. Builders commit here; teachers import.

## Layout

```
courses/<code>/course.json          registry entry: title, grade, subject, owner, kits   (hand-edited by the owner)
courses/<code>/<kit>.spec.json      the kit spec, see docs/SPEC.md                       (authored per course)
courses/<code>/files/               files the spec bundles into the cartridge            (small: syllabus, manual)
cartridges/<kit>.imscc + <kit>.json built cartridge + sidecar                             (generated)
catalog.json                        light index the widget loads first                    (generated)
.github/CODEOWNERS                  who reviews which course folder                       (generated from owners)
_build/                             the toolchain, Python standard library only
docs/SPEC.md                        the spec contract
courses/_example/                   synthetic fixture; proves the toolchain, never listed
```

Built for 130+ courses and about ten contributors: one folder per course so nobody
edits a shared file, an index under 200 KB however many courses exist, per-kit detail
fetched only when a teacher selects that kit, and a gate that refuses stale or
malformed content before it can reach a teacher.

## Add or update a course

See `CONTRIBUTING.md`. Short form:

```
courses/1001040/course.json                       register the course (shows as pending in the widget)
courses/1001040/1001040-s1.spec.json              write the kit spec
python _build/kit.py 1001040-s1                   build + verify + catalog + gate
git add courses/1001040 cartridges/1001040-s1.* catalog.json .github/CODEOWNERS
git commit && git push                            live in the widget after Pages rebuilds (~1 min)
```

## Tools

| Command | Does |
|---|---|
| `python _build/kit.py <kit> [--force]` / `--all` | Build changed kits, regenerate the catalog, run the gate. The one command builders need. |
| `python _build/check_repo.py` | The gate: registry, specs, voice, cartridges, catalog, fixture, payload. `0 FAIL` or nothing ships. |
| `python _build/make_catalog.py [--check]` | `courses/*/course.json` + sidecars -> `catalog.json` + `CODEOWNERS`. |
| `python _build/build_kit.py <spec> <kit> --label L` | Spec -> cartridge + sidecar, verified. `kit.py` calls this. |
| `python _build/verify_cartridge.py <imscc>` | Structural gate for any Canvas cartridge, including real exports. |
| `python _build/import_test.py <imscc> "<name>"` | Import into a scratch Canvas course on optimaoaoteam and report issues. Needs the Canvas token. |
| `python _build/pull_canvas.py <course id> <code> <out>` | READ-ONLY: live Canvas course -> spec. Reference for the compare gate on courses that were deployed the old way. |
| `python _build/compare_specs.py <folder spec> <canvas spec>` | Item-by-item equivalence, for courses that have both. |

## Rules that are not negotiable

- Nothing in `cartridges/`, `catalog.json` or `CODEOWNERS` is hand-edited.
- Stage explicit paths; never `git add -A`.
- Keep `id` values stable once a kit is live; identifiers derive from them.
- Bundled files live under `courses/<code>/files/` and stay small. Media belongs in the
  course's lesson repo on GitHub Pages.
- Student text says teacher, not facilitator, and names weeks, not weekdays.
- Cartridges carry quiz answer keys and this repo is public. That is the decision for
  2026-27; a signed-in store is next year's change.

## Teacher import notes (the widget shows these too)

Import as **Canvas Course Export Package**. Leave **Import existing quizzes as New
Quizzes** unchecked; that option empties every ungraded intro/outro survey.

## Related

- Widget: https://github.com/optimaondemand/optima-course-kit
- Predecessor store (three 2026-27 kits, frozen): https://github.com/optimaondemand/optima-course-cartridges
- Cartridge layout notes: `_build/cc.py` docstring and `docs/SPEC.md`
