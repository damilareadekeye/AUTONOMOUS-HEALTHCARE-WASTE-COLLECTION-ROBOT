# Builds main.pdf locally with MiKTeX (pdfLaTeX + BibTeX). Usage: powershell -File build.ps1
# Calls the MiKTeX engine directly (the pdflatex launcher needs a DLL that is missing on this PC).
$bin = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
$env:PATH = $bin + ';' + (($env:PATH -split ';' | ? { $_ -and (Test-Path $_ -PathType Container) }) -join ';')
Set-Location $PSScriptRoot
function Tex { & "$bin\miktex-pdftex.exe" -undump=pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null; $LASTEXITCODE }
$c1 = Tex
& "$bin\miktex-bibtex.exe" main | Select-String -Pattern 'Warning|Error|error' | Select -First 10
$c2 = Tex
$c3 = Tex
"pdfLaTeX exit codes: $c1 $c2 $c3"
$log = Get-Content main.log -Raw
$w = [regex]::Matches($log, '(Overfull|Underfull) \\[hv]box[^\r\n]*').Count
"boxes warnings: $w ; undefined refs/citations:"
Select-String -Path main.log -Pattern 'undefined' | Select -First 8
Select-String -Path main.log -Pattern 'Output written' | Select -First 1
