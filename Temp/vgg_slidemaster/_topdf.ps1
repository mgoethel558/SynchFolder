$ppt = New-Object -ComObject PowerPoint.Application
$path = (Resolve-Path "_probe.pptx").Path
$out = $path -replace '\.pptx$','.pdf'
$pres = $ppt.Presentations.Open($path, $true, $false, $false)
$pres.SaveAs($out, 32)  # 32 = ppSaveAsPDF
$pres.Close()
$ppt.Quit()
Write-Output $out
