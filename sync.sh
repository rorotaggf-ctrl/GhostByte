#!/bin/bash
set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
MSG="${1:-Auto-Sync: basename "$PWD"}"

echo "=========================================="
echo "  Universal Sync: $(basename "$PWD")"
echo "  Branch:         $BRANCH"
echo "=========================================="

# 1. Lokale Änderungen erfassen & committen
git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "$MSG"
else
    echo "Keine neuen lokalen Änderungen zum Committen."
fi

# 2. Vor dem Push: Stand von GitHub holen (Auto-Rebase)
echo "Synchronisiere mit remote ($BRANCH)..."
if ! git pull --rebase origin "$BRANCH"; then
    echo "⚠️  KONFLIKT entdeckt! Breche automatischen Rebase ab..."
    git rebase --abort
    echo "FEHLER: Bitte Konflikte manuell auflösen!"
    exit 1
fi

# 3. Sauber hochpushen
echo "Pushe zu origin/$BRANCH..."
git push origin "$BRANCH"

echo "=========================================="
echo "  Erfolgreich synchronisiert!"
echo "=========================================="