$ProgressPreference = 'SilentlyContinue'
$baseUrl = "https://raw.githubusercontent.com/zhengxixuan/CharlieMungerTalk/master/Letters"
$destDir = "C:\Users\steve\nothing to add project\data\letters\wesco_letters"

Write-Host "Downloading Charlie Munger's Wesco Financial Letters..."
Write-Host ""

# Get list of all PDF files
$files = @(
    "001-1997-letters.pdf",
    "002-1998-letters.pdf",
    "003-1999-letters.pdf",
    "004-2000-letters.pdf",
    "005-2001-letters.pdf",
    "006-2002-letters.pdf",
    "007-2003-letters.pdf",
    "008-2004-letters.pdf",
    "009-2005-letters.pdf",
    "010-2006-letters.pdf",
    "011-2007-letters.pdf",
    "012-2008-letters.pdf",
    "013-2009-letters.pdf",
    "014-2010-letters.pdf",
    "015-2011-letters.pdf",
    "016-2012-letters.pdf",
    "017-2013-letters.pdf",
    "018-2014-letters.pdf",
    "019-2015-letters.pdf",
    "020-2016-letters.pdf",
    "021-2017-letters.pdf",
    "022-2018-letters.pdf",
    "023-2019-letters.pdf",
    "024-2020-letters.pdf",
    "025-2021-letters.pdf",
    "026-2022-letters.pdf"
)

$successCount = 0
$failedCount = 0

foreach ($file in $files) {
    $year = $file -replace "-letters.pdf", "" -replace "^\d+-", ""
    Write-Host "Downloading $year... " -NoNewline

    try {
        $url = "$baseUrl/$file"
        $destPath = Join-Path $destDir $file

        Invoke-WebRequest -Uri $url -OutFile $destPath -ErrorAction Stop
        $fileSize = [math]::Round((Get-Item $destPath).Length / 1KB, 2)
        Write-Host "[OK] ${fileSize}KB" -ForegroundColor Green
        $successCount++

        Start-Sleep -Milliseconds 200
    }
    catch {
        Write-Host "[FAILED]" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host ""
Write-Host "Download completed!"
Write-Host "Success: $successCount/$($files.Count)"
Write-Host "Failed: $failedCount/$($files.Count)"
