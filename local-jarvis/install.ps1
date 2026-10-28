#Requires -Version 5.1
<#
.SYNOPSIS
    Idempotent Local Jarvis setup for Windows 10/11.

.DESCRIPTION
    Checks prerequisites, creates C:\Jarvis\venv when it is missing,
    pip-installs both requirements files, copies package files into
    C:\Jarvis when those filenames are not already there, and prints
    the next steps.

    This script does not remove files or directories. It does not write
    secrets. It does not register scheduled tasks unless -RegisterTasks
    is passed, and then only the two task XML files copied to
    C:\Jarvis\tasks. The voice loop is never registered.

.PARAMETER RegisterTasks
    Register C:\Jarvis\tasks\orchestrator.xml and voicemeeter.xml for
    the current user. Refuses while the user, SID, or path placeholders
    are still in those files.
#>
[CmdletBinding()]
param(
    [switch]$RegisterTasks
)

$ErrorActionPreference = "Continue"

if ($env:OS -ne "Windows_NT") {
    Write-Host "install.ps1 targets Windows 10/11. Run it on the PC that will host Local Jarvis."
    exit 1
}

$Root = $PSScriptRoot
$JarvisHome = "C:\Jarvis"
$VenvPython = Join-Path $JarvisHome "venv\Scripts\python.exe"
$VoiceRequirements = Join-Path $Root "requirements-voice.txt"
$OrchestratorRequirements = Join-Path $Root "requirements-orchestrator.txt"

$PackageFiles = @(
    "enroll.py",
    "jarvis.py",
    "jarvis_voice.py",
    "orchestrator.py",
    "voice_gate.py",
    "voice_gate.json",
    "jarvis.cmd",
    "jarvis_voice.cmd",
    "vlc_remote.cmd",
    "requirements-orchestrator.txt",
    "requirements-voice.txt",
    ".env.example",
    "README.md"
)

$TaskFiles = [System.Collections.Generic.List[object]]::new()
$TaskFiles.Add([pscustomobject]@{
    Name     = "Jarvis - Orchestrator 8080"
    Relative = "tasks\orchestrator.xml"
}) | Out-Null
$TaskFiles.Add([pscustomobject]@{
    Name     = "Jarvis - VoiceMeeter Banana"
    Relative = "tasks\voicemeeter.xml"
}) | Out-Null

$Placeholders = @("CHANGE_ME_USER_SID", "<user>", "<COMPUTER>", "CHANGE_ME")

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "== $Message"
}

function Test-Python313 {
    & py -3.13 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"
    return ($LASTEXITCODE -eq 0)
}

function Get-EnvState([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = [Environment]::GetEnvironmentVariable($Name, "User")
    }
    if ([string]::IsNullOrWhiteSpace($value)) { return "unset" }
    if ($value -eq "CHANGE_ME") { return "placeholder" }
    return "set"
}

function Copy-PackageFile([string]$Name) {
    $source = Join-Path $Root $Name
    $destination = Join-Path $JarvisHome $Name
    if (-not (Test-Path -LiteralPath $source)) {
        Write-Host "missing source $source"
        return
    }
    if (Test-Path -LiteralPath $destination) {
        Write-Host "present  $destination"
        return
    }
    Copy-Item -LiteralPath $source -Destination $destination
    Write-Host "copied   $destination"
}

function Read-TaskText([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 2 -and $bytes[0] -eq 255 -and $bytes[1] -eq 254) {
        return [System.Text.Encoding]::Unicode.GetString($bytes, 2, $bytes.Length - 2)
    }
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
        return [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
    }
    return [System.Text.Encoding]::UTF8.GetString($bytes)
}

function Get-TaskPlaceholderHits([string]$Text) {
    $hits = @()
    foreach ($needle in $Placeholders) {
        if ($Text.Contains($needle)) { $hits += $needle }
    }
    return ,$hits
}

$notes = [System.Collections.Generic.List[string]]::new()
$hardFail = $false

Write-Step "Prerequisites"

if (Test-Python313) {
    Write-Host "Python 3.13: found (py -3.13)"
} else {
    Write-Host "Python 3.13: NOT FOUND"
    $notes.Add("Install Python 3.13 from https://www.python.org/downloads/ and include the py launcher. Then re-run this script.") | Out-Null
    $hardFail = $true
}

$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidia) {
    Write-Host "NVIDIA driver: nvidia-smi is on PATH (this build was tested on an RTX 2060 6GB)."
} else {
    Write-Host "NVIDIA driver: nvidia-smi was not found."
    $notes.Add("nvidia-smi was not found. Whisper still runs on CPU. Install a current NVIDIA driver if this PC has an NVIDIA GPU.") | Out-Null
}

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Host "Ollama: NOT FOUND"
    $notes.Add("Install Ollama from https://ollama.com/download and then run: ollama pull qwen3:8b") | Out-Null
    $notes.Add("Also pull the model jarvis.py uses: ollama pull qwen2.5:3b") | Out-Null
} else {
    Write-Host "Ollama: found"
    $listed = & ollama list 2>&1 | Out-String
    if ($listed -notmatch "qwen3:8b") {
        Write-Host "Ollama model qwen3:8b: missing"
        $notes.Add("Pull the orchestrator model: ollama pull qwen3:8b") | Out-Null
    } else {
        Write-Host "Ollama model qwen3:8b: present"
    }
    if ($listed -notmatch "qwen2\.5:3b") {
        Write-Host "Ollama model qwen2.5:3b: missing"
        $notes.Add("Pull the jarvis.py model: ollama pull qwen2.5:3b") | Out-Null
    } else {
        Write-Host "Ollama model qwen2.5:3b: present"
    }
}

$vlc = "C:\Program Files\VideoLAN\VLC\vlc.exe"
if (Test-Path -LiteralPath $vlc) {
    Write-Host "VLC: found"
    $notes.Add("In VLC, enable the Web interface and set the Lua HTTP password in Preferences. Start it with C:\Jarvis\vlc_remote.cmd so the remote is localhost:8090. Put that same password in VLC_HTTP_PASSWORD.") | Out-Null
} else {
    Write-Host "VLC: not found at $vlc"
    $notes.Add("Install VLC from https://www.videolan.org/ . Enable the Web interface, set the Lua HTTP password in Preferences, and start C:\Jarvis\vlc_remote.cmd (localhost:8090).") | Out-Null
}

$voice = "C:\Jarvis\voices\en_GB-alan-medium.onnx"
$voiceJson = "C:\Jarvis\voices\en_GB-alan-medium.onnx.json"
if ((Test-Path -LiteralPath $voice) -and (Test-Path -LiteralPath $voiceJson)) {
    Write-Host "Piper voice: found"
} else {
    Write-Host "Piper voice: not in C:\Jarvis\voices yet"
    $notes.Add("Download the Piper voice en_GB-alan-medium into C:\Jarvis\voices (both the .onnx and the .onnx.json). See local-jarvis\README.md.") | Out-Null
}

$voicemeeter = "C:\Program Files (x86)\VB\Voicemeeter\voicemeeterpro.exe"
if (Test-Path -LiteralPath $voicemeeter) {
    Write-Host "VoiceMeeter Banana: found (optional)"
} else {
    Write-Host "VoiceMeeter Banana: not installed (optional)"
    $notes.Add("VoiceMeeter Banana is optional. The logon task expects $voicemeeter.") | Out-Null
}

$npx = "C:\Program Files\nodejs\npx.cmd"
if (Test-Path -LiteralPath $npx) {
    Write-Host "Node.js: found (optional, used by REA)"
} else {
    Write-Host "Node.js: not installed (optional)"
    $notes.Add("Node.js is optional. REA calls C:\Program Files\nodejs\npx.cmd to run rea-agents@6.8.0. Install Node from https://nodejs.org/ if you want that tool.") | Out-Null
}

foreach ($name in @("VLC_HTTP_PASSWORD", "JARVIS_OPERATOR_NAME", "JARVIS_MODEL", "JARVIS_WHISPER_DEVICE", "XAI_API_KEY")) {
    $state = Get-EnvState $name
    Write-Host "env ${name}: $state"
}
if ((Get-EnvState "VLC_HTTP_PASSWORD") -ne "set") {
    $notes.Add("Set VLC_HTTP_PASSWORD to the VLC Lua HTTP password. The example value CHANGE_ME is a placeholder. This script does not store it.") | Out-Null
}
if ((Get-EnvState "XAI_API_KEY") -eq "unset") {
    $notes.Add("XAI_API_KEY is optional. Leave it unset to keep the canned DEMO brief.") | Out-Null
}

if ($hardFail) {
    Write-Step "Next steps"
    foreach ($line in $notes) { Write-Host "- $line" }
    exit 1
}

Write-Step "C:\Jarvis layout"
if (-not (Test-Path -LiteralPath $JarvisHome)) {
    New-Item -ItemType Directory -Path $JarvisHome | Out-Null
    Write-Host "created  $JarvisHome"
} else {
    Write-Host "present  $JarvisHome"
}
foreach ($dir in @("voices", "out")) {
    $path = Join-Path $JarvisHome $dir
    if (-not (Test-Path -LiteralPath $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "created  $path"
    } else {
        Write-Host "present  $path"
    }
}
foreach ($name in $PackageFiles) {
    Copy-PackageFile $name
}
$taskDir = Join-Path $JarvisHome "tasks"
if (-not (Test-Path -LiteralPath $taskDir)) {
    New-Item -ItemType Directory -Path $taskDir | Out-Null
    Write-Host "created  $taskDir"
}
foreach ($task in $TaskFiles) {
    $source = Join-Path $Root $task.Relative
    $leaf = Split-Path -Leaf $task.Relative
    $destination = Join-Path $taskDir $leaf
    if (-not (Test-Path -LiteralPath $source)) {
        Write-Host "missing source $source"
        continue
    }
    if (Test-Path -LiteralPath $destination) {
        Write-Host "present  $destination"
    } else {
        Copy-Item -LiteralPath $source -Destination $destination
        Write-Host "copied   $destination"
    }
}

Write-Step "Virtual environment"
if (Test-Path -LiteralPath $VenvPython) {
    Write-Host "present  $VenvPython"
} else {
    & py -3.13 -m venv $JarvisHome\venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $VenvPython)) {
        Write-Host "Could not create $VenvPython"
        exit 1
    }
    Write-Host "created  $VenvPython"
}

Write-Step "Python packages"
Write-Host "requirements-voice.txt -> $VenvPython"
& $VenvPython -m pip install -r $VoiceRequirements
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip failed for requirements-voice.txt"
    exit 1
}
Write-Host "requirements-orchestrator.txt -> $VenvPython"
& $VenvPython -m pip install -r $OrchestratorRequirements
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip failed for requirements-orchestrator.txt inside the venv"
    exit 1
}
Write-Host "requirements-orchestrator.txt -> py -3.13 (voice gate and enroll.py)"
& py -3.13 -m pip install --user -r $OrchestratorRequirements
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip failed for requirements-orchestrator.txt on system Python 3.13"
    exit 1
}

$gateCopy = Join-Path $JarvisHome "voice_gate.py"
$loopCopy = Join-Path $JarvisHome "jarvis_voice.py"
if ((Test-Path -LiteralPath $gateCopy) -and (Select-String -LiteralPath $gateCopy -Pattern "<user>" -Quiet -SimpleMatch)) {
    $notes.Add("Edit C:\Jarvis\voice_gate.py and replace C:\Users\<user> with your user profile so profiles.json resolves under your Downloads folder.") | Out-Null
}
if ((Test-Path -LiteralPath $loopCopy) -and (Select-String -LiteralPath $loopCopy -Pattern "<user>" -Quiet -SimpleMatch)) {
    $notes.Add("Edit C:\Jarvis\jarvis_voice.py so GATE_PY is the Python 3.13 executable that has SpeechBrain (py -3.13 -c `"import sys; print(sys.executable)`").") | Out-Null
}
$jarvisCopy = Join-Path $JarvisHome "jarvis.py"
if (Test-Path -LiteralPath $jarvisCopy) {
    $notes.Add("jarvis.py listens and speaks on the Maono device names from the reference laptop. Change MIC and SPK in C:\Jarvis\jarvis.py to the Windows sound-device names on this PC.") | Out-Null
}

if ($RegisterTasks) {
    Write-Step "Scheduled tasks"
    $loaded = [System.Collections.Generic.List[object]]::new()
    $blocked = $false
    foreach ($task in $TaskFiles) {
        $leaf = Split-Path -Leaf $task.Relative
        $path = Join-Path (Join-Path $JarvisHome "tasks") $leaf
        if (-not (Test-Path -LiteralPath $path)) {
            Write-Host "missing $path"
            $blocked = $true
            continue
        }
        $text = Read-TaskText $path
        $hits = Get-TaskPlaceholderHits $text
        if ($hits.Count -gt 0) {
            Write-Host "refusing $($task.Name): $path still contains $($hits -join ', ')"
            $blocked = $true
            continue
        }
        $loaded.Add([pscustomobject]@{
            Name = $task.Name
            Xml  = $text.Replace('encoding="UTF-16"', 'encoding="UTF-8"')
        }) | Out-Null
    }
    if ($blocked) {
        Write-Host "No scheduled task was registered. Edit the <user>, SID, and path placeholders in C:\Jarvis\tasks first."
        Write-Host "The voice loop was not registered."
        exit 1
    }
    Import-Module ScheduledTasks
    foreach ($task in $loaded) {
        try {
            Register-ScheduledTask -TaskName $task.Name -Xml $task.Xml -Force -ErrorAction Stop | Out-Null
            Write-Host "registered $($task.Name)"
        } catch {
            Write-Host "Register-ScheduledTask failed for $($task.Name): $($_.Exception.Message)"
            Write-Host "No files were removed."
            exit 1
        }
    }
    Write-Host "The voice loop is not a scheduled task. Start it with C:\Jarvis\jarvis_voice.cmd when you want it."
} else {
    $notes.Add("Logon tasks stay unregistered. Edit the <user>, SID, and path placeholders in C:\Jarvis\tasks (the git copies stay generic), then re-run: powershell -ExecutionPolicy Bypass -File .\install.ps1 -RegisterTasks") | Out-Null
    $notes.Add("The voice loop is deliberately not auto-started.") | Out-Null
}

Write-Step "Next steps"
$notes.Add("Enroll from your Downloads folder (5 takes): py -3.13 C:\Jarvis\enroll.py") | Out-Null
$notes.Add("Check the enrollment: py -3.13 C:\Jarvis\enroll.py --verify") | Out-Null
$notes.Add("The voice gate starts at 0.45 and is UNCALIBRATED. Score a quiet take, an across-the-room take, and an unknown voice before you trust that number.") | Out-Null
$notes.Add("Start the orchestrator: py -3.13 C:\Jarvis\orchestrator.py") | Out-Null
$notes.Add("Test one file: C:\Jarvis\jarvis_voice.cmd test file.wav") | Out-Null
$notes.Add("Then the live loop: C:\Jarvis\jarvis_voice.cmd loop 5") | Out-Null
foreach ($line in $notes) { Write-Host "- $line" }
Write-Host ""
Write-Host "Done. Re-running this script skips C:\Jarvis files that already exist and pip-installs the pinned requirements again."
exit 0
