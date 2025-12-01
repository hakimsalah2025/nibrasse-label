Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Run quick_start.bat in hidden mode (0)
WshShell.Run chr(34) & strPath & "\quick_start.bat" & chr(34), 0
Set WshShell = Nothing
