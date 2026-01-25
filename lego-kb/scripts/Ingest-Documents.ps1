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
    [string[]]$FileTypes = @("*.pdf", "*.docx", "*.doc"),
    
    [Parameter(Mandatory=$false)]
    [int]$ChunkSize = 1000,
    
    [Parameter(Mandatory=$false)]
    [int]$ChunkOverlap = 200
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
        [string]$AccessToken
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
            "Authorization" = "Bearer $AccessToken"
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
                $headerValue = $webResponse.Headers[$headerName]
                # Handle both string and array values
                if ($headerValue -is [array]) {
                    $resultUrl = $headerValue[0]
                } else {
                    $resultUrl = $headerValue
                }
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
                "Authorization" = "Bearer $AccessToken"
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

# Function to split text into chunks with overlap
function Split-TextIntoChunks {
    param(
        [string]$Text,
        [int]$ChunkSize = 1000,
        [int]$Overlap = 200
    )
    
    if ([string]::IsNullOrWhiteSpace($Text)) {
        return @()
    }
    
    $chunks = @()
    $text = $Text.Trim()
    
    # If text is smaller than chunk size, return as single chunk
    if ($text.Length -le $ChunkSize) {
        return @(@{ 
            Content = $text
            StartIndex = 0
            EndIndex = $text.Length
            ChunkIndex = 0
        })
    }
    
    $startIndex = 0
    $chunkIndex = 0
    
    while ($startIndex -lt $text.Length) {
        $endIndex = [Math]::Min($startIndex + $ChunkSize, $text.Length)
        
        # Try to break at sentence or paragraph boundary if not at end
        if ($endIndex -lt $text.Length) {
            # Look for paragraph break first
            $paragraphBreak = $text.LastIndexOf("`n`n", $endIndex, [Math]::Min(200, $endIndex - $startIndex))
            if ($paragraphBreak -gt $startIndex + ($ChunkSize / 2)) {
                $endIndex = $paragraphBreak + 2
            } else {
                # Look for sentence break (. ! ?)
                $sentenceBreak = -1
                $searchStart = [Math]::Max($startIndex + ($ChunkSize / 2), $startIndex)
                $searchRange = $endIndex - $searchStart
                
                foreach ($delimiter in @(". ", "! ", "? ", ".\n", "!\n", "?\n")) {
                    $pos = $text.LastIndexOf($delimiter, $endIndex, $searchRange)
                    if ($pos -gt $sentenceBreak) {
                        $sentenceBreak = $pos + $delimiter.Length
                    }
                }
                
                if ($sentenceBreak -gt $startIndex) {
                    $endIndex = $sentenceBreak
                }
            }
        }
        
        $chunkText = $text.Substring($startIndex, $endIndex - $startIndex).Trim()
        
        if ($chunkText.Length -gt 0) {
            $chunks += @{
                Content = $chunkText
                StartIndex = $startIndex
                EndIndex = $endIndex
                ChunkIndex = $chunkIndex
            }
            $chunkIndex++
        }
        
        # Move start position with overlap
        $startIndex = $endIndex - $Overlap
        if ($startIndex -ge $text.Length - $Overlap) {
            break
        }
    }
    
    return $chunks
}

# Function to get Azure access token for managed identity authentication
function Get-AzureAccessToken {
    param(
        [string]$Resource = "https://search.azure.com"
    )
    
    try {
        # Use Azure CLI to get access token
        $tokenResponse = az account get-access-token --resource $Resource --output json 2>$null | ConvertFrom-Json
        
        if ($tokenResponse -and $tokenResponse.accessToken) {
            Write-Verbose "Successfully obtained access token for $Resource"
            return $tokenResponse.accessToken
        }
        
        throw "Failed to get access token from Azure CLI"
    }
    catch {
        Write-Error "Failed to get Azure access token. Make sure you are logged in with 'az login' and have appropriate permissions."
        Write-Error "Error: $_"
        return $null
    }
}

# Function to upload documents to Azure AI Search
function Add-DocumentsToIndex {
    param(
        [array]$Documents,
        [string]$Endpoint,
        [string]$IndexName,
        [string]$AccessToken
    )
    
    if ($Documents.Count -eq 0) {
        Write-Warning "No documents to upload"
        return
    }
    
    $uploadUrl = "$Endpoint/indexes/$IndexName/docs/index?api-version=2024-07-01"
    $headers = @{
        "Authorization" = "Bearer $AccessToken"
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
$indexName = $env:AZURE_SEARCH_INDEX_NAME
$docIntelligenceEndpoint = $env:AZURE_DOC_INTELLIGENCE_ENDPOINT

if (-not $searchEndpoint -or -not $indexName) {
    Write-Error "Required environment variables not set. Please configure AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_INDEX_NAME"
    exit 1
}

if (-not $docIntelligenceEndpoint) {
    Write-Error "Required environment variable not set. Please configure AZURE_DOC_INTELLIGENCE_ENDPOINT"
    exit 1
}

# Get access token for Azure AI Search using managed identity
Write-Host "Obtaining Azure access token for AI Search..." -ForegroundColor Cyan
$searchAccessToken = Get-AzureAccessToken -Resource "https://search.azure.com"
if (-not $searchAccessToken) {
    Write-Error "Failed to obtain access token for Azure AI Search. Ensure you are logged in with 'az login'."
    exit 1
}

# Get access token for Document Intelligence using managed identity
Write-Host "Obtaining Azure access token for Document Intelligence..." -ForegroundColor Cyan
$docIntelligenceAccessToken = Get-AzureAccessToken -Resource "https://cognitiveservices.azure.com"
if (-not $docIntelligenceAccessToken) {
    Write-Error "Failed to obtain access token for Document Intelligence. Ensure you are logged in with 'az login'."
    exit 1
}

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "Index Name: $indexName" -ForegroundColor Cyan
Write-Host "Doc Intelligence Endpoint: $docIntelligenceEndpoint" -ForegroundColor Cyan
Write-Host "Docs Path: $DocsPath" -ForegroundColor Cyan
Write-Host "Chunk Size: $ChunkSize characters" -ForegroundColor Cyan
Write-Host "Chunk Overlap: $ChunkOverlap characters" -ForegroundColor Cyan
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
$totalChunks = 0

foreach ($file in $allFiles) {
    $processedCount++
    Write-Host "[$processedCount/$($allFiles.Count)] Processing: $($file.Name)" -ForegroundColor Cyan
    
    try {
        # Analyze document with Document Intelligence
        $analysisResult = Invoke-DocumentAnalysis -FilePath $file.FullName -Endpoint $docIntelligenceEndpoint -AccessToken $docIntelligenceAccessToken
        
        if ($analysisResult) {
            # Extract text content
            $content = Get-TextFromAnalysis -AnalysisResult $analysisResult
            
            # Get page count
            $pageCount = 0
            if ($analysisResult.pages) {
                $pageCount = $analysisResult.pages.Count
            }
            
            # Split content into chunks
            $chunks = Split-TextIntoChunks -Text $content -ChunkSize $ChunkSize -Overlap $ChunkOverlap
            
            # Generate base ID using file path hash
            $filePathHash = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($file.FullName))).Replace('-','').Substring(0, 16)
            $baseId = [System.IO.Path]::GetFileNameWithoutExtension($file.Name) -replace '[^a-zA-Z0-9_-]', '_'
            
            # Create a document for each chunk
            foreach ($chunk in $chunks) {
                $chunkId = "$baseId-$filePathHash-chunk$($chunk.ChunkIndex)"
                
                $doc = @{
                    "@search.action" = "mergeOrUpload"
                    id = $chunkId
                    title = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                    content = $chunk.Content
                    documentType = $file.Extension.TrimStart('.')
                    filePath = $file.FullName
                    fileName = $file.Name
                    pageCount = $pageCount
                    chunkIndex = $chunk.ChunkIndex
                    totalChunks = $chunks.Count
                    uploadedAt = (Get-Date).ToUniversalTime().ToString("o")
                    category = "LEGO Robot Documentation"
                }
                
                $documentsToIndex += $doc
            }
            
            $totalChunks += $chunks.Count
            Write-Host "  ✓ Parsed successfully ($pageCount pages, $($content.Length) chars → $($chunks.Count) chunks)" -ForegroundColor Green
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
Write-Host "  Documents processed: $processedCount" -ForegroundColor White
Write-Host "  Documents successful: $($processedCount - $failedCount)" -ForegroundColor Green
Write-Host "  Documents failed: $failedCount" -ForegroundColor $(if ($failedCount -gt 0) { "Yellow" } else { "White" })
Write-Host "  Total chunks created: $totalChunks" -ForegroundColor Cyan
Write-Host ""

# Upload documents to search index
if ($documentsToIndex.Count -gt 0) {
    Write-Host "Uploading documents to Azure AI Search..." -ForegroundColor Cyan
    Add-DocumentsToIndex -Documents $documentsToIndex -Endpoint $searchEndpoint -IndexName $indexName -AccessToken $searchAccessToken
    Write-Host ""
    Write-Host "Ingestion complete! Documents are now searchable." -ForegroundColor Green
} else {
    Write-Warning "No documents to upload"
}
