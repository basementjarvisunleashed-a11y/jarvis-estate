<# sync-preflight.ps1 - REQUIRED before every OneDrive/Dropbox mirror of watch-offgrid.
 Lists files eligible to mirror (code+docs only, sync-exclude.txt applied) and secret-scans them.
 Exit 0 = clean (prints the file list). Exit 3 = possible secret found -> DO NOT SYNC. Read-only. #>
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ex = Get-Content (Join-Path $root 'sync-exclude.txt') | Where-Object { $_ -and -not $_.StartsWith('#') }
$files = Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
  $rel = $_.FullName.Substring($root.Length+1); $parts = $rel -split '\\'
  ($_.Name -eq '.env.example') -or -not ($ex | Where-Object { $p=$_; ($parts | Where-Object { $_ -like $p }) })
}
$pat = @(
  '(?i)(api[_-]?key|secret|token|passphrase|_PASS)\s*[=:]\s*[''"]?(?!CHANGE_VIA_ENV)[A-Za-z0-9_\-+/=!#%]{12,}',
  'AKIA[0-9A-Z]{16}','ghp_[A-Za-z0-9]{30,}','glpat-[A-Za-z0-9_\-]{20,}','sk-[A-Za-z0-9]{20,}','xox[bpas]-[A-Za-z0-9-]{10,}',
  '-----BEGIN [A-Z ]*PRIVATE KEY-----','tskey-[A-Za-z0-9-]{10,}','(?<![\d.])(10|192\.168)\.\d{1,3}\.\d{1,3}(?![\d.]|/)'
)
$hits = foreach($f in $files){ foreach($p in $pat){ Select-String -LiteralPath $f.FullName -Pattern $p -AllMatches -ErrorAction SilentlyContinue | ForEach-Object { "$($f.FullName.Substring($root.Length+1)):$($_.LineNumber) matches /$p/" } } }
if($hits){ Write-Host 'SECRET SCAN FAILED - DO NOT SYNC:' -ForegroundColor Red; $hits | Sort-Object -Unique; exit 3 }
Write-Host "Secret scan clean. $(@($files).Count) files eligible to mirror:" -ForegroundColor Green
$files | ForEach-Object { $_.FullName.Substring($root.Length+1) }
exit 0


