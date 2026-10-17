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
sed -i "s/${OLD}-1/${NEW}-1/g" packaging/fedora/sessionintent.spec
sed -i "s/sessionintent ${OLD}/sessionintent ${NEW}/" man/sessionintent.1
echo "Bumped ${OLD} -> ${NEW}"
