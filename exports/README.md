# exports

Canvas cartridges (.imscc) exported or built outside the kit toolchain, kept here as
reference copies. Nothing in this folder is read by the Course Kit widget; the served
kits live in `cartridges/` and are generated from `courses/<code>/*.spec.json`.

One subfolder per course family.

## Light cartridges (media stripped)

The PE courses, the Hope and Discovering Computer Science section exports, and the
full Financial Literacy export carry hundreds of MB of uploaded video, which is over
GitHub's 100 MB per-file limit. The copies here have the `web_resources/` folder
removed: pages, quizzes, assignments, discussions and module structure are intact,
but embedded media links will not resolve until the course files are uploaded.

The complete cartridges, media included, are on OneDrive under
`Documents\Claude's Workshop\Course Cartridges (full)`. To get a working course,
import the full cartridge from OneDrive, or import the light one here and then upload
the media into the course's Files area with the same paths.

Canvas reports the missing `web_resources` entries as migration issues when a light
cartridge is imported. That is expected.
