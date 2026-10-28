<# start-mediamtx.ps1 - Jarvis Recon Kit PKG-1 launcher (SAF GO-WITH-CHANGES 2026-10-28)
 Manual foreground start ONLY. No autostart/service/installs/network changes.
 Exits non-zero unless all secrets are set, not placeholders, and >=24 random chars.
 Loads <project>\.env then laptop-ingest\.env (gitignored). Real env vars win. Values never printed. #>
[CmdletBinding()]
param(
  [string]$MediaMtxExe = 'C:\Jarvis\tools\mediamtx\mediamtx.exe',
  [string]$ConfigPath  = '',
  [string]$LogDir      = 'C:\JarvisData\mediamtx'
)
$ErrorActionPreference = 'Stop'
$here = if($PSScriptRoot){$PSScriptRoot}else{Split-Path -Parent $MyInvocation.MyCommand.Path}
if(-not $ConfigPath){ $ConfigPath = Join-Path $here 'mediamtx.yml' }
$PH = 'CHANGE_VIA_ENV'
function Fail([string]$m,[int]$c=2){ Write-Host "[start-mediamtx] REFUSING TO START: $m" -ForegroundColor Red; exit $c }
function V([string]$k){ [Environment]::GetEnvironmentVariable($k,'Process') }

$root = Split-Path $here -Parent
foreach($f in @((Join-Path $root '.env'),(Join-Path $here '.env'))){
  if(-not (Test-Path -LiteralPath $f)){ continue }
  foreach($line in Get-Content -LiteralPath $f){
    $t=$line.Trim(); if($t -eq '' -or $t.StartsWith('#') -or -not $t.Contains('=')){ continue }
    $k,$v=$t.Split('=',2); $k=$k.Trim(); $v=$v.Trim().Trim('"').Trim("'")
    if($k -match '^(MTX_|JV_)' -and -not (V $k)){ [Environment]::SetEnvironmentVariable($k,$v,'Process') }
  }
  Write-Host "[start-mediamtx] loaded keys from $f (values hidden)"
}

function Weak([string]$s){
  if($s.Length -lt 24){ return 'is shorter than 24 characters' }
  $cl=@('[a-z]','[A-Z]','[0-9]','[^a-zA-Z0-9]') | Where-Object { $s -cmatch $_ }
  if(@($cl).Count -lt 3){ return 'needs 3 of: lower, upper, digit, symbol' }
  if(@($s.ToCharArray() | Sort-Object -Unique -CaseSensitive).Count -lt 12){ return 'has too few distinct characters (not random)' }
  if($s -match '(.)\1{3,}'){ return 'has a run of 4+ identical characters' }
  if($s -match '(?i)password|changeme|change_via_env|jarvis|mediamtx|1234|qwerty'){ return 'contains a dictionary/placeholder word' }
  $null
}
function Check([string]$k,[switch]$Secret){
  $v=V $k
  if([string]::IsNullOrWhiteSpace($v)){ return "$k is not set" }
  if($v -eq $PH){ return "$k is still the placeholder $PH" }
  if($Secret){ $w=Weak $v; if($w){ return "$k $w" } }
  $null
}

$e=@()
foreach($i in 0,1){
  $e += Check "MTX_AUTHINTERNALUSERS_${i}_USER"
  $e += Check "MTX_AUTHINTERNALUSERS_${i}_PASS" -Secret
}
$e += Check 'MTX_PATHS_GLASSES_SRTPUBLISHPASSPHRASE' -Secret
if((V 'MTX_PATHS_GLASSES_SRTPUBLISHPASSPHRASE').Length -gt 79){ $e += 'MTX_PATHS_GLASSES_SRTPUBLISHPASSPHRASE exceeds 79 chars (SRT limit)' }
if((V 'MTX_AUTHINTERNALUSERS_0_USER') -and (V 'MTX_AUTHINTERNALUSERS_0_USER') -eq (V 'MTX_AUTHINTERNALUSERS_1_USER')){ $e += 'publisher and reader usernames must differ' }
if((V 'MTX_AUTHINTERNALUSERS_0_PASS') -and (V 'MTX_AUTHINTERNALUSERS_0_PASS') -eq (V 'MTX_AUTHINTERNALUSERS_1_PASS')){ $e += 'publisher and reader passwords must differ' }

$ips=V 'MTX_AUTHINTERNALUSERS_0_IPS'
if($ips){
  $l=@('100.64.0.0/10') + ($ips.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne '100.64.0.0/10' })
  foreach($x in $l[1..($l.Count)]){ if($x -and $x -notmatch '^(\d{1,3}\.){3}\d{1,3}(/32)?$'){ $e += "MTX_AUTHINTERNALUSERS_0_IPS entry '$x' must be a single host (/32), never a subnet" } }
  [Environment]::SetEnvironmentVariable('MTX_AUTHINTERNALUSERS_0_IPS',($l -join ','),'Process')
}
foreach($k in 'MTX_RTMP','MTX_API','MTX_METRICS','MTX_PPROF','MTX_PLAYBACK','MTX_HLS','MTX_WEBRTCICESERVERS2','MTX_RTSPADDRESS','MTX_LOGLEVEL'){
  if(V $k){ $e += "$k env override not allowed (edit mediamtx.yml + SAF review)" }
}
if(-not (Test-Path -LiteralPath $MediaMtxExe)){ $e += "mediamtx.exe not found at $MediaMtxExe (PKG-1 not installed)" }
if(-not (Test-Path -LiteralPath $ConfigPath)){ $e += "config not found: $ConfigPath" } else {
  $c=Get-Content -LiteralPath $ConfigPath -Raw
  if($c -notmatch '(?m)^webrtcICEServers2:\s*\[\]'){ $e += 'mediamtx.yml must set webrtcICEServers2: []' }
  if($c -notmatch '(?m)^rtspAddress:\s*127\.0\.0\.1:'){ $e += 'mediamtx.yml rtspAddress must be 127.0.0.1' }
  if($c -match '(?m)^\s*record:\s*yes'){ $e += 'mediamtx.yml must not enable recording' }
}
if(-not (Test-Path -LiteralPath $LogDir)){ $e += "log dir $LogDir missing (PKG-12; outside OneDrive/Dropbox)" }
elseif((Resolve-Path -LiteralPath $LogDir).Path -match '(?i)onedrive|dropbox'){ $e += "log dir $LogDir is inside a synced folder" }

$e=@($e | Where-Object { $_ })
if($e.Count){ $e | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }; Fail "$($e.Count) check(s) failed. Fix your gitignored .env (see .env.example). Nothing started." }

Write-Host "[start-mediamtx] checks passed; MediaMTX foreground (Ctrl+C stops). Log: $LogDir\mediamtx.log"
& $MediaMtxExe $ConfigPath
if($LASTEXITCODE -ne 0){ Fail "mediamtx.exe exited $LASTEXITCODE" $LASTEXITCODE }
exit 0

