Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strPath = FSO.GetParentFolderName(WScript.ScriptFullName)

' Construct the path to the batch file
strBatchFile = strPath & "\run_pipeline.bat"

' Check if the batch file exists
If FSO.FileExists(strBatchFile) Then
    ' Run the batch file silently (0 = hide window)
    WshShell.Run chr(34) & strBatchFile & chr(34), 0
Else
    MsgBox "Could not find run_pipeline.bat in " & strPath, 16, "Error"
End If

Set WshShell = Nothing
Set FSO = Nothing
