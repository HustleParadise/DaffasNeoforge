param(
    [string]$Jar,
    [string]$Name = ''   # необязательно: часть имени класса миксина, если авто-поиск не сработает
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Jar) {
    $found = Get-ChildItem $dir -Filter 'hbm*.jar' |
        Where-Object { $_.Name -notlike '*-fixed.jar' } | Select-Object -First 1
    if (-not $found) { throw "Не найден hbm*.jar рядом со скриптом. Передай путь: fix-hbm.bat путь\к\hbm.jar" }
    $Jar = $found.FullName
}
$out = Join-Path $dir ([IO.Path]::GetFileNameWithoutExtension($Jar) + '-fixed.jar')
Copy-Item $Jar $out -Force
Write-Host "Исходник: $Jar"
Write-Host "Результат: $out"

$utf8 = New-Object Text.UTF8Encoding($false)
$latin1 = [Text.Encoding]::GetEncoding(28591)

function Get-EntryBytes($entry) {
    $s = $entry.Open()
    $ms = New-Object IO.MemoryStream
    $s.CopyTo($ms); $s.Close()
    return ,$ms.ToArray()
}

$zip = [IO.Compression.ZipFile]::Open($out, 'Update')
$totalRemoved = 0
try {
    $jsons = @($zip.Entries | Where-Object { $_.FullName -match '\.mixins\.json$' } | ForEach-Object { $_.FullName })
    foreach ($jsonName in $jsons) {
        $entry = $zip.GetEntry($jsonName)
        $text = $utf8.GetString((Get-EntryBytes $entry))
        if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) { $text = $text.Substring(1) }
        $j = $text | ConvertFrom-Json
        $pkg = [string]$j.package
        $changed = $false

        foreach ($key in 'mixins', 'client', 'server') {
            if (-not $j.PSObject.Properties[$key]) { continue }
            $keep = @()
            foreach ($m in @($j.$key)) {
                $path = (($pkg + '.' + $m) -replace '\.', '/') + '.class'
                $ce = $zip.GetEntry($path)
                $bad = $false
                if ($ce) {
                    $body = $latin1.GetString((Get-EntryBytes $ce))
                    if ($body.Contains('cursorChanged')) { $bad = $true }
                }
                if (-not $bad -and $Name -and ([string]$m).Contains($Name)) { $bad = $true }
                if ($bad) {
                    Write-Host "  [-] $jsonName : убран '$m' (секция $key)"
                    $changed = $true
                    $totalRemoved++
                } else {
                    $keep += $m
                }
            }
            if ($changed) { $j.$key = @($keep) }
        }

        if ($changed) {
            $newText = $j | ConvertTo-Json -Depth 20
            $entry.Delete()
            $ne = $zip.CreateEntry($jsonName)
            $w = $ne.Open()
            $bytes = $utf8.GetBytes($newText)
            $w.Write($bytes, 0, $bytes.Length)
            $w.Close()
        }
    }

    # подписи больше не валидны после правки
    @($zip.Entries | Where-Object { $_.FullName -match '^META-INF/[^/]+\.(SF|RSA|DSA|EC)$' }) |
        ForEach-Object { $_.Delete() }
}
finally {
    $zip.Dispose()
}

if ($totalRemoved -eq 0) {
    Write-Warning "Миксин с cursorChanged не найден. Запусти с именем: fix-hbm.bat -Name AbstractContainerMenu"
} else {
    Write-Host "Готово. Убрано миксинов: $totalRemoved. Положи '$out' в mods/ вместо оригинала."
}
