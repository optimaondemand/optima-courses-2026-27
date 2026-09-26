# The kit spec: `courses/<code>/<kit>.spec.json`

One JSON file per kit is the whole contract between a course build and the Course Kit
widget. How the file is produced is the course's business (a deploy harness, a script
over the build folder, Claude reading the module maps, or by hand). What it must
contain is fixed here and enforced by `_build/check_repo.py`. `_build/cc.py` turns it
into a Canvas-flavoured Common Cartridge 1.1; its docstring is the terse version of
this page.

## Top level

```json
{
  "course": {"title": "M/J Language Arts 2 Sem 2", "code": "1001040",
             "default_view": "wiki", "weighted": false, "announcements_on_home": false},
  "assignment_groups": [...],
  "rubrics": [...],
  "pages": [...],
  "assignments": [...],
  "quizzes": [...],
  "discussions": [...],
  "files": [...],
  "modules": [...],
  "syllabus_html": "<p>optional</p>",
  "source": {"note": "optional provenance: where this spec came from"}
}
```

- `course.code` must equal the folder name and the kit id prefix.
- `course.title` is what Canvas shows as the course name after import; the widget
  shows `course.json`'s title in its menu. Keep them consistent.
- `default_view` is always `wiki`: the widget swaps the teacher's home page into the
  front page. If no page carries `front_page: true`, the build inserts a placeholder.
- `weighted: true` or any group with a weight above 0 turns on percent weighting.
- `version` and `date` are stamped by the build; do not set them.

## Identifiers

Every `id` is a short, stable, human-readable string unique within its collection
(`p_m1_lesson_1`, `a_m1_essay`, `q_m1_check`, `d_m1`, `m_1`, `ag_practice`, `r_essay`).
Cartridge identifiers are derived deterministically from `code + kind + id`, so a
rebuilt kit re-imported into the same Canvas course updates items in place. **Renaming
an id creates a new Canvas item and orphans the old one.** Change titles freely; change
ids only before a kit is live.

## Link tokens

Allowed inside any HTML field. Canvas rewrites them to real URLs on import, which is
what lets a home page link to modules that do not exist yet.

| Token | Points at |
|---|---|
| `{{page:ID}}` `{{assignment:ID}}` `{{quiz:ID}}` `{{discussion:ID}}` `{{module:ID}}` | an item in this spec (unknown id = build error) |
| `{{file:folder/name.ext}}` | a bundled file by its `path` |
| `{{modules}}` `{{syllabus}}` `{{grades}}` `{{assignments}}` `{{announcements}}` `{{home}}` | course tabs |

Any `{{...}}` left unresolved fails the build. Never paste a Canvas URL from a live
course; it points at that course, not the teacher's.

## Objects

**assignment_groups** `[{id, title, weight}]`. Required when any graded item exists.
With exactly one group, items may omit `group`.

**rubrics** `[{id, title, free_form_comments, criteria: [{description, long_description,
points, ratings: [{description, long_description, points}]}]}]`. Referenced from an
assignment or graded discussion by `rubric: id`; `rubric_use_for_grading` defaults true.

**pages** `[{id, title, html, front_page, published, slug}]`. `slug` optional; derived
from the title. Exactly one page may be `front_page: true`.

**assignments** `[{id, title, html, points, group, rubric, grading_type, submission_types,
allowed_extensions, published, omit_from_final_grade, due_at, unlock_at, lock_at, week, kind}]`.
`submission_types` defaults to `online_text_entry,online_upload`. `grading_type` defaults
to `points`.

**quizzes** `[{id, title, description, quiz_type, points, allowed_attempts, shuffle_answers,
show_correct_answers, group, published, due_at, unlock_at, lock_at, week, kind, questions}]`.
`quiz_type` is `assignment` (graded), `practice_quiz`, `graded_survey` or `survey` `grading_type` (default `points`; `pass_fail` = complete/incomplete) applies to the assignment Canvas creates for an `assignment` or `graded_survey` quiz.
(ungraded; the intro/outro pattern). `allowed_attempts: -1` means unlimited. `points`
may be omitted; the build sums the questions.

Question: `{type, text, points, answers: [{text, correct, feedback}], feedback_correct,
feedback_incorrect, feedback_general}` with `type` one of `multiple_choice`, `true_false`,
`multiple_answers`, `short_answer`, `essay`, `file_upload`, `text_only`. Essay and
file-upload questions take `answers: []`.

**discussions** `[{id, title, html, graded, points, group, rubric, require_initial_post,
discussion_type, published, due_at, unlock_at, lock_at, week, kind}]`. `graded: true`
creates the shadow assignment Canvas expects.

**files** `[{path, src}]`. `path` is the folder and name inside the Canvas Files tab
(`teacher-resources/Syllabus.pdf`). `src` is **relative to the spec's folder** and must
live under `courses/<code>/files/` in this repo, forward slashes, no `..`, never an
absolute path. Keep bundled files small: syllabus, teacher manual, a reference PDF.
Lesson media, videos, fonts and interactive pages stay in the course's lesson repo on
GitHub Pages and are embedded from there.

**figures** on a page, assignment or discussion: `[{file, src, title, artist, date, medium,
collection, credit, alt, description}]`. For **licensed images (Artstor / Images on JSTOR,
agency photographs)** that may be shown to enrolled students but never published on an
open website. Each figure renders as a Canvas-native block ABOVE the object's `html`:
image, then an italic title with artist, date and medium, then a credit line. The `<img>`
links to the course file **by path** (`course files/<folder>/<file>`), so the cartridge
holds no image bytes and the link survives course copies. The images travel separately in
the **art pack**, a files-only cartridge built by `python _build/art_pack.py <kit>` from the
same spec and placed on a login-gated store (SharePoint), which the teacher imports into
the same course. `file` is a bare name ending `.jpg` or `.png`; `src` is the source image
relative to `art_pack.root`; `title` is required; `alt` is one factual clause. Caption
fields come from the image's own metadata, never from memory. The `licensed` gate fails
any cartridge or bundled file that carries a licence statement or an entry under the art
folder.

**art_pack** `{folder, root, note}` (top level). `folder` (default `art`) is the Canvas
Files folder the figures link to and the art pack fills; the folder is hidden from the Files tab
but the files inside are not. Canvas resolves a path link (`file_contents/course files/...`)
only to a file whose state is available, so a file marked hidden shows as a broken image.
`root` is the folder the figure `src` paths are read from, relative to the builder's
OneDrive. Neither the sources nor the pack live in this repo.

**modules** `[{id, title, published, sequential, unlock_at, items: [ITEM]}]` in the order
students see them. ITEM `{type, ref, title, url, new_tab, indent, published, week,
completion}`:

| type | ref | notes |
|---|---|---|
| `page` `assignment` `quiz` `discussion` | the object's id | `title` optional; defaults to the object's |
| `file` | the file's `path` | |
| `url` | none; give `url` and `title` | external link |
| `header` | none; give `title` | text sub-header inside the module |

`completion` puts the item in the module's `<completionRequirements>` block, which is
what draws the **Mark as done** button students use. It is a string — `must_view`,
`must_mark_done`, `must_submit`, `must_contribute` — or `{"type": "min_score",
"min_score": 16}` for a score gate. A header cannot carry one. Optima lesson pages take
`must_mark_done`; leaving it off ships a course whose pages have no Mark as done button.

`week` on an item (or `Week N` in its title) is what the widget's date panel uses to
place due dates. `kind` is a free label (`quick-write`, `module-discussion`) the widget
shows when a teacher edits points.

## Dates

`due_at`, `unlock_at`, `lock_at` and module `unlock_at` are `YYYY-MM-DDTHH:MM:SS` in UTC
with no zone suffix, exactly as Canvas exports write them. Most kits ship with **no
dates**: the teacher sets a term start in the widget and it stamps them from `week`.

## Sizes and what not to put in a spec

- A kit's cartridge must stay under 25 MB (gate fails) and should stay under 10 MB
  (gate warns). Three PDFs took one kit to 12 MB; a syllabus PDF alone is ~1 MB.
- No `<style>` or `<script>` in HTML bodies: Canvas strips both on import. Inline
  styles survive. Interactive content is an `<iframe>` to the lesson repo on Pages.
- No teacher-only text in student-facing fields (build notes, answer rationales,
  standards codes). Teacher material goes in an unpublished Teacher Resources module.
- Student text says **teacher**, never facilitator, and names weeks, never weekdays.
  The gate reports both.

## Minimal complete example

`courses/_example/0000000-s1.spec.json` is a full, valid spec with every object type,
placeholder text only. Copy it to start a course and replace everything.
