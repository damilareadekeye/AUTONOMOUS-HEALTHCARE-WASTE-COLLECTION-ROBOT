# Adds slide transitions and entrance animations to the deck, using PowerPoint itself (so the file stays valid).
#   powershell -File tools\animate_slides.ps1 <path-to-pptx>
# Shapes named "aNN_<effect>" (made by make_slides.py) are animated in order of NN: effect = wipe | fade | fly | zoom | wipeP.
# wipeP animates a text box paragraph by paragraph (lines of a headline appear one after another).
# Every step runs automatically after the previous one (no extra clicks); only the video waits for a click to play.
param([string]$Path)
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Path, $false, $false, $false)
$ids = @{ wipe = 22; fade = 10; fly = 2; zoom = 53; wipeP = 22 }
$report = @()
foreach ($sl in $pres.Slides) {
    try { $sl.SlideShowTransition.EntryEffect = 3849; $sl.SlideShowTransition.Duration = 0.6 } catch { $report += "transition failed on slide $($sl.SlideIndex): $_" }
    $seq = $sl.TimeLine.MainSequence
    while ($seq.Count -gt 0) { $seq.Item(1).Delete() }
    $shapes = @($sl.Shapes | ? { $_.Name -match '^a\d\d_' } | sort Name)
    foreach ($sh in $shapes) {
        $kind = $sh.Name.Substring(4)
        $level = 0; if ($kind -eq 'wipeP') { $level = 2 }
        try {
            $e = $seq.AddEffect($sh, $ids[$kind], $level, 3)
            if ($kind -eq 'wipe' -or $kind -eq 'wipeP') { try { $e.EffectParameters.Direction = 4 } catch {} }
            if ($kind -eq 'fly') { try { $e.EffectParameters.Direction = 3 } catch {} }
        } catch { $report += "effect failed slide $($sl.SlideIndex) $($sh.Name): $_" }
    }
    # all text and shape steps: automatic, short, no waiting for clicks
    for ($i = 1; $i -le $seq.Count; $i++) {
        $e = $seq.Item($i)
        $e.Timing.TriggerType = 3          # after previous
        $e.Timing.Duration = 0.4
        $e.Timing.TriggerDelayTime = 0
    }
    # the video starts when clicked
    foreach ($sh in $sl.Shapes) {
        if ($sh.Type -eq 16) { try { $m = $seq.AddEffect($sh, 83, 0, 1); $report += "slide $($sl.SlideIndex): video play-on-click" } catch { $report += "video effect failed: $_" } }
    }
    $report += "slide $($sl.SlideIndex): $($seq.Count) animation steps"
}
$pres.Save()
$pres.Close()
$app.Quit()
$report
