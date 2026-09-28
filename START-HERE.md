# Start here

This folder contains Lukas Hensel's academic homepage. The current source map,
editing rules, and deployment behavior are in [README.md](README.md). Read that
first; it is the shared guide for people and tools on any platform.

## Work locally

From the repository root:

```sh
git status --short
git diff
```

Preserve existing work, edit the source identified in the README, then build:

```sh
python3 build.py
git diff --check
git diff
```

On Windows, `py -3 build.py` is an alternative to `python3 build.py`. The build
regenerates HTML in place. See the README for preview routing limitations and
checks appropriate to your change.

## Publication boundary

Prepare a reviewable local diff. Pushes to `main` trigger public deployment;
manual workflow dispatch can also publish. Do not push or trigger workflows
without Lukas's explicit request. Keep secret values in the deployment
platform's secret store, never in project notes.

## Moving between computers or tools

Use repository-relative paths and UTF-8 Markdown for notes. Record changed
files, checks, unresolved issues, and publication status so another person or
tool can continue without the original chat.

When working in a cloud-synced folder, avoid concurrent Git operations from
multiple computers. Prefer a separate Git checkout on each computer; configure
any cloud-sync exclusions using the provider's instructions for that OS.
Private CV source material under `Academic CV/` is ignored by Git, so a fresh
clone may not include it. Transfer needed source material separately through
an appropriate private channel.
