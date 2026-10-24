@echo off
chcp 65001 >nul
set "HBMDIR=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=[IO.File]::ReadAllText('%~f0'); $c=$c.Substring($c.LastIndexOf('#PS'+'#')+4); & ([scriptblock]::Create($c)) %*"
echo.
pause
exit /b
#PS#
param([Parameter(Mandatory=$true)][string]$Jar)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$dir = $env:HBMDIR.TrimEnd([char]92)
$tmp = Join-Path $dir 'hbm-extract'
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null
$latin1 = [Text.Encoding]::GetEncoding(28591)
$zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path $Jar).Path)
$n = 0
try {
    foreach ($e in $zip.Entries) {
        if ($e.FullName.EndsWith('/')) { continue }
        $take = $false
        if ($e.FullName -match '\.mixins\.json$') { $take = $true }
        elseif ($e.FullName.EndsWith('.class') -and $e.Length -lt 2000000) {
            $s = $e.Open(); $ms = New-Object IO.MemoryStream; $s.CopyTo($ms); $s.Close()
            $t = $latin1.GetString($ms.ToArray())
            if ($t.Contains('cursorChanged') -or $t.Contains('fuseOwner')) { $take = $true }
        }
        if ($take) {
            $dest = Join-Path $tmp ($e.FullName -replace '/', '\')
            New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
            [IO.Compression.ZipFileExtensions]::ExtractToFile($e, $dest, $true)
            Write-Host "  + $($e.FullName)"
            $n++
        }
    }
} finally { $zip.Dispose() }
$out = Join-Path $dir 'hbm-extract.zip'
if (Test-Path $out) { Remove-Item $out -Force }
[IO.Compression.ZipFile]::CreateFromDirectory($tmp, $out)
Write-Host "Готово: $n файлов -> $out"
