<#
.SYNOPSIS
    Setup Azure AI Search indexer with automatic chunking

.DESCRIPTION
    Creates a data source, skillset with Text Split skill, and indexer for
    automatic document chunking. Documents are read from Azure Blob Storage
    and chunked using built-in AI Search capabilities.

.EXAMPLE
    .\Setup-Indexer.ps1

.EXAMPLE
    .\Setup-Indexer.ps1 -ChunkSize 2000 -ChunkOverlap 500

.NOTES
    Requires:
    - Documents uploaded to Azure Blob Storage container
    - Azure Document Intelligence resource (for PDF/Office parsing)
    - Environment variables in .env file
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env",
    
    [Parameter(Mandatory=$false)]
    [int]$ChunkSize = 2000,
    
    [Parameter(Mandatory=$false)]
    [int]$ChunkOverlap = 500,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
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
Write-Host "=== Azure AI Search Indexer Setup ===" -ForegroundColor Green
Write-Host ""

# Load environment variables
Import-EnvFile -Path $EnvFile

# Get required environment variables
$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$indexName = $env:AZURE_SEARCH_INDEX_NAME
$storageResourceId = $env:AZURE_STORAGE_RESOURCE_ID
$storageContainer = $env:AZURE_STORAGE_CONTAINER
$docIntelligenceEndpoint = $env:AZURE_DOC_INTELLIGENCE_ENDPOINT

# Validate required variables
$missingVars = @()
if (-not $searchEndpoint) { $missingVars += "AZURE_SEARCH_ENDPOINT" }
if (-not $indexName) { $missingVars += "AZURE_SEARCH_INDEX_NAME" }
if (-not $storageResourceId) { $missingVars += "AZURE_STORAGE_RESOURCE_ID" }
if (-not $storageContainer) { $missingVars += "AZURE_STORAGE_CONTAINER" }
if (-not $docIntelligenceEndpoint) { $missingVars += "AZURE_DOC_INTELLIGENCE_ENDPOINT" }

if ($missingVars.Count -gt 0) {
    Write-Error "Missing required environment variables: $($missingVars -join ', ')"
    Write-Host ""
    Write-Host "Required .env variables:" -ForegroundColor Yellow
    Write-Host "  AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net"
    Write-Host "  AZURE_SEARCH_INDEX_NAME=lego-kb"
    Write-Host "  AZURE_STORAGE_RESOURCE_ID=/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>"
    Write-Host "  AZURE_STORAGE_CONTAINER=documents"
    Write-Host "  AZURE_DOC_INTELLIGENCE_ENDPOINT=https://<doc-intelligence>.cognitiveservices.azure.com"
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

# Resource names
$dataSourceName = "$indexName-datasource"
$skillsetName = "$indexName-skillset"
$indexerName = "$indexName-indexer"

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Index Name: $indexName" -ForegroundColor Cyan
Write-Host "Data Source: $dataSourceName" -ForegroundColor Cyan
Write-Host "Skillset: $skillsetName" -ForegroundColor Cyan
Write-Host "Indexer: $indexerName" -ForegroundColor Cyan
Write-Host "Chunk Size: $ChunkSize" -ForegroundColor Cyan
Write-Host "Chunk Overlap: $ChunkOverlap" -ForegroundColor Cyan
Write-Host ""

# Helper function to create or update a resource
function Set-SearchResource {
    param(
        [string]$ResourceType,
        [string]$ResourceName,
        [hashtable]$ResourceBody
    )
    
    $resourceJson = $ResourceBody | ConvertTo-Json -Depth 20
    
    # Check if resource exists
    $checkUrl = "$searchEndpoint/$ResourceType/$ResourceName`?api-version=2024-07-01"
    $exists = $false
    
    try {
        Invoke-RestMethod -Uri $checkUrl -Method Get -Headers $headers -ErrorAction Stop | Out-Null
        $exists = $true
    } catch {
        $statusCode = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $statusCode = $_.Exception.Response.StatusCode.value__
        }
        if ($statusCode -ne 404) {
            throw $_
        }
    }
    
    if ($exists) {
        if ($Force) {
            Write-Host "  Updating existing $ResourceType '$ResourceName'..." -ForegroundColor Yellow
            $updateUrl = "$searchEndpoint/$ResourceType/$ResourceName`?api-version=2024-07-01"
            Invoke-RestMethod -Uri $updateUrl -Method Put -Headers $headers -Body $resourceJson -ErrorAction Stop | Out-Null
        } else {
            Write-Host "  $ResourceType '$ResourceName' already exists (use -Force to update)" -ForegroundColor Yellow
            return
        }
    } else {
        Write-Host "  Creating $ResourceType '$ResourceName'..." -ForegroundColor Cyan
        $createUrl = "$searchEndpoint/$ResourceType`?api-version=2024-07-01"
        Invoke-RestMethod -Uri $createUrl -Method Post -Headers $headers -Body $resourceJson -ErrorAction Stop | Out-Null
    }
    
    Write-Host "  ✓ $ResourceType configured successfully" -ForegroundColor Green
}

# 1. Create Data Source
Write-Host "Step 1: Configuring Data Source..." -ForegroundColor Cyan
$dataSource = @{
    name = $dataSourceName
    type = "azureblob"
    credentials = @{
        connectionString = "ResourceId=$storageResourceId;"
    }
    container = @{
        name = $storageContainer
    }
    dataChangeDetectionPolicy = @{
        "@odata.type" = "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy"
        highWaterMarkColumnName = "metadata_storage_last_modified"
    }
}

try {
    Set-SearchResource -ResourceType "datasources" -ResourceName $dataSourceName -ResourceBody $dataSource
} catch {
    Write-Error "Failed to create data source: $_"
    exit 1
}

# 2. Create Skillset with Text Split and Document Intelligence
Write-Host "Step 2: Configuring Skillset..." -ForegroundColor Cyan
$skillset = @{
    name = $skillsetName
    description = "Skillset for chunking documents with Document Intelligence parsing"
    skills = @(
        # Document Extraction skill - uses built-in Azure AI Search integration with Document Intelligence
        @{
            "@odata.type" = "#Microsoft.Skills.Util.DocumentExtractionSkill"
            name = "document-extraction"
            description = "Extract text from documents using Document Intelligence"
            context = "/document"
            parsingMode = "default"
            dataToExtract = "contentAndMetadata"
            inputs = @(
                @{
                    name = "file_data"
                    source = "/document/file_data"
                }
            )
            outputs = @(
                @{
                    name = "content"
                    targetName = "extracted_content"
                }
            )
        },
        # Text Split skill for chunking - now uses extracted content
        @{
            "@odata.type" = "#Microsoft.Skills.Text.SplitSkill"
            name = "text-split"
            description = "Split text into chunks"
            context = "/document"
            textSplitMode = "pages"
            maximumPageLength = $ChunkSize
            pageOverlapLength = $ChunkOverlap
            inputs = @(
                @{
                    name = "text"
                    source = "/document/extracted_content"
                }
            )
            outputs = @(
                @{
                    name = "textItems"
                    targetName = "chunks"
                }
            )
        }
    )
    indexProjections = @{
        selectors = @(
            @{
                targetIndexName = $indexName
                parentKeyFieldName = "parent_id"
                sourceContext = "/document/chunks/*"
                mappings = @(
                    @{
                        name = "content"
                        source = "/document/chunks/*"
                    },
                    @{
                        name = "title"
                        source = "/document/metadata_storage_name"
                    },
                    @{
                        name = "fileName"
                        source = "/document/metadata_storage_name"
                    },
                    @{
                        name = "filePath"
                        source = "/document/metadata_storage_path"
                    },
                    @{
                        name = "documentType"
                        source = "/document/metadata_content_type"
                    },
                    @{
                        name = "chunkIndex"
                        source = "/document/chunks/*/@odata.index"
                    }
                )
            }
        )
        parameters = @{
            projectionMode = "skipIndexingParentDocuments"
        }
    }
}

try {
    Set-SearchResource -ResourceType "skillsets" -ResourceName $skillsetName -ResourceBody $skillset
} catch {
    Write-Error "Failed to create skillset: $_"
    exit 1
}

# 3. Create Indexer
Write-Host "Step 3: Configuring Indexer..." -ForegroundColor Cyan
$indexer = @{
    name = $indexerName
    description = "Indexer for LEGO knowledge base documents"
    dataSourceName = $dataSourceName
    targetIndexName = $indexName
    skillsetName = $skillsetName
    schedule = @{
        interval = "PT1H"  # Run every hour
    }
    parameters = @{
        configuration = @{
            dataToExtract = "contentAndMetadata"
            parsingMode = "default"
            imageAction = "none"
            allowSkillsetToReadFileData = $true
        }
    }
    fieldMappings = @(
        @{
            sourceFieldName = "metadata_storage_name"
            targetFieldName = "fileName"
        },
        @{
            sourceFieldName = "metadata_storage_path"
            targetFieldName = "filePath"
        }
    )
}

try {
    Set-SearchResource -ResourceType "indexers" -ResourceName $indexerName -ResourceBody $indexer
} catch {
    Write-Error "Failed to create indexer: $_"
    exit 1
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "The indexer is now configured to:" -ForegroundColor Cyan
Write-Host "  1. Read documents from Azure Blob Storage container '$storageContainer'"
Write-Host "  2. Parse PDFs and Office documents"
Write-Host "  3. Split text into chunks of ~$ChunkSize characters with $ChunkOverlap overlap"
Write-Host "  4. Index chunks into '$indexName'"
Write-Host "  5. Run automatically every hour"
Write-Host ""
Write-Host "To run the indexer now:" -ForegroundColor Yellow
Write-Host "  .\3a-Run-Indexer.ps1"
Write-Host ""
Write-Host "To check indexer status:" -ForegroundColor Yellow
Write-Host "  .\4-Get-IndexerStatus.ps1"
