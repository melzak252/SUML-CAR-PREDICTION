$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir "..\.."
$pyDir = Join-Path $repoRoot "..\python310"
$pyExe = Join-Path $pyDir "python.exe"
$pyVersion = "3.10.11"
$pyZipUrl = "https://www.python.org/ftp/python/$pyVersion/python-$pyVersion-embed-amd64.zip"
$pyZipPath = Join-Path $env:TEMP "python-$pyVersion-embed-amd64.zip"

function Test-Python310 {
    foreach ($cmd in @("py -3.10", "python3.10", "python")) {
        try {
            $parts = $cmd -split ' '
            if ($parts.Length -eq 2) {
                $ver = & $parts[0] $parts[1] --version 2>&1 | Out-String
            } else {
                $ver = & $cmd --version 2>&1 | Out-String
            }
            if ($ver -match "3\.10\.\d+") { return $true }
        } catch { }
    }
    if (Test-Path $pyExe) {
        try {
            $ver = & $pyExe --version 2>&1 | Out-String
            if ($ver -match "3\.10\.\d+") { return $true }
        } catch { }
    }
    return $false
}

if (Test-Python310) {
    Write-Host "Python 3.10 juz zainstalowany."
    exit 0
}

Write-Host "Python 3.10 nie znaleziony. Instalacja..."

if (-not (Test-Path $pyDir)) {
    New-Item -ItemType Directory -Path $pyDir -Force | Out-Null
}

Write-Host "Pobieranie Python $pyVersion (embeddable)..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $pyZipUrl -OutFile $pyZipPath -UseBasicParsing

Write-Host "Wypakowywanie..."
Expand-Archive -Path $pyZipPath -DestinationPath $pyDir -Force
Remove-Item $pyZipPath -Force -ErrorAction SilentlyContinue

$pthFile = Get-ChildItem "$pyDir\*._pth" | Select-Object -First 1
if ($pthFile) {
    $content = Get-Content $pthFile.FullName
    $content = $content | ForEach-Object { $_ -replace '^#?\s*import site', 'import site' }
    if ($content -notcontains 'Lib\site-packages') {
        $content += 'Lib\site-packages'
    }
    Set-Content $pthFile.FullName -Value $content
}

Write-Host "Instalacja pip..."
$getPipPath = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipPath -UseBasicParsing
& $pyExe $getPipPath 2>$null | Out-Null
Remove-Item $getPipPath -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "$pyDir\Scripts\pip.exe")) {
    Write-Host "pip nie zainstalowany"
    exit 1
}

Write-Host "Instalacja virtualenv..."
& $pyExe -m pip install virtualenv 2>$null | Out-Null

if (Test-Python310) {
    Write-Host "Python 3.10 zainstalowany pomyslnie."
} else {
    Write-Host "Nie udalo sie zainstalowac Python 3.10"
    exit 1
}