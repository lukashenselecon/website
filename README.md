# Lukas Hensel — academic homepage

Source for [lukashensel.com](https://lukashensel.com). This is a small static
site built with Python, HTML, and CSS, with no frontend framework or npm setup.
Read this guide before editing. All file paths below are relative to the
repository root, so the instructions work wherever the folder is checked out.

## Editing and publication rules

- Edit the source files, then regenerate the pages. Direct HTML edits will be
  overwritten by the next build.
- Preserve existing local changes. Review `git status` and the diff before work.
- Prepare a local, reviewable diff. Do not push, run deployment workflows, or
  publish without Lukas's explicit request. A push to `main` deploys the site.
- Use American spelling for this site's prose. Preserve source spelling in
  paper titles, abstracts, quotations, and citations.
- Keep author order and citation metadata faithful to the paper. Distinguish
  published, accepted, revision, working-paper, and in-progress statuses.
- Chinese copy is a draft and needs native-speaker review before publication.
- Verify time-sensitive claims and external links against current sources when
  editing them; a stored URL is not evidence that its destination is current.
- Keep credentials and private personal context out of documentation and public
  files. Store deployment secrets in the deployment platform's secret store.

## Source map

| Change | Source |
| --- | --- |
| Papers, authors, journals, abstracts, coverage, and links | [data.py](data.py) |
| Biography, page prose, navigation, and page structure | [build.py](build.py) |
| Courses, supervision, and reference-letter guidance | `teaching()` in `build.py` |
| Office hours in both languages | `OFFICE_HOURS_EN` and `OFFICE_HOURS_ZH` in `build.py` |
| CV page summary | `cv()` in `build.py` |
| Downloadable CV | [cv.pdf](cv.pdf); local LaTeX source is under `Academic CV/` |
| Portrait and profile buttons | `assets/photo.jpg`, `PROFILE_BUTTONS` in `build.py` |
| Colors, typography, and responsive layout | [assets/style.css](assets/style.css) |
| Visiting-academic guide | `visiting()` in `build.py` |
| Cycling itinerary and confirmation | `cycling()` and `cycling_thanks()` in `build.py` |
| Cycling map and route coordinates | [cyclemap.py](cyclemap.py), [cycling-route.json](cycling-route.json) |
| Hosted paper PDFs | `papers/`; see [paper guide](papers/README.md) |
| Event sign-up service | `deploy/signup/`; see [service guide](deploy/signup/README.md) |
| Server analytics and weekly digest | `deploy/analytics/`; see [analytics guide](deploy/analytics/README.md) |
| Public deployment | [.github/workflows/deploy.yml](.github/workflows/deploy.yml) |

The build uses Python's standard library. Run it from the repository root:
several asset and paper paths are resolved relative to the working directory.
The deployment workflow uses Python 3.12.

## Local workflow

1. Read this guide and inspect the existing changes:

   ```sh
   git status --short
   git diff
   ```

2. Edit the relevant sources, including both language versions where applicable.
3. Regenerate the HTML, robots file, and sitemap:

   ```sh
   python3 build.py
   ```

   On Windows, `py -3 build.py` is an alternative if Python is installed through
   the Windows launcher. The script writes its outputs in place.

4. Review the source and generated changes:

   ```sh
   git diff --check
   git diff --stat
   git diff
   ```

5. For layout changes, check desktop and phone widths, navigation, language
   switching, and any affected abstract or citation panels. Confirm local
   asset paths and changed external links. Leave the diff ready for review.

A basic local file server can display `/index.html` and other explicit HTML
paths, but production uses nginx to resolve extensionless routes such as
`/publications`. A plain `python3 -m http.server` does not reproduce that routing
or the sign-up backend; use a preview server with equivalent routing for a full
navigation check. Keep production links extensionless.

## Pages and assets

As checked against the local source on September 28, 2026, the build writes
20 HTML files:

- Five main pages in English and Chinese: Home, CV, Publications, Work in
  Progress, and Teaching and Supervision.
- English and Chinese 404 pages.
- Two `/references` redirect stubs pointing to `/teaching#references` in the
  matching language.
- English and Chinese cycling and cycling-confirmation pages.
- An English visiting guide and a Chinese-path redirect to that English page.

Only the ten main pages are in the sitemap. Cycling and visiting pages are
unlisted and marked `noindex`; this does not make them private.

English pages are at the root and Chinese pages under `zh/`. The shared page
builder supplies canonical URLs, language links, and social preview metadata.

Public Sans and IBM Plex Mono are bundled under `assets/fonts/`. Chinese text
uses system font fallbacks. Abstracts and citation panels use native HTML
`details` elements. Small inline scripts provide citation copying and redirects.
The cycling map loads external Amap tiles and overlays the route locally;
the site should not be described as making no external requests.

## Papers and citations

`data.py` contains four groups: `PUBS` (peer-reviewed publications), `WPS`
(working papers), `WIP` (work in progress), and `NPR` (other writing).

- `authors=[...]` controls citation author order, including Lukas. The fallback
  sorts names alphabetically by surname; use explicit metadata when available.
- `random_order=True` marks randomized order with ⓡ in the citation panel and
  adds an author-order note to BibTeX.
- `cite_year` supplies the citation year when the displayed status is not a year.
- `v`, `vs`, and `flag` control venue, volume/pages, and forthcoming status.
- `a_en` and `a_zh` supply the visible coauthor text. Keep them consistent with
  the full author list when editing a paper.
- `pdf("name.pdf", "https://fallback")` selects the local file in `papers/` when
  present, otherwise the external URL. See the paper guide for filenames.
- Link URLs beginning with `REPLICATION_URL` are omitted from the rendered page.
- Add coverage with `coverage=[("Label", "中文标签", "https://example.org/article")]`.

Citation and BibTeX formatting is implemented in `build.py`, with a link to
[econ.bst](https://ctan.org/pkg/econ-bst) for randomized-order entries. Check the
rendered citation and BibTeX after changing publication metadata.

`PEOPLE` maps coauthor names to URLs. Chinese pages also use `SURNAMES` and
`ZH_NAMES`; ambiguous surnames are not linked automatically. Verify a person's
current page before adding or replacing a link.

## Portrait and profiles

The portrait is `assets/photo.jpg`, also used for social previews. CSS displays
it at 212 × 265 pixels on desktop and 224 × 280 on phones; keep the source at
least 560 pixels wide.

`PROFILE_BUTTONS` controls the order of Google Scholar, ORCID, Twitter, Bluesky,
and LinkedIn. Emptying the associated profile setting hides that button. Icons
are loaded from `assets/icons/`, preferring SVG, then PNG, then WebP, with text
as a fallback. CSS displays the icons at 26 × 26 pixels.

## Deployment and server services

The GitHub Actions deployment runs on pushes to `main` and on manual dispatch.
It builds the pages, then mirrors files to the server using `rsync --delete`.
Removing a deployed file from the repository can therefore remove it remotely.
The workflow defines the destination and exclusions; `.gitignore` is not an
rsync exclusion list. Review what will be uploaded before an authorized deploy.

The deployment requires the `SERVER_IP` and `SERVER_SSH_KEY` repository secrets.
Keep their values out of notes. Server setup for analytics and event sign-ups
uses separate, manually dispatched workflows and the configuration described
in their respective guides. A normal page deployment does not reinstall those
services.

## Current maintenance notes

These are local-source observations from September 28, 2026, not a live-site
or external-source audit:

- Teaching already includes two Autumn 2026 courses, supervision guidance, and
  reference-letter instructions. Update these as teaching arrangements change.
- The analysis-code link for *Income Shocks and Suicides* is present in `data.py`.
  Its destination still needs checking when that entry is updated.
- The cycling page and confirmation say September 27, 2026; the sign-up service
  and its guide still name September 26, with a September 23 deadline. Reconcile
  the itinerary, service metadata, deadline, and messages before reusing it.
- The visiting guide contains time-sensitive travel advice. Verify it against
  current official sources before revising or publishing that advice.

## Portable notes and handoffs

Keep project knowledge in UTF-8 Markdown alongside the project so it can be
read by people and tools on any platform. This README is the project's durable
entry point; [START-HERE.md](START-HERE.md) is a short onboarding guide.

- Use repository-relative file links and ordinary web links. Avoid absolute
  user-directory paths, application-specific URLs, and references that require
  access to a particular chat or assistant's memory.
- State the working directory for commands and label any OS-specific steps.
- Keep essential editing rules here. If another tool needs its own instruction
  file, point it to this guide instead of maintaining a conflicting copy.
- Date status snapshots and distinguish verified facts from pending checks.
- Handoffs should state the task, changed files, validation performed, unresolved
  issues, and publication status. Update stale notes when the work changes.
- Do not copy private global profiles, credentials, or research-project files
  into this repository merely to make a handoff self-contained.
