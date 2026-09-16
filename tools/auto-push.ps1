$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

function Sync-Repository {
  $changes = git status --porcelain
  if (-not $changes) {
    return
  }

  git add -A
  $staged = git diff --cached --name-only
  if (-not $staged) {
    return
  }

  $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  git commit -m "Auto update $timestamp"
  if ($LASTEXITCODE -eq 0) {
    git push origin main
  }
}

Write-Host "Auto GitHub push aktif: $repo"
Sync-Repository

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repo
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, DirectoryName, LastWrite, Size'
$watcher.Filter = '*'

$subscription = Register-ObjectEvent -InputObject $watcher -EventName Changed -SourceIdentifier 'IconnetAutoPushChanged'
$subscriptionCreated = Register-ObjectEvent -InputObject $watcher -EventName Created -SourceIdentifier 'IconnetAutoPushCreated'
$subscriptionDeleted = Register-ObjectEvent -InputObject $watcher -EventName Deleted -SourceIdentifier 'IconnetAutoPushDeleted'
$subscriptionRenamed = Register-ObjectEvent -InputObject $watcher -EventName Renamed -SourceIdentifier 'IconnetAutoPushRenamed'

try {
  while ($true) {
    $event = Wait-Event -Timeout 3
    if (-not $event) {
      continue
    }

    do {
      Remove-Event -EventIdentifier $event.EventIdentifier -ErrorAction SilentlyContinue
      $event = Wait-Event -Timeout 1
    } while ($event)

    Sync-Repository
  }
}
finally {
  Unregister-Event -SourceIdentifier 'IconnetAutoPushChanged' -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier 'IconnetAutoPushCreated' -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier 'IconnetAutoPushDeleted' -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier 'IconnetAutoPushRenamed' -ErrorAction SilentlyContinue
  $watcher.Dispose()
}
