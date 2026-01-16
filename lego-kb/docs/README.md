# LEGO Knowledge Base Documents

This folder contains PDF and Word documents that will be indexed in Azure AI Search.

## Supported File Types

- **PDF files** (*.pdf)
- **Word documents** (*.docx, *.doc)

## Adding Documents

1. Place your PDF or Word documents in this folder
2. Run the ingestion script from the `scripts` folder:
   ```powershell
   cd ../scripts
   .\Ingest-Documents.ps1
   ```

## Document Organization

You can organize documents in subfolders if needed. The ingestion script will scan this folder for supported file types.

## Examples

Example documents you might add:
- LEGO robot assembly manuals
- Technical specifications
- Programming guides
- Troubleshooting documentation
- User manuals
- API documentation

## Notes

- Documents should not contain sensitive or proprietary information unless proper access controls are configured in Azure AI Search
- Large documents may take longer to process with Azure Document Intelligence
- The ingestion script will extract text, tables, and structure from documents
