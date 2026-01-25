<#
.SYNOPSIS
    Upload documents to Azure Blob Storage for indexing

.DESCRIPTION
    This script uploads PDF and Word documents to Azure Blob Storage.
    The Azure AI Search indexer will automatically process and index them.

.EXAMPLE
    .\2-Ingest-Documents.ps1

.EXAMPLE
    .\2-Ingest-Documents.ps1 -DocsPath "C:\path\to\docs"

.NOTES
    Requires:
    - Azure CLI logged in with 'az login'
    - Storage Blob Data Contributor role on the storage account
    - Environment variables in .env file
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DocsPath = "../docs",
    
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env",
    
    [Parameter(Mandatory=$false)]
    [string[]]$FileTypes = @("*.pdf", "*.docx", "*.doc", "*.txt", "*.md")
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

# Main script
Write-Host "=== Upload Documents to Azure Blob Storage ===" -ForegroundColor Green
Write-Host ""

# Load environment variables
Import-EnvFile -Path $EnvFile

# Get required environment variables
$storageResourceId = $env:AZURE_STORAGE_RESOURCE_ID
$storageContainer = $env:AZURE_STORAGE_CONTAINER

if (-not $storageResourceId -or -not $storageContainer) {
    Write-Error "Required environment variables not set. Please configure AZURE_STORAGE_RESOURCE_ID and AZURE_STORAGE_CONTAINER"
    exit 1
}

# Extract storage account name from resource ID
$storageAccountName = ($storageResourceId -split '/')[-1]

Write-Host "Storage Account: $storageAccountName" -ForegroundColor Cyan
Write-Host "Container: $storageContainer" -ForegroundColor Cyan
Write-Host "Docs Path: $DocsPath" -ForegroundColor Cyan
Write-Host ""

# Check if docs folder exists
$resolvedDocsPath = Resolve-Path $DocsPath -ErrorAction SilentlyContinue
if (-not $resolvedDocsPath) {
    Write-Error "Docs folder not found at: $DocsPath"
    exit 1
}

# Find all documents
$allFiles = @()
foreach ($fileType in $FileTypes) {
    $files = Get-ChildItem -Path $resolvedDocsPath -Filter $fileType -File -Recurse
    $allFiles += $files
}

if ($allFiles.Count -eq 0) {
    Write-Warning "No documents found in $DocsPath"
    Write-Host "Supported file types: $($FileTypes -join ', ')" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($allFiles.Count) document(s) to upload" -ForegroundColor Cyan
Write-Host ""

# Upload each document
$uploadedCount = 0
$failedCount = 0

foreach ($file in $allFiles) {
    $relativePath = $file.FullName.Substring($resolvedDocsPath.Path.Length).TrimStart('\', '/')
    $blobName = $relativePath -replace '\\', '/'
    
    Write-Host "Uploading: $($file.Name)..." -ForegroundColor Cyan -NoNewline
    
    try {
        $result = az storage blob upload `
            --account-name $storageAccountName `
            --container-name $storageContainer `
            --name $blobName `
            --file $file.FullName `
            --overwrite `
            --auth-mode login `
            --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $uploadedCount++
        } else {
            Write-Host " ✗" -ForegroundColor Red
            Write-Warning "  Error: $result"
            $failedCount++
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        Write-Warning "  Error: $_"
        $failedCount++
    }
}

Write-Host ""
Write-Host "=== Upload Complete ===" -ForegroundColor Green
Write-Host "  Uploaded: $uploadedCount" -ForegroundColor Green
Write-Host "  Failed: $failedCount" -ForegroundColor $(if ($failedCount -gt 0) { "Yellow" } else { "White" })
Write-Host ""

if ($uploadedCount -gt 0) {
    Write-Host "Documents uploaded to blob storage." -ForegroundColor Cyan
    Write-Host "The indexer will automatically process them (runs every hour)." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To trigger indexing immediately, run:" -ForegroundColor Yellow
    Write-Host "  .\3-Run-Indexer.ps1" -ForegroundColor White
}

