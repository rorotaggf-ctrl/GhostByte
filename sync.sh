#!/bin/bash
set -e

# 1. Namen des aktuellen Projektordners holen
PROJ_NAME=$(basename "$PWD")

# 2. Saubere Branch-Ermittlung (immer einzeilig)
BRANCH=$(git branch --show-current 2>/dev/null | tr -d '\r\n')
if [ -z "$BRANCH" ] || [ "$BRANCH" = "HEAD" ]; then
    BRANCH="main"
fi

MSG="${1:-Auto-Sync: $PROJ_NAME Update}"

echo "=========================================="
echo "  Universal Sync: $PROJ_NAME"
echo "  Branch:         $BRANCH"
echo "=========================================="

# 3. Änderungen stagen
git add .

# 4. Lokale Änderungen committen (falls vorhanden)
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    git commit -m "$MSG"
else
    echo "Keine neuen lokalen Änderungen zum Committen."
fi

# 5. Remote-Prüfung: Gibt es 'origin'?
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  Kein Remote 'origin' gefunden! Bitte zuerst 'git remote add origin ...' ausführen."
    exit 1
fi

# 6. Prüfen, ob der Branch auf GitHub schon existiert
REMOTE_EXISTS=$(git ls-remote --heads origin "$BRANCH" 2>/dev/null || true)

if [ -n "$REMOTE_EXISTS" ]; then
    echo "Synchronisiere mit remote ($BRANCH)..."
    if ! git pull --rebase origin "$BRANCH"; then
        echo "⚠️  KONFLIKT entdeckt! Breche automatischen Rebase ab..."
        git rebase --abort 2>/dev/null || true
        echo "FEHLER: Bitte Konflikte manuell auflösen!"
        exit 1
    fi
    echo "Pushe zu origin/$BRANCH..."
    git push origin "$BRANCH"
else
    echo "Erster Push für Branch '$BRANCH' zu origin..."
    git push -u origin "$BRANCH"
fi

echo "=========================================="
echo "  Erfolgreich synchronisiert!"
echo "=========================================="