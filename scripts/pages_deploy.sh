#!/usr/bin/env bash
# Spiegelt build/ in den gh-pages-Branch. Der Branch enthaelt nur die fertige
# Seite — kein Repo-Inhalt, keine Historie zum Mitschleppen.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/pages.py
tmp=$(mktemp -d)
cp -R build/. "$tmp"/
git worktree remove --force .ghpages 2>/dev/null || true
if git show-ref --verify --quiet refs/heads/gh-pages; then
  git worktree add -q .ghpages gh-pages
else
  git worktree add -q --detach .ghpages
  git -C .ghpages checkout -q --orphan gh-pages
  git -C .ghpages rm -rqf . 2>/dev/null || true
fi
find .ghpages -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$tmp"/. .ghpages/
rm -rf "$tmp"
git -C .ghpages add -A
git -C .ghpages commit -q -m "Seite neu gebaut" || echo "nichts geaendert"
git -C .ghpages push -q -u origin gh-pages
git worktree remove --force .ghpages
echo "=> gh-pages gepusht"
