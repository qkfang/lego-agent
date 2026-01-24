# LEGO Knowledge Base (lego-kb)

A knowledge base system for the LEGO robot that integrates with Azure AI Search and Azure Document Intelligence to store and retrieve information from PDF and Word documents.

## 🎯 Overview

This knowledge base project provides:
- Azure AI Search index for document storage and retrieval
- Azure Document Intelligence integration for document parsing
- PowerShell scripts for index management and document ingestion
- Support for PDF and Word document formats
- Integration capability with Foundry Agent via Foundry IQ

## 🏗️ Architecture

The knowledge base consists of:
- **Azure AI Search**: Vector and semantic search capabilities
- **Azure Document Intelligence**: Document parsing and extraction
- **Document Storage**: Local `docs/` folder for PDF and Word documents
- **Management Scripts**: PowerShell automation for index operations

## 📋 Prerequisites

- **PowerShell 7.0+** (PowerShell Core)
- **Azure Subscription** with the following services:
  - Azure AI Search service
  - Azure Document Intelligence service
- **Azure CLI** installed and configured
- **Az.Search PowerShell module** (optional, for enhanced operations)

## 🛠️ Setup

### 1. Install Azure CLI

```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Login to Azure

```powershell
az login
```

### 3. Configure Environment Variables

Create a `.env` file in the `lego-kb` directory with the following variables:

```env
# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-admin-api-key
AZURE_SEARCH_INDEX_NAME=lego-knowledge-base

# Azure Document Intelligence Configuration
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-doc-intelligence-key

# Optional: Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string
AZURE_STORAGE_CONTAINER=lego-documents
```

### 4. Add Documents

Place your PDF and Word documents in the `docs/` folder:

```
lego-kb/
└── docs/
    ├── manual.pdf
    ├── specifications.docx
    └── instructions.pdf
```

## 🚀 Usage

### Initialize AI Search Index

Create a new Azure AI Search index:

```powershell
cd lego-kb/scripts
.\Initialize-SearchIndex.ps1
```

This script will:
- Create the search index with appropriate schema
- Configure vector search capabilities
- Set up semantic search configurations

### Ingest Documents

Parse and ingest documents into the search index:

```powershell
cd lego-kb/scripts
.\Ingest-Documents.ps1
```

This script will:
- Scan the `docs/` folder for PDF and Word files
- Use Azure Document Intelligence to parse documents
- Extract text, tables, and structure
- Index documents in Azure AI Search

### Reset and Re-ingest

To clear the index and re-ingest all documents:

```powershell
cd lego-kb/scripts
.\Reset-Index.ps1
```

This script will:
- Delete all documents from the index
- Optionally delete and recreate the index
- Re-ingest all documents from the `docs/` folder

## 📁 Project Structure

```
lego-kb/
├── README.md                           # This file
├── .env                                # Environment configuration (not in git)
├── .env.example                        # Example environment configuration
├── docs/                               # Document storage
│   ├── manual.pdf
│   └── specifications.docx
└── scripts/                            # PowerShell automation scripts
    ├── Initialize-SearchIndex.ps1      # Create search index
    ├── Ingest-Documents.ps1            # Ingest documents
    └── Reset-Index.ps1                 # Reset and re-ingest
```

## 🔍 Search Index Schema

The search index includes the following fields:

- **id**: Unique document identifier
- **title**: Document title
- **content**: Full text content
- **documentType**: File type (PDF, DOCX)
- **filePath**: Original file path
- **pageCount**: Number of pages
- **uploadedAt**: Timestamp
- **metadata**: Additional document metadata
- **contentVector**: Vector embeddings for semantic search (optional)

## 🔗 Integration with Foundry Agent

The knowledge base is designed to integrate with Foundry Agent via Foundry IQ:

1. **Query Interface**: Use Azure AI Search REST API or SDK
2. **Semantic Search**: Leverage semantic ranking for better results
3. **Vector Search**: Support for vector-based retrieval (RAG patterns)
4. **Hybrid Search**: Combine keyword and semantic search

Example integration code will be provided in the main `lego-api` service.

## 🧪 Testing

To verify the setup:

```powershell
# Test Azure AI Search connection
az search service show --name your-search-service --resource-group your-rg

# Test Document Intelligence connection
az cognitiveservices account show --name your-doc-intelligence --resource-group your-rg
```

## 📚 API Examples

### Query the Knowledge Base

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

results = client.search(
    search_text="robot assembly instructions",
    select=["title", "content"],
    top=5
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Content: {result['content'][:200]}...")
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure Azure CLI is logged in and has proper permissions
2. **Index Creation Fails**: Check API key permissions (need admin key)
3. **Document Parsing Errors**: Verify Document Intelligence endpoint and key
4. **File Not Found**: Ensure documents are in the `docs/` folder

### Logs

Scripts output detailed logs to help troubleshoot issues. Check the console output for error messages and suggestions.

## 🤝 Contributing

To add new document types or enhance the knowledge base:

1. Update the index schema in `Initialize-SearchIndex.ps1`
2. Modify parsing logic in `Ingest-Documents.ps1`
3. Test with sample documents
4. Update this README

## 📄 License

This project is part of the LEGO Agent system and follows the same MIT License.

## 🆘 Support

For issues or questions:
- Review Azure AI Search documentation
- Check Azure Document Intelligence documentation
- Consult the main LEGO Agent repository

---

**Note**: Ensure documents stored in the knowledge base do not contain sensitive or proprietary information unless proper access controls are configured in Azure AI Search.
