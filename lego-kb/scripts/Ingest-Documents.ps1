<#
.SYNOPSIS
    Ingest documents into Azure AI Search using Azure Document Intelligence

.DESCRIPTION
    This script scans the docs folder for PDF and Word documents, uses Azure
    Document Intelligence to parse them, and indexes the content in Azure AI Search.

.EXAMPLE
    .\Ingest-Documents.ps1

.EXAMPLE
    .\Ingest-Documents.ps1 -DocsPath "C:\path\to\docs"

.NOTES
    Requires environment variables to be set in .env file or system environment
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DocsPath = "../docs",
    
    [Parameter(Mandatory=$false)]
    [string]$EnvFile = "../.env",
    
    [Parameter(Mandatory=$false)]
    [string[]]$FileTypes = @("*.pdf", "*.docx", "*.doc")
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

# Function to analyze document with Azure Document Intelligence
function Invoke-DocumentAnalysis {
    param(
        [string]$FilePath,
        [string]$Endpoint,
        [string]$ApiKey
    )
    
    try {
        # Read file as bytes
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        
        # Determine content type
        $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
        $contentType = switch ($extension) {
            ".pdf" { "application/pdf" }
            ".docx" { "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }
            ".doc" { "application/msword" }
            default { "application/octet-stream" }
        }
        
        Write-Verbose "Analyzing document: $FilePath ($contentType)"
        
        # Start document analysis (use Invoke-WebRequest to capture headers)
        $analyzeUrl = "$Endpoint/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31"
        $headers = @{
            "Ocp-Apim-Subscription-Key" = $ApiKey
            "Content-Type" = $contentType
        }
        
        # Use Invoke-WebRequest to get both response and headers
        $webResponse = Invoke-WebRequest -Uri $analyzeUrl -Method Post -Headers $headers -Body $fileBytes -ErrorAction Stop
        
        # Check HTTP status
        if ($webResponse.StatusCode -lt 200 -or $webResponse.StatusCode -ge 300) {
            throw "Document analysis request failed with status code: $($webResponse.StatusCode)"
        }
        
        # Get operation location from response headers (case-insensitive lookup)
        $resultUrl = $null
        foreach ($headerName in $webResponse.Headers.Keys) {
            if ($headerName -eq 'Operation-Location') {
                $resultUrl = $webResponse.Headers[$headerName]
                break
            }
        }
        
        if (-not $resultUrl) {
            throw "Operation-Location header not found in response"
        }
        
        Write-Verbose "Polling for results at: $resultUrl"
        
        $maxAttempts = 30
        $attempt = 0
        $result = $null
        
        do {
            Start-Sleep -Seconds 2
            $attempt++
            
            $getHeaders = @{
                "Ocp-Apim-Subscription-Key" = $ApiKey
            }
            
            $result = Invoke-RestMethod -Uri $resultUrl -Method Get -Headers $getHeaders
            $status = $result.status
            
            Write-Verbose "Attempt $attempt/$maxAttempts - Status: $status"
            
            if ($status -eq "succeeded") {
                return $result.analyzeResult
            } elseif ($status -eq "failed") {
                throw "Document analysis failed: $($result.error.message)"
            }
            
        } while ($status -ne "succeeded" -and $attempt -lt $maxAttempts)
        
        if ($attempt -ge $maxAttempts) {
            throw "Document analysis timed out after $maxAttempts attempts"
        }
        
        return $result.analyzeResult
        
    } catch {
        Write-Warning "Failed to analyze document $FilePath : $_"
        return $null
    }
}

# Function to extract text from analysis result
function Get-TextFromAnalysis {
    param($AnalysisResult)
    
    if (-not $AnalysisResult) {
        return ""
    }
    
    # Extract text content
    $content = ""
    
    if ($AnalysisResult.content) {
        $content = $AnalysisResult.content
    } elseif ($AnalysisResult.pages) {
        # Fallback: concatenate text from all pages
        foreach ($page in $AnalysisResult.pages) {
            if ($page.lines) {
                foreach ($line in $page.lines) {
                    $content += $line.content + "`n"
                }
            }
        }
    }
    
    return $content
}

# Function to upload documents to Azure AI Search
function Add-DocumentsToIndex {
    param(
        [array]$Documents,
        [string]$Endpoint,
        [string]$IndexName,
        [string]$ApiKey
    )
    
    if ($Documents.Count -eq 0) {
        Write-Warning "No documents to upload"
        return
    }
    
    $uploadUrl = "$Endpoint/indexes/$IndexName/docs/index?api-version=2023-11-01"
    $headers = @{
        "api-key" = $ApiKey
        "Content-Type" = "application/json"
    }
    
    $batch = @{
        value = $Documents
    }
    
    $batchJson = $batch | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri $uploadUrl -Method Post -Headers $headers -Body $batchJson
        
        $successCount = ($response.value | Where-Object { $_.status -eq $true }).Count
        Write-Host "✓ Uploaded $successCount documents successfully" -ForegroundColor Green
        
        $failedDocs = $response.value | Where-Object { $_.status -eq $false }
        if ($failedDocs.Count -gt 0) {
            Write-Warning "Failed to upload $($failedDocs.Count) documents"
            foreach ($failed in $failedDocs) {
                Write-Warning "  - $($failed.key): $($failed.errorMessage)"
            }
        }
        
    } catch {
        Write-Error "Failed to upload documents: $_"
        if ($_.ErrorDetails.Message) {
            Write-Error "Details: $($_.ErrorDetails.Message)"
        }
    }
}

# Main script
Write-Host "=== Azure AI Search Document Ingestion ===" -ForegroundColor Green
Write-Host ""

# Load environment variables
Import-EnvFile -Path $EnvFile

# Get required environment variables
$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$searchApiKey = $env:AZURE_SEARCH_API_KEY
$indexName = $env:AZURE_SEARCH_INDEX_NAME
$docIntelligenceEndpoint = $env:AZURE_DOC_INTELLIGENCE_ENDPOINT
$docIntelligenceKey = $env:AZURE_DOC_INTELLIGENCE_KEY

if (-not $searchEndpoint -or -not $searchApiKey -or -not $indexName) {
    Write-Error "Required environment variables not set. Please configure AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, and AZURE_SEARCH_INDEX_NAME"
    exit 1
}

if (-not $docIntelligenceEndpoint -or -not $docIntelligenceKey) {
    Write-Error "Required environment variables not set. Please configure AZURE_DOC_INTELLIGENCE_ENDPOINT and AZURE_DOC_INTELLIGENCE_KEY"
    exit 1
}

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Index Name: $indexName" -ForegroundColor Cyan
Write-Host "Doc Intelligence Endpoint: $docIntelligenceEndpoint" -ForegroundColor Cyan
Write-Host "Docs Path: $DocsPath" -ForegroundColor Cyan
Write-Host ""

# Check if docs folder exists
if (-not (Test-Path $DocsPath)) {
    Write-Error "Docs folder not found at: $DocsPath"
    exit 1
}

# Find all documents
$allFiles = @()
foreach ($fileType in $FileTypes) {
    $files = Get-ChildItem -Path $DocsPath -Filter $fileType -File
    $allFiles += $files
}

if ($allFiles.Count -eq 0) {
    Write-Warning "No documents found in $DocsPath"
    Write-Host "Supported file types: $($FileTypes -join ', ')" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($allFiles.Count) document(s) to process" -ForegroundColor Cyan
Write-Host ""

# Process each document
$documentsToIndex = @()
$processedCount = 0
$failedCount = 0

foreach ($file in $allFiles) {
    $processedCount++
    Write-Host "[$processedCount/$($allFiles.Count)] Processing: $($file.Name)" -ForegroundColor Cyan
    
    try {
        # Analyze document with Document Intelligence
        $analysisResult = Invoke-DocumentAnalysis -FilePath $file.FullName -Endpoint $docIntelligenceEndpoint -ApiKey $docIntelligenceKey
        
        if ($analysisResult) {
            # Extract text content
            $content = Get-TextFromAnalysis -AnalysisResult $analysisResult
            
            # Get page count
            $pageCount = 0
            if ($analysisResult.pages) {
                $pageCount = $analysisResult.pages.Count
            }
            
            # Create document object for indexing
            # Generate unique ID using file path hash to avoid duplicates
            $filePathHash = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($file.FullName))).Replace('-','').Substring(0, 16)
            $baseId = [System.IO.Path]::GetFileNameWithoutExtension($file.Name) -replace '[^a-zA-Z0-9_-]', '_'
            $uniqueId = "$baseId-$filePathHash"
            
            $doc = @{
                "@search.action" = "mergeOrUpload"
                id = $uniqueId
                title = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                content = $content
                documentType = $file.Extension.TrimStart('.')
                filePath = $file.FullName
                fileName = $file.Name
                pageCount = $pageCount
                uploadedAt = (Get-Date).ToUniversalTime().ToString("o")
                category = "LEGO Robot Documentation"
            }
            
            $documentsToIndex += $doc
            
            Write-Host "  ✓ Parsed successfully ($pageCount pages, $($content.Length) characters)" -ForegroundColor Green
        } else {
            $failedCount++
            Write-Warning "  ✗ Failed to analyze document"
        }
        
    } catch {
        $failedCount++
        Write-Warning "  ✗ Error processing document: $_"
    }
}

Write-Host ""
Write-Host "Processing complete:" -ForegroundColor Cyan
Write-Host "  Processed: $processedCount" -ForegroundColor White
Write-Host "  Successful: $($documentsToIndex.Count)" -ForegroundColor Green
Write-Host "  Failed: $failedCount" -ForegroundColor $(if ($failedCount -gt 0) { "Yellow" } else { "White" })
Write-Host ""

# Upload documents to search index
if ($documentsToIndex.Count -gt 0) {
    Write-Host "Uploading documents to Azure AI Search..." -ForegroundColor Cyan
    Add-DocumentsToIndex -Documents $documentsToIndex -Endpoint $searchEndpoint -IndexName $indexName -ApiKey $searchApiKey
    Write-Host ""
    Write-Host "Ingestion complete! Documents are now searchable." -ForegroundColor Green
} else {
    Write-Warning "No documents to upload"
}
