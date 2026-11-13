# start-router.ps1 — launch the Little Router on Windows.
#
# Sets the router's environment, reads the FreeLLMAPI gateway key at
# runtime from Windows Credential Manager (target FreeLLMAPI/unified)
# via C:\Users\hgx\.freellmapi\Get-GatewayKey.ps1, and starts
# 04-little-router.py in this folder (binds 127.0.0.1:11435).
#
# The key lives in memory only: this script never prints, logs, or
# writes it to disk. If the key cannot be read, the router still
# starts — with no key it sends no Authorization header on the free
# route (the router's previous behaviour), so the free route will get
# "Invalid API key" from the gateway until the key is available.
#
# Assumption: Get-GatewayKey.ps1 outputs the key and nothing else, so
# its output can be captured into a variable. If that script's
# interface differs, this launcher needs the matching read.
#
# Run:  powershell -ExecutionPolicy Bypass -File .\start-router.ps1
# Stop: Ctrl+C in this window.

$ErrorActionPreference = "Stop"

# --- environment (matches the router's new defaults) ---
$env:ROUTER_PORT    = "11435"
$env:OLLAMA_URL     = "http://127.0.0.1:11434"
$env:RESIDENT_MODEL = "qwen3-4b-rea:latest"
$env:HEAVY_MODEL    = "gemma3-27b-rea:latest"
$env:FREELLM_MODEL  = "auto"
$env:FREELLM_URL    = "http://127.0.0.1:3001"

# --- gateway key, read at runtime, in memory only ---
$env:FREELLM_API_KEY = ""
$KeyScript = "C:\Users\hgx\.freellmapi\Get-GatewayKey.ps1"
if (Test-Path $KeyScript) {
    try {
        $key = (& $KeyScript | Out-String).Trim()
        if ($key) {
            $env:FREELLM_API_KEY = $key
        } else {
            Write-Warning "Get-GatewayKey.ps1 returned nothing; router starts without a gateway key."
        }
    } catch {
        Write-Warning "Could not read the FreeLLMAPI key; router starts without it."
    } finally {
        if (Test-Path variable:key) { Remove-Variable key -ErrorAction SilentlyContinue }
    }
} else {
    Write-Warning "Key script not found at $KeyScript; router starts without a gateway key."
}

# --- start the router (this folder, whatever the caller's cwd is) ---
$RouterScript = Join-Path $PSScriptRoot "04-little-router.py"
if (Get-Command python -ErrorAction SilentlyContinue) {
    python $RouterScript
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 $RouterScript
} else {
    Write-Error "No Python found (python / py). Install Python 3 and retry."
    exit 1
}
