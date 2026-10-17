#!/usr/bin/env bash
# Bump SessionIntent version across all packaging files.
# Usage: ./scripts/bump-version.sh 0.4.5
set -euo pipefail
NEW="${1:?usage: $0 <version>}"
OLD=$(grep -oP '__version__ = "\K[^"]+' src/sessionintent/__init__.py)

sed -i "s/__version__ = \"${OLD}\"/__version__ = \"${NEW}\"/" src/sessionintent/__init__.py
sed -i "s/^Version:        ${OLD}/Version:        ${NEW}/" packaging/fedora/sessionintent.spec
sed -i "s/${OLD}-1/${NEW}-1/g" packaging/fedora/sessionintent.spec
sed -i "s/^pkgver=${OLD}/pkgver=${NEW}/" packaging/arch/PKGBUILD
sed -i "s/tag: v${OLD}/tag: v${NEW}/" packaging/flatpak/io.github.fazrigading.SessionIntent.yml
sed -i "s/sessionintent ${OLD}/sessionintent ${NEW}/" man/sessionintent.1
echo "Bumped ${OLD} -> ${NEW}"
