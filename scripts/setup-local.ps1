# setup-local.ps1 — One-click local install for the job-apply skill (Path A)
# 本地模式一键安装脚本（路径 A：本地桥）
#
# What it does (it does these for you, in order):
#   1. Installs Python 3.12 (only if missing) — current user only, no admin needed.
#   2. Installs the `websockets` package.
#   3. Downloads Antigravity Browser Bridge v1.4.1 and extracts it.
#   4. Creates start-bridge.bat to launch the bridge server.
#   5. Starts the bridge and checks it answers on 127.0.0.1:9224.
#
# What it does NOT do (you do these by hand, once):
#   - Load the browser extension (Chrome: chrome://extensions -> Developer mode
#     -> "Load unpacked" -> pick the `extension` folder). The script tells you
#     exactly which folder.
#   - Log in to the four job sites in your own browser.
#   - Fill in criteria.yaml (your AI will ask you and write it).
#
# After this script, the remaining manual steps are: load extension, log in to
# the 4 sites, let the AI write criteria.yaml. That is the whole install.
#
# Run: right-click -> "Run with PowerShell", or from PowerShell:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-local.ps1
#
# This script is for the LOCAL path only (Path A). It installs nothing that
# talks to the network except the bridge itself on 127.0.0.1. No Tailscale,
# no SSH, no port forwarding. If you need the remote path (Path B, cloud
# agent), see references/bridge.md Option 1.

$ErrorActionPreference = 'Stop'

$PythonVersion = '3.12.7'
$PythonUrls = @(
    "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe",
    "https://mirrors.huaweicloud.com/python/$PythonVersion/python-$PythonVersion-amd64.exe"
)
$PipMirror = 'https://pypi.tuna.tsinghua.edu.cn/simple'
$BridgeTag = 'v1.4.1'
# Pinned to the audited commit 60c4c05 (v1.4.1 + two daemon fixes; see
# references/bridge.md). Tags can be moved; a commit cannot.
$BridgeCommit = '60c4c05a81a2bf02f739e53b000de76e7da9a1cc'
$BridgeZipUrl = "https://github.com/AshenJyy/browser-bridge/archive/$BridgeCommit.zip"
$BridgeDir = Join-Path $env:USERPROFILE 'antigravity-browser-bridge'
$TmpDir = Join-Path $env:TEMP 'job-apply-setup'

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg) { Write-Host "    OK: $msg" -ForegroundColor Green }
function Note($msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# ---------- 1. Python ----------
Step '1/5  Checking Python / 检查 Python'
function Find-RealPython {
    # The WindowsApps "python.exe" is a Microsoft Store stub, not Python.
    foreach ($c in @(Get-Command python -All -ErrorAction SilentlyContinue)) {
        if ($c.Source -like '*\WindowsApps\*') { continue }
        try {
            $v = & $c.Source --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$v" -match 'Python 3') { return $c.Source }
        } catch { }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        try {
            $exe = (& $py.Source -3 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1)
            if ($LASTEXITCODE -eq 0 -and $exe -and (Test-Path $exe)) { return $exe.Trim() }
        } catch { }
    }
    return $null
}

$Py = Find-RealPython
if ($Py) {
    Ok "Python found: $(& $Py --version 2>&1)  ($Py)"
} else {
    Note 'Python not found (the WindowsApps "python" stub does not count). Downloading Python 3.12.7 ... / 未找到可用的 Python，正在下载…'
    New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null
    $installer = Join-Path $TmpDir "python-$PythonVersion-amd64.exe"
    $got = $false
    foreach ($u in $PythonUrls) {
        try { Invoke-WebRequest -Uri $u -OutFile $installer -UseBasicParsing; $got = $true; break }
        catch { Note "Download failed from $u, trying the next source... / 下载失败，换下一个源…" }
    }
    if (-not $got) { throw 'Could not download Python. Install Python 3 by hand from python.org, then rerun. / 无法下载 Python，请手动安装后重新运行。' }
    Note 'Installing Python (current user only, no admin needed) ... / 正在安装 Python（仅当前用户，无需管理员）…'
    Start-Process -FilePath $installer -ArgumentList '/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_test=0', 'Include_launcher=1' -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $Py = Find-RealPython
    if (-not $Py) {
        $guess = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
        if (Test-Path $guess) { $Py = $guess }
    }
    if (-not $Py) { throw 'Python was installed but cannot be found. Close this window, open a new PowerShell and rerun. / Python 已安装但找不到，请重新打开 PowerShell 再运行。' }
    Ok "Python installed: $(& $Py --version 2>&1)  ($Py)"
}
Note 'Tip: turn off Settings > Apps > Advanced app settings > App execution aliases > python.exe / python3.exe, so every AI tool finds this Python. / 建议在「应用执行别名」里关掉 python.exe 和 python3.exe。'

# ---------- 2. websockets ----------
Step '2/5  Installing websockets / 安装 websockets'
& $Py -m pip install --quiet --upgrade websockets
if ($LASTEXITCODE -ne 0) {
    Note "Retrying with a mirror ($PipMirror) ... / 换国内镜像重试…"
    & $Py -m pip install --quiet --upgrade websockets -i $PipMirror
}
if ($LASTEXITCODE -ne 0) { throw 'pip install websockets failed. Check your network and rerun. / 安装 websockets 失败，请检查网络后重新运行。' }
Ok 'websockets installed'

# ---------- 3. Bridge ----------
Step '3/5  Downloading the bridge (v1.4.1) / 下载 bridge'
if (Test-Path (Join-Path $BridgeDir 'server\server.py')) {
    Ok "Bridge already present at $BridgeDir — skipping download. / bridge 已存在，跳过下载。"
} else {
    New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null
    $zip = Join-Path $TmpDir 'browser-bridge-1.4.1.zip'
    try { Invoke-WebRequest -Uri $BridgeZipUrl -OutFile $zip -UseBasicParsing }
    catch { throw "Could not download the bridge from GitHub (it may be blocked on your network). Download it by hand: https://github.com/AshenJyy/browser-bridge/releases/tag/v1.4.1 , unzip to $BridgeDir and rerun. / 无法从 GitHub 下载 bridge，请手动下载解压到 $BridgeDir 后重新运行。" }
    $extract = Join-Path $TmpDir 'bridge-extract'
    if (Test-Path $extract) { Remove-Item -Recurse -Force $extract }
    Expand-Archive -Path $zip -DestinationPath $extract -Force
    $inner = Get-ChildItem -Directory $extract | Select-Object -First 1
    if (Test-Path $BridgeDir) { Remove-Item -Recurse -Force $BridgeDir }
    Move-Item -Path $inner.FullName -Destination $BridgeDir
    Ok "Bridge extracted to $BridgeDir"
}
if (-not (Test-Path (Join-Path $BridgeDir 'server\server.py'))) {
    throw "Bridge download looked OK but server\server.py is missing under $BridgeDir. Please download it by hand from https://github.com/AshenJyy/browser-bridge/releases/tag/v1.4.1"
}

# ---------- 4. start-bridge.bat ----------
Step '4/5  Creating start-bridge.bat / 创建启动脚本'
$bat = Join-Path $BridgeDir 'start-bridge.bat'
@"
@echo off
REM Double-click to start the bridge. Keep this window open while the agent works.
cd /d "%~dp0server"
"$Py" server.py
pause
"@ | Set-Content -Path $bat -Encoding ASCII
Ok "Created $bat"

# ---------- 5. Start the bridge and check health ----------
Step '5/5  Starting the bridge / 启动 bridge'
$running = Get-NetTCPConnection -LocalPort 9224 -State Listen -ErrorAction SilentlyContinue
if ($running) {
    Ok 'Bridge is already listening on 127.0.0.1:9224. / bridge 已在运行。'
} else {
    Start-Process -FilePath $Py -ArgumentList 'server.py' -WorkingDirectory (Join-Path $BridgeDir 'server')
    Start-Sleep -Seconds 4
}
try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:9224/health' -TimeoutSec 5
    Ok "Bridge answers on 127.0.0.1:9224 (extension_connected=$($health.extension_connected))"
} catch {
    throw 'Bridge server did not answer on 127.0.0.1:9224. Try double-clicking start-bridge.bat by hand and check the window for errors. / bridge 未响应，请手动双击 start-bridge.bat 查看窗口报错。'
}

Write-Host ''
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host 'Done. Two manual steps left (once only): / 还剩两步手动操作（只需做一次）：' -ForegroundColor Cyan
Write-Host ''
Write-Host "  1. Load the extension: open chrome://extensions (Edge: edge://extensions),"
Write-Host '     enable Developer mode, click "Load unpacked" and pick this folder:'
Write-Host "       $BridgeDir\extension"
Write-Host '     加载扩展：打开 chrome://extensions，开启开发者模式，点"加载解压缩的扩展"，选上面这个 extension 文件夹。'
Write-Host ''
Write-Host '  2. Log in to the four job sites in your own browser (BOSS, Liepin, 51job, Zhaopin),'
Write-Host "     then let your AI write criteria.yaml and run:  `"$Py`" scripts/selftest.py"
Write-Host '     在你自己的浏览器里登录四个招聘网站，然后让 AI 帮你填 criteria.yaml，再跑自检：python scripts/selftest.py'
Write-Host ''
Write-Host 'To stop the bridge later, close its window. / 用完关闭 bridge 窗口即可停止。'
Write-Host '============================================================' -ForegroundColor Cyan
