# PowerShell script to package Teams app for deployment
# This creates a zip file with the app manifest and icons

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppPackageDir = Join-Path $ScriptDir "..\appPackage"
$OutputFile = Join-Path $ScriptDir "..\lego-copilot-teams-app.zip"

Write-Host "Packaging LEGO Copilot Teams App..." -ForegroundColor Green

# Check if appPackage directory exists
if (-not (Test-Path $AppPackageDir)) {
    Write-Host "Error: appPackage directory not found" -ForegroundColor Red
    exit 1
}

# Check required files
$ManifestPath = Join-Path $AppPackageDir "manifest.json"
if (-not (Test-Path $ManifestPath)) {
    Write-Host "Error: manifest.json not found in appPackage" -ForegroundColor Red
    exit 1
}

# Remove old package if exists
if (Test-Path $OutputFile) {
    Remove-Item $OutputFile
    Write-Host "Removed old package"
}

# Create zip package
try {
    Compress-Archive -Path "$AppPackageDir\*" -DestinationPath $OutputFile -Force
    
    if (Test-Path $OutputFile) {
        Write-Host "`n✓ Teams app package created: lego-copilot-teams-app.zip" -ForegroundColor Green
        Write-Host "`nNext steps:"
        Write-Host "1. Open Microsoft Teams"
        Write-Host "2. Go to Apps > Manage your apps > Upload an app"
        Write-Host "3. Select 'Upload a custom app'"
        Write-Host "4. Choose the lego-copilot-teams-app.zip file"
        Write-Host "`nNote: Make sure to update BOT_ID and TEAMS_APP_ID in manifest.json before packaging" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error: Failed to create package - $_" -ForegroundColor Red
    exit 1
}
