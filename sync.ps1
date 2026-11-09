param(
    [string]$msg = "Auto-Sync: gravity-matrix Update"
)

$ErrorActionPreference = "Stop"

$branch = git rev-parse --abbrev-ref HEAD 2>$null
if (-not $branch) {
    $branch = "main"
}

$dirName = Split-Path -Leaf (Get-Location)

Write-Host "=========================================="
Write-Host "  Universal Sync: $dirName"
Write-Host "  Branch:         $branch"
Write-Host "=========================================="

git add .
git diff-index --quiet HEAD -- 2>$null
if ($LASTEXITCODE -ne 0) {
    git commit -m "$msg"
}
else {
    Write-Host "Keine neuen lokalen Aenderungen zum Committen."
}

Write-Host "Synchronisiere mit remote ($branch)..."
git pull --rebase origin "$branch"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNUNG] KONFLIKT entdeckt! Breche Rebase ab..." -ForegroundColor Yellow
    git rebase --abort
    Write-Host "[FEHLER] Bitte Konflikte manuell aufloesen!" -ForegroundColor Red
    exit 1
}

Write-Host "Pushe zu origin/$branch..."
git push origin "$branch"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FEHLER] Fehler beim Pushen!" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================="
Write-Host "  Erfolgreich synchronisiert!"
Write-Host "=========================================="