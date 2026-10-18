#!/usr/bin/env bash
# Bump SessionIntent version across the files that ship in a release.
# packaging/arch and packaging/flatpak are reference-only (not built by CI);
# bump them by hand if that packaging is ever revived.
# Usage: ./scripts/bump-version.sh 0.4.5
set -euo pipefail
NEW="${1:?usage: $0 <version>}"
OLD=$(grep -oP '__version__ = "\K[^"]+' src/sessionintent/__init__.py)

sed -i "s/__version__ = \"${OLD}\"/__version__ = \"${NEW}\"/" src/sessionintent/__init__.py
sed -i "s/^Version:        ${OLD}/Version:        ${NEW}/" packaging/fedora/sessionintent.spec

# Insert a fresh changelog entry. Rewriting the previous one in place would
# hand the new version the old release's date and description.
NAME=$(git config user.name)
EMAIL=$(git config user.email)
sed -i "/^%changelog$/a\\
* $(LC_ALL=C date '+%a %b %d %Y') ${NAME} <${EMAIL}> - ${NEW}-1\\
- See CHANGELOG.md for details." packaging/fedora/sessionintent.spec

sed -i "s/sessionintent ${OLD}/sessionintent ${NEW}/" man/sessionintent.1
echo "Bumped ${OLD} -> ${NEW}"
echo "Edit the new %changelog entry before tagging."
