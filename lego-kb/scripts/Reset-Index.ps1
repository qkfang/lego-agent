<#
.SYNOPSIS
    Reset Azure AI Search index and re-ingest all documents

.DESCRIPTION
    This script provides options to clear all documents from the index or completely
    delete and recreate the index, then re-ingest all documents from the docs folder.

.EXAMPLE
    .\Reset-Index.ps1
    Clear all documents and re-ingest

.EXAMPLE
    .\Reset-Index.ps1 -RecreateIndex
    Delete and recreate the index, then re-ingest all documents

.NOTES
    Requires environment variables to be set in .env file or system environment
    This operation cannot be undone - use with caution!
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$RecreateIndex,
    
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Import environment variables from .env file if it exists
function Import-EnvFile {
    param([string]$Path)
    
    if (Test-Path $Path) {
        Write-Host "Loading environment variables from $Path" -ForegroundColor Cyan
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.+)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                Write-Verbose "Set $name"
            }
        }
    } else {
        Write-Warning ".env file not found at $Path. Using system environment variables."
    }
}

# Function to get all document IDs from the index
function Get-IndexDocumentIds {
    param(
        [string]$Endpoint,
        [string]$IndexName,
        [string]$ApiKey
    )
    
    $searchUrl = "$Endpoint/indexes/$IndexName/docs?api-version=2023-11-01&`$select=id&`$top=1000"
    $headers = @{
        "api-key" = $ApiKey
    }
    
    try {
        $response = Invoke-RestMethod -Uri $searchUrl -Method Get -Headers $headers
        return $response.value
    } catch {
        Write-Error "Failed to retrieve document IDs: $_"
        return @()
    }
}

# Function to delete all documents from the index
function Clear-IndexDocuments {
    param(
        [string]$Endpoint,
        [string]$IndexName,
        [string]$ApiKey
    )
    
    Write-Host "Retrieving all document IDs..." -ForegroundColor Cyan
    $documents = Get-IndexDocumentIds -Endpoint $Endpoint -IndexName $IndexName -ApiKey $ApiKey
    
    if ($documents.Count -eq 0) {
        Write-Host "Index is already empty" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "Found $($documents.Count) documents to delete" -ForegroundColor Cyan
    
    # Create delete batch
    $deleteActions = @()
    foreach ($doc in $documents) {
        $deleteActions += @{
            "@search.action" = "delete"
            id = $doc.id
        }
    }
    
    $batch = @{
        value = $deleteActions
    }
    
    $batchJson = $batch | ConvertTo-Json -Depth 10
    
    $uploadUrl = "$Endpoint/indexes/$IndexName/docs/index?api-version=2023-11-01"
    $headers = @{
        "api-key" = $ApiKey
        "Content-Type" = "application/json"
    }
    
    try {
        Write-Host "Deleting documents..." -ForegroundColor Cyan
        $response = Invoke-RestMethod -Uri $uploadUrl -Method Post -Headers $headers -Body $batchJson
        
        $successCount = ($response.value | Where-Object { $_.status -eq $true }).Count
        Write-Host "✓ Deleted $successCount documents" -ForegroundColor Green
        
        return $true
    } catch {
        Write-Error "Failed to delete documents: $_"
        return $false
    }
}

# Main script
Write-Host "=== Azure AI Search Index Reset ===" -ForegroundColor Red
Write-Host ""

# Load environment variables
Import-EnvFile -Path $EnvFile

# Get required environment variables
$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$searchApiKey = $env:AZURE_SEARCH_API_KEY
$indexName = $env:AZURE_SEARCH_INDEX_NAME

if (-not $searchEndpoint -or -not $searchApiKey -or -not $indexName) {
    Write-Error "Required environment variables not set. Please configure AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, and AZURE_SEARCH_INDEX_NAME"
    exit 1
}

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Index Name: $indexName" -ForegroundColor Cyan
Write-Host ""

# Confirm with user
if (-not $Force) {
    if ($RecreateIndex) {
        Write-Warning "This will DELETE the entire index '$indexName' and recreate it."
    } else {
        Write-Warning "This will CLEAR all documents from the index '$indexName'."
    }
    
    Write-Host "This operation cannot be undone!" -ForegroundColor Yellow
    $confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
    
    if ($confirmation -ne "yes") {
        Write-Host "Operation cancelled" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""

# Perform reset operation
if ($RecreateIndex) {
    Write-Host "Recreating index..." -ForegroundColor Cyan
    
    # Call Initialize-SearchIndex.ps1 with -Force flag
    $initScript = Join-Path $PSScriptRoot "Initialize-SearchIndex.ps1"
    
    if (Test-Path $initScript) {
        try {
            & $initScript -Force -EnvFile $EnvFile
            if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
                throw "Script returned exit code $LASTEXITCODE"
            }
        } catch {
            Write-Error "Failed to recreate index: $_"
            exit 1
        }
    } else {
        Write-Error "Initialize-SearchIndex.ps1 not found at: $initScript"
        exit 1
    }
} else {
    Write-Host "Clearing all documents from index..." -ForegroundColor Cyan
    
    $success = Clear-IndexDocuments -Endpoint $searchEndpoint -IndexName $indexName -ApiKey $searchApiKey
    
    if (-not $success) {
        Write-Error "Failed to clear documents"
        exit 1
    }
}

Write-Host ""
Write-Host "Reset complete!" -ForegroundColor Green
Write-Host ""

# Ask if user wants to re-ingest documents
$reingest = Read-Host "Do you want to re-ingest documents now? (yes/no)"

if ($reingest -eq "yes") {
    Write-Host ""
    Write-Host "Starting document ingestion..." -ForegroundColor Cyan
    Write-Host ""
    
    # Call Ingest-Documents.ps1
    $ingestScript = Join-Path $PSScriptRoot "Ingest-Documents.ps1"
    
    if (Test-Path $ingestScript) {
        try {
            & $ingestScript -EnvFile $EnvFile
            Write-Host ""
            Write-Host "Reset and re-ingestion complete!" -ForegroundColor Green
        } catch {
            Write-Error "Ingestion failed: $_"
            exit 1
        }
    } else {
        Write-Error "Ingest-Documents.ps1 not found at: $ingestScript"
        exit 1
    }
} else {
    Write-Host "Skipping document ingestion" -ForegroundColor Yellow
    Write-Host "You can manually run .\Ingest-Documents.ps1 when ready" -ForegroundColor Yellow
}
