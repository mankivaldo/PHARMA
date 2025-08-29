Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\App\PHARMA\start_pharma.bat" & chr(34), 0
Set WshShell = Nothing
