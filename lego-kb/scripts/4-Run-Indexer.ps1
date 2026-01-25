<#
.SYNOPSIS
    Run the Azure AI Search indexer

.DESCRIPTION
    Manually triggers the indexer to process documents and monitors progress.

.EXAMPLE
    .\3a-Run-Indexer.ps1

.NOTES
    Requires:
    - Indexer already configured via 3-Setup-Indexer.ps1
    - Environment variables in .env file
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env"
)

# Import environment variables from .env file
function Import-EnvFile {
    param([string]$Path)
    
    if (Test-Path $Path) {
        Write-Host "Loading environment variables from $Path" -ForegroundColor Cyan
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.+)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, 'Process')
            }
        }
    } else {
        Write-Warning ".env file not found at $Path"
    }
}

# Get Azure access token
function Get-AzureAccessToken {
    param([string]$Resource)
    
    try {
        $tokenResponse = az account get-access-token --resource $Resource --output json 2>$null | ConvertFrom-Json
        if ($tokenResponse -and $tokenResponse.accessToken) {
            return $tokenResponse.accessToken
        }
        throw "Failed to get access token"
    }
    catch {
        Write-Error "Failed to get Azure access token for $Resource. Ensure you are logged in with 'az login'."
        return $null
    }
}

# Main script
Write-Host "=== Run Azure AI Search Indexer ===" -ForegroundColor Green
Write-Host ""

# Load environment variables
Import-EnvFile -Path $EnvFile

# Get required environment variables
$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$indexName = $env:AZURE_SEARCH_INDEX_NAME

# Validate required variables
$missingVars = @()
if (-not $searchEndpoint) { $missingVars += "AZURE_SEARCH_ENDPOINT" }
if (-not $indexName) { $missingVars += "AZURE_SEARCH_INDEX_NAME" }

if ($missingVars.Count -gt 0) {
    Write-Error "Missing required environment variables: $($missingVars -join ', ')"
    exit 1
}

# Get access token
Write-Host "Acquiring access token..." -ForegroundColor Cyan
$accessToken = Get-AzureAccessToken -Resource "https://search.azure.com"
if (-not $accessToken) { exit 1 }

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

$indexerName = "$indexName-indexer"

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Indexer: $indexerName" -ForegroundColor Cyan
Write-Host ""

# Run the indexer
Write-Host "Running Indexer..." -ForegroundColor Cyan
$runUrl = "$searchEndpoint/indexers/$indexerName/run?api-version=2024-07-01"
try {
    Invoke-RestMethod -Uri $runUrl -Method Post -Headers $headers -ErrorAction Stop | Out-Null
    Write-Host "  ✓ Indexer started successfully" -ForegroundColor Green
    
    # Wait and show initial progress
    Write-Host ""
    Write-Host "Waiting for indexer to process..." -ForegroundColor Cyan
    $statusUrl = "$searchEndpoint/indexers/$indexerName/status?api-version=2024-07-01"
    $maxWaitAttempts = 30
    $waitAttempt = 0
    
    do {
        Start-Sleep -Seconds 5
        $waitAttempt++
        
        try {
            $status = Invoke-RestMethod -Uri $statusUrl -Method Get -Headers $headers -ErrorAction Stop
            $lastResult = $status.lastResult
            
            if ($lastResult) {
                $runStatus = $lastResult.status
                $itemsProcessed = $lastResult.itemsProcessed
                $itemsFailed = $lastResult.itemsFailed
                
                Write-Host "  Status: $runStatus | Processed: $itemsProcessed | Failed: $itemsFailed" -ForegroundColor $(
                    if ($runStatus -eq "success") { "Green" }
                    elseif ($runStatus -eq "inProgress") { "Yellow" }
                    else { "Red" }
                )
                
                if ($runStatus -eq "success") {
                    Write-Host "  ✓ Indexer completed successfully!" -ForegroundColor Green
                    break
                } elseif ($runStatus -eq "transientFailure" -or $runStatus -eq "persistentFailure") {
                    Write-Warning "  Indexer encountered errors. Run .\4-Get-IndexerStatus.ps1 for details."
                    break
                }
            }
        } catch {
            Write-Verbose "Could not get status: $_"
        }
        
    } while ($waitAttempt -lt $maxWaitAttempts)
    
    if ($waitAttempt -ge $maxWaitAttempts) {
        Write-Host "  Indexer still running. Use .\4-Get-IndexerStatus.ps1 to check progress." -ForegroundColor Yellow
    }
    
} catch {
    Write-Warning "Failed to start indexer: $_"
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
