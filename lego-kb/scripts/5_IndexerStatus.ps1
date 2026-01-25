<#
.SYNOPSIS
    Check the status of the Azure AI Search indexer

.DESCRIPTION
    Displays the current status, last run time, and any errors from the indexer.

.EXAMPLE
    .\Get-IndexerStatus.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env"
)

# Import environment variables
function Import-EnvFile {
    param([string]$Path)
    
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.+)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, 'Process')
            }
        }
    }
}

Import-EnvFile -Path $EnvFile

$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$indexName = $env:AZURE_SEARCH_INDEX_NAME
$indexerName = "$indexName-indexer"

if (-not $searchEndpoint -or -not $indexName) {
    Write-Error "Required environment variables not set"
    exit 1
}

# Get access token
$accessToken = az account get-access-token --resource https://search.azure.com --query accessToken -o tsv
if (-not $accessToken) {
    Write-Error "Failed to get access token"
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

Write-Host "=== Indexer Status ===" -ForegroundColor Green
Write-Host "Indexer: $indexerName" -ForegroundColor Cyan
Write-Host ""

# Get indexer status
$statusUrl = "$searchEndpoint/indexers/$indexerName/status?api-version=2024-07-01"
try {
    $status = Invoke-RestMethod -Uri $statusUrl -Method Get -Headers $headers -ErrorAction Stop
    
    Write-Host "Overall Status: $($status.status)" -ForegroundColor $(if ($status.status -eq "running") { "Green" } else { "Yellow" })
    Write-Host ""
    
    if ($status.lastResult) {
        $lastRun = $status.lastResult
        Write-Host "Last Run:" -ForegroundColor Cyan
        Write-Host "  Status: $($lastRun.status)" -ForegroundColor $(if ($lastRun.status -eq "success") { "Green" } elseif ($lastRun.status -eq "inProgress") { "Yellow" } else { "Red" })
        Write-Host "  Start Time: $($lastRun.startTime)"
        Write-Host "  End Time: $($lastRun.endTime)"
        Write-Host "  Items Processed: $($lastRun.itemsProcessed)"
        Write-Host "  Items Failed: $($lastRun.itemsFailed)" -ForegroundColor $(if ($lastRun.itemsFailed -gt 0) { "Red" } else { "White" })
        
        if ($lastRun.errors -and $lastRun.errors.Count -gt 0) {
            Write-Host ""
            Write-Host "Errors:" -ForegroundColor Red
            foreach ($error in $lastRun.errors) {
                Write-Host "  - $($error.message)" -ForegroundColor Red
                if ($error.details) {
                    Write-Host "    Details: $($error.details)" -ForegroundColor DarkRed
                }
            }
        }
        
        if ($lastRun.warnings -and $lastRun.warnings.Count -gt 0) {
            Write-Host ""
            Write-Host "Warnings:" -ForegroundColor Yellow
            foreach ($warning in $lastRun.warnings | Select-Object -First 5) {
                Write-Host "  - $($warning.message)" -ForegroundColor Yellow
            }
            if ($lastRun.warnings.Count -gt 5) {
                Write-Host "  ... and $($lastRun.warnings.Count - 5) more warnings" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "No runs recorded yet" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Execution History (last 5 runs):" -ForegroundColor Cyan
    if ($status.executionHistory -and $status.executionHistory.Count -gt 0) {
        $history = $status.executionHistory | Select-Object -First 5
        foreach ($run in $history) {
            $statusColor = switch ($run.status) {
                "success" { "Green" }
                "inProgress" { "Yellow" }
                default { "Red" }
            }
            Write-Host "  [$($run.startTime)] $($run.status) - $($run.itemsProcessed) items" -ForegroundColor $statusColor
        }
    } else {
        Write-Host "  No execution history" -ForegroundColor Gray
    }
    
} catch {
    Write-Error "Failed to get indexer status: $_"
    exit 1
}

# Get index document count
Write-Host ""
Write-Host "Index Statistics:" -ForegroundColor Cyan
$indexStatsUrl = "$searchEndpoint/indexes/$indexName/stats?api-version=2024-07-01"
try {
    $indexStats = Invoke-RestMethod -Uri $indexStatsUrl -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "  Document Count: $($indexStats.documentCount)"
    Write-Host "  Storage Size: $([math]::Round($indexStats.storageSize / 1MB, 2)) MB"
} catch {
    Write-Warning "Could not retrieve index statistics"
}
