# Start here

Everything for lukashensel.com lives in this folder. It is already a git
repository with one commit. Four things left.

---

## 1. Stop Dropbox from syncing the `.git` folder

Do this **before** you touch anything else.

Git writes many small files very fast. Dropbox syncing them mid-write is the
standard way a repository in a Dropbox folder gets corrupted — and it is much
worse if you ever open this folder on a second machine. One line in Terminal
fixes it permanently:

```
xattr -w com.dropbox.ignored 1 "/Users/lukas/Library/CloudStorage/Dropbox/Lukas_homepage/.git"
```

Your files still sync and still back up. Only the repository's internal
bookkeeping stops syncing — which is fine, because GitHub is where the history
actually lives.

---

## 2. Put it on GitHub

Create an empty repository at <https://github.com/new>:

- **Name:** `website`
- **Public** — the repo holds no secrets, and public repositories get unlimited
  Actions minutes
- Do **not** tick "Add a README" — this folder already has one

Then, in Terminal:

```
cd "/Users/lukas/Library/CloudStorage/Dropbox/Lukas_homepage"
git remote add origin https://github.com/YOUR-USERNAME/website.git
git push -u origin main
```

If git asks for a password, it wants a personal access token, not your account
password. The path of least resistance is to install GitHub Desktop, sign in
once, and use **Add Local Repository** on this folder instead.

---

## 3. Add the two deploy secrets

On GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
Twice:

| Name | Value |
|---|---|
| `SERVER_IP` | `47.236.242.36` |
| `SERVER_SSH_KEY` | the private key the server setup script printed — everything from `-----BEGIN` to `-----END`, inclusive |

---

## 4. Deploy

**Actions** tab → *Deploy to server* → **Run workflow**.

From then on every `git push` (or every commit made through github.com) rebuilds
the pages and pushes them to the server. Roughly forty seconds.

---

## Working on it afterwards

Two equally good options, and you can switch freely:

- **In this folder.** Edit, then `git add -A && git commit -m "..." && git push`.
- **In the browser.** Open the file on github.com, click the pencil, commit.
  Then run `git pull` here before your next local edit.

What to edit for what is in `README.md`.

## First three things worth replacing

1. `assets/photo.jpg` — placeholder
2. `cv.pdf` — placeholder
3. The Chinese pages under `zh/` — my draft, needs a native speaker's eye
