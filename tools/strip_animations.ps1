# Makes a copy of the deck with no animations and no transitions (the video still plays on a click).
#   powershell -File tools\strip_animations.ps1 <source.pptx> <output.pptx>
param([string]$Src, [string]$Dst)
Copy-Item $Src $Dst -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Dst, $false, $false, $false)
$report = @()
foreach ($sl in $pres.Slides) {
    $seq = $sl.TimeLine.MainSequence
    while ($seq.Count -gt 0) { $seq.Item(1).Delete() }
    $sl.SlideShowTransition.EntryEffect = 0          # ppEffectNone
    $sl.SlideShowTransition.AdvanceOnClick = -1
    foreach ($sh in $sl.Shapes) {
        if ($sh.Type -eq 16) {                       # embedded video: play when clicked
            try { $e = $seq.AddEffect($sh, 83, 0, 1); $report += "slide $($sl.SlideIndex): video play-on-click added ($($sh.Name))" }
            catch { $report += "slide $($sl.SlideIndex): could not add video play effect: $_" }
        }
    }
    $report += "slide $($sl.SlideIndex): animation steps now $($seq.Count)"
}
$pres.Save()
$pres.Close()
$app.Quit()
$report
