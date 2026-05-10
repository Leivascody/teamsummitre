#!/usr/bin/env bash
# One-time push of the Summit website to github.com/Leivascody/teamsummitre
# Run from anywhere — the script cd's into its own folder.
set -e

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SITE_DIR"

echo "==> Initializing git repo in $SITE_DIR"
if [ ! -d .git ]; then
    git init -b main
else
    git checkout -B main
fi

git add -A
if git diff --cached --quiet; then
    echo "==> No changes to commit"
else
    git -c user.email="leivas.cody@gmail.com" -c user.name="Cody Leivas" \
        commit -m "Add Summit Real Estate Services website (multi-page, brand system)"
fi

# Set / refresh the remote
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin https://github.com/Leivascody/teamsummitre.git
else
    git remote add origin https://github.com/Leivascody/teamsummitre.git
fi

echo "==> Force-pushing to overwrite the bootstrap commit"
git push -u --force origin main

echo
echo "Done. Repo: https://github.com/Leivascody/teamsummitre"
echo "Next: Settings -> Pages -> Source = main / root, then visit https://leivascody.github.io/teamsummitre/"
