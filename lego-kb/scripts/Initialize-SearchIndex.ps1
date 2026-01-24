<#
.SYNOPSIS
    Initialize Azure AI Search index for LEGO Knowledge Base

.DESCRIPTION
    This script creates a new Azure AI Search index with the appropriate schema
    for storing LEGO robot documentation, manuals, and knowledge base content.

.EXAMPLE
    .\Initialize-SearchIndex.ps1

.NOTES
    Requires environment variables to be set in .env file or system environment
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env"
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

Write-Host "=== Azure AI Search Index Initialization ===" -ForegroundColor Green
Write-Host "Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Index Name: $indexName" -ForegroundColor Cyan

# Define the index schema
$indexSchema = @{
    name = $indexName
    fields = @(
        @{
            name = "id"
            type = "Edm.String"
            key = $true
            searchable = $false
            filterable = $true
            sortable = $false
            facetable = $false
        },
        @{
            name = "title"
            type = "Edm.String"
            searchable = $true
            filterable = $true
            sortable = $true
            facetable = $false
            analyzer = "standard.lucene"
        },
        @{
            name = "content"
            type = "Edm.String"
            searchable = $true
            filterable = $false
            sortable = $false
            facetable = $false
            analyzer = "standard.lucene"
        },
        @{
            name = "documentType"
            type = "Edm.String"
            searchable = $false
            filterable = $true
            sortable = $true
            facetable = $true
        },
        @{
            name = "filePath"
            type = "Edm.String"
            searchable = $false
            filterable = $true
            sortable = $false
            facetable = $false
        },
        @{
            name = "fileName"
            type = "Edm.String"
            searchable = $true
            filterable = $true
            sortable = $true
            facetable = $false
        },
        @{
            name = "pageCount"
            type = "Edm.Int32"
            searchable = $false
            filterable = $true
            sortable = $true
            facetable = $true
        },
        @{
            name = "uploadedAt"
            type = "Edm.DateTimeOffset"
            searchable = $false
            filterable = $true
            sortable = $true
            facetable = $false
        },
        @{
            name = "metadata"
            type = "Edm.String"
            searchable = $false
            filterable = $false
            sortable = $false
            facetable = $false
        },
        @{
            name = "category"
            type = "Edm.String"
            searchable = $true
            filterable = $true
            sortable = $true
            facetable = $true
        }
    )
    suggesters = @(
        @{
            name = "sg"
            searchMode = "analyzingInfixMatching"
            sourceFields = @("title", "fileName", "category")
        }
    )
    semantic = @{
        configurations = @(
            @{
                name = "default"
                prioritizedFields = @{
                    titleField = @{
                        fieldName = "title"
                    }
                    contentFields = @(
                        @{ fieldName = "content" }
                    )
                    keywordsFields = @(
                        @{ fieldName = "category" }
                    )
                }
            }
        )
    }
}

# Convert to JSON
$indexSchemaJson = $indexSchema | ConvertTo-Json -Depth 10

# Prepare headers
$headers = @{
    "api-key" = $searchApiKey
    "Content-Type" = "application/json"
}

# Check if index already exists
$checkUrl = "$searchEndpoint/indexes/$indexName?api-version=2023-11-01"
try {
    $existingIndex = Invoke-RestMethod -Uri $checkUrl -Method Get -Headers $headers -ErrorAction Stop
    
    if ($Force) {
        Write-Warning "Index '$indexName' already exists. Deleting due to -Force flag..."
        
        # Delete the existing index
        $deleteUrl = "$searchEndpoint/indexes/$indexName?api-version=2023-11-01"
        Invoke-RestMethod -Uri $deleteUrl -Method Delete -Headers $headers -ErrorAction Stop
        Write-Host "Existing index deleted successfully" -ForegroundColor Yellow
    } else {
        Write-Warning "Index '$indexName' already exists. Use -Force to delete and recreate."
        Write-Host "Exiting without changes." -ForegroundColor Yellow
        exit 0
    }
} catch {
    $statusCode = $null
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }
    
    if ($statusCode -eq 404) {
        Write-Host "Index does not exist. Creating new index..." -ForegroundColor Cyan
    } else {
        Write-Error "Error checking index: $_"
        exit 1
    }
}

# Create the index
$createUrl = "$searchEndpoint/indexes?api-version=2023-11-01"
try {
    Write-Host "Creating index '$indexName'..." -ForegroundColor Cyan
    
    $response = Invoke-RestMethod -Uri $createUrl -Method Post -Headers $headers -Body $indexSchemaJson -ErrorAction Stop
    
    Write-Host "✓ Index created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Index Details:" -ForegroundColor Cyan
    Write-Host "  Name: $($response.name)"
    Write-Host "  Fields: $($response.fields.Count)"
    Write-Host "  Semantic Configuration: Enabled"
    Write-Host "  Suggester: Enabled"
    Write-Host ""
    Write-Host "You can now ingest documents using .\Ingest-Documents.ps1" -ForegroundColor Green
    
} catch {
    Write-Error "Failed to create index: $_"
    if ($_.ErrorDetails.Message) {
        Write-Error "Details: $($_.ErrorDetails.Message)"
    }
    exit 1
}
