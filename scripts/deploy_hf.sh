#!/usr/bin/env bash
# Deploy the last commit to a Hugging Face Docker Space.
#
#   HF_TOKEN=hf_xxx scripts/deploy_hf.sh your-hf-username/krishimitra
#   DRY_RUN=1 scripts/deploy_hf.sh your-hf-username/krishimitra   # build the snapshot only
#
# Pushes a fresh one-commit snapshot (not the GitHub history, which contains old large
# files). Every binary file (images, fonts, videos, models, .mo) is stored with Git LFS,
# because Hugging Face rejects binary files that are not. Secrets are NOT uploaded:
# .env is git-ignored; set secrets in the Space's Settings page instead.
set -euo pipefail

SPACE="${1:?usage: HF_TOKEN=... scripts/deploy_hf.sh <hf-username>/<space-name>}"
ROOT="$(git rev-parse --show-toplevel)"
command -v git-lfs >/dev/null || { echo "Git LFS missing: brew install git-lfs"; exit 1; }
if [ -n "$(git -C "$ROOT" status --porcelain --untracked-files=no)" ]; then
  echo "You have uncommitted changes. Commit them first; the deploy uses your last commit."; exit 1
fi
if [ -z "${DRY_RUN:-}" ] && [ -z "${HF_TOKEN:-}" ]; then
  echo "Set HF_TOKEN to a Hugging Face access token with WRITE permission."; exit 1
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
APP="$TMP/app"; mkdir -p "$APP"

echo "1/4 Copying tracked files of commit $(git -C "$ROOT" rev-parse --short HEAD)..."
(cd "$ROOT" && git ls-files -z | rsync -a --from0 --files-from=- ./ "$APP/")

echo "2/4 Adding Hugging Face Space settings..."
{
  printf -- '---\ntitle: KrishiMitra\nemoji: 🌾\ncolorFrom: green\ncolorTo: yellow\nsdk: docker\napp_port: 8000\npinned: false\n---\n\n'
  cat "$ROOT/README.md" 2>/dev/null || true
} > "$APP/README.md"

echo "3/4 Storing binary files with Git LFS..."
cd "$APP"
git init -q -b main
git lfs install --local >/dev/null
exts="$( { git ls-files --others -z | xargs -0 grep -IL '' 2>/dev/null || true; } \
        | while read -r f; do if [ -s "$f" ]; then echo "${f##*.}"; fi; done | tr 'A-Z' 'a-z' | sort -u)"
for e in $exts; do git lfs track "*.$e" >/dev/null; done
echo "    LFS file types: $(echo $exts | tr '\n' ' ')"
git add -A
git -c user.name="deploy" -c user.email="deploy@localhost" commit -q -m "Deploy $(git -C "$ROOT" rev-parse --short HEAD)"
big="$(git ls-files -z | xargs -0 git check-attr filter -- | grep -v ': lfs$' | cut -d: -f1 \
        | while read -r f; do [ "$(wc -c < "$f")" -gt 10000000 ] && echo "$f"; done || true)"
[ -z "$big" ] || { echo "Files over 10 MB not in LFS: $big"; exit 1; }
echo "    $(git ls-files | wc -l | tr -d ' ') files, $(git lfs ls-files | wc -l | tr -d ' ') in LFS"

if [ -n "${DRY_RUN:-}" ]; then echo "DRY_RUN: snapshot OK, nothing pushed."; exit 0; fi

echo "4/4 Uploading to https://huggingface.co/spaces/$SPACE (this can take a few minutes)..."
git push --force -q "https://user:${HF_TOKEN}@huggingface.co/spaces/${SPACE}" main
echo "Done. Watch the build: https://huggingface.co/spaces/$SPACE  (Logs → Build)"
