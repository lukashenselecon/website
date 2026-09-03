# lukashensel.com

Ten static pages — five in English, five in Chinese — plus a small build script.
No frameworks, no npm, no external requests: the font is bundled, there is no
JavaScript, and nothing on any page calls a host that is blocked in China.

## How you change things

Everything you'll actually want to edit lives in **`data.py`** — every paper,
its authors, journal, abstract, and links. Edit it on github.com, commit, and
the GitHub Action rebuilds all ten pages and pushes them to the server. Live in
about forty seconds.

| I want to…                    | Edit                                            |
|-------------------------------|-------------------------------------------------|
| Add or update a paper         | `data.py`                                        |
| Change the bio or a page's prose | `build.py` (the `home`, `teaching`, `cv` functions) |
| Add courses                   | `build.py`, `teaching()` — the commented template |
| Replace your CV               | upload over `cv.pdf`                             |
| Replace your photo            | upload over `assets/photo.jpg`                   |
| Host a paper on your own domain | drop the PDF into `papers/` — see `papers/README.md` |
| Change colours or type        | `assets/style.css`                               |

You never need to run anything locally. If you want to preview a change before
committing, `python3 build.py` regenerates the HTML in place.

## One-time setup

1. Push this folder to a repository named `website` on your GitHub account.
2. **Settings → Secrets and variables → Actions → New repository secret**, twice:
   - `SERVER_IP` → `47.236.242.36`
   - `SERVER_SSH_KEY` → the private key the server setup script printed
     (everything from `-----BEGIN` to `-----END`, inclusive)
3. **Actions** tab → *Deploy to server* → **Run workflow**. First deploy done.

The server expects the files at `/var/www/lukashensel.com/`, which the setup
script created. `rsync --delete` mirrors the repo, so deleting a file here
deletes it there.

## Replace these three things first

- **`assets/photo.jpg`** — a placeholder. Plain background, shoulders up, at
  least 480×600. It's also the preview image when someone shares the link.
- **`cv.pdf`** — a placeholder. The address `lukashensel.com/cv.pdf` is stable,
  so it's the link worth putting in your email signature.
- **The Chinese pages** — I drafted them; you and a native-speaker colleague
  should correct the tone before you tell anyone the site exists.

## Still missing

- **Teaching page content.** The page is live but generic — courses, years, and
  levels go in `build.py`, in the commented block inside `teaching()`.
- **Four abstracts** — *Does Party Competition Affect Political Activism?*,
  *Designing Severance Insurance*, *Jobseekers' Beliefs about Comparative
  Advantage*, and *From Followers to Leaders*. Those four entries have no
  `ab=` field in `data.py`; add one and the Abstract toggle appears. The other
  twelve are in already, taken from the published versions.

## Notes

- URLs have no `.html` on the end — nginx's `try_files` handles that. Keep
  internal links written as `/publications`, not `/publications.html`.
- Chinese pages live under `/zh/`. Each page links to its counterpart through
  the EN / 中文 switch, and declares `hreflang` so search engines pair them.
- Chinese text uses whatever serif the reader's device has (Songti, PingFang,
  Noto). Bundling a CJK webfont would add several megabytes for no real gain.
- Abstracts use `<details>` — no JavaScript, so they still open if scripts are
  blocked or the page is printed.
