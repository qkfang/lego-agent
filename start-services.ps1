# Start lego-mcp, lego-api, and lego-web services together
param(
    [switch]$Mock
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "Starting services..." -ForegroundColor Blue

$jobs = @()

try {
    # 1. Build and start lego-mcp
    Write-Host "Building lego-mcp..." -ForegroundColor Blue
    Push-Location "$ProjectRoot\lego-mcp"
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Failed to build lego-mcp" }
    Pop-Location

    Write-Host "Starting lego-mcp..." -ForegroundColor Green
    $env:IS_MOCK = if ($Mock) { "true" } else { "false" }
    $jobs += Start-Process -FilePath "node" -ArgumentList "build/index.js" -WorkingDirectory "$ProjectRoot\lego-mcp" -PassThru -NoNewWindow

    Start-Sleep -Seconds 2

    # 2. Start lego-api
    Write-Host "Starting lego-api..." -ForegroundColor Green
    $jobs += Start-Process -FilePath "uvicorn" -ArgumentList "main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "$ProjectRoot\lego-api" -PassThru -NoNewWindow

    Start-Sleep -Seconds 2

    # 3. Start lego-web
    Write-Host "Starting lego-web..." -ForegroundColor Green
    $jobs += Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -WorkingDirectory "$ProjectRoot\lego-web" -PassThru -NoNewWindow

    Write-Host "`nAll services started!" -ForegroundColor Green
    Write-Host "  lego-mcp: MCP server running"
    Write-Host "  lego-api: http://localhost:8000"
    Write-Host "  lego-web: http://localhost:5173"
    Write-Host "`nPress Ctrl+C to stop all services..." -ForegroundColor Yellow

    # Wait for user interrupt
    while ($true) {
        Start-Sleep -Seconds 1
        foreach ($job in $jobs) {
            if ($job.HasExited) {
                Write-Host "A service has stopped unexpectedly" -ForegroundColor Red
                break
            }
        }
    }
}
finally {
    Write-Host "`nStopping services..." -ForegroundColor Red
    foreach ($job in $jobs) {
        if (-not $job.HasExited) {
            Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "Cleanup complete" -ForegroundColor Green
}
