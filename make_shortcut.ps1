# Creates "Deutsch lernen" shortcuts on the Desktop and in the Start menu.
# Run again any time (right-click > Run with PowerShell) if you move the app folder.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$shell = New-Object -ComObject WScript.Shell
$places = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))
foreach ($dir in $places) {
    $lnk = $shell.CreateShortcut((Join-Path $dir 'Deutsch lernen.lnk'))
    $lnk.TargetPath = Join-Path $root '.venv\Scripts\pythonw.exe'
    $lnk.Arguments = '"' + (Join-Path $root 'launch.pyw') + '"'
    $lnk.WorkingDirectory = $root
    $lnk.IconLocation = (Join-Path $root 'static\icon.ico')
    $lnk.Description = 'German study app: textbooks, practice, flashcards and coach'
    $lnk.Save()
    Write-Host "Created shortcut in $dir"
}
