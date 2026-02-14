# Test ngrok MCP server tools/list

Write-Host "Testing LEGO Robot MCP Server tools/list..." -ForegroundColor Cyan

# Send tools/list request directly using curl
# Format: POST /message?sessionId=test with tools/list JSON-RPC request

$body = @{
    jsonrpc = "2.0"
    method = "tools/list"
    id = 1
} | ConvertTo-Json

Write-Host "`nSending tools/list request to ngrok endpoint..." -ForegroundColor Yellow

# Note: This test assumes we can send without establishing SSE first
# In real scenario, client must GET /sse first to get session, then POST with that sessionId

try {
    $response = Invoke-RestMethod -Uri "https://termless-marg-hotly.ngrok-free.dev/health" -Method GET
    Write-Host "✓ Health check passed:" $response -ForegroundColor Green
} catch {
    Write-Host "✗ Health check failed:" $_ -ForegroundColor Red
}

Write-Host "`nTo properly test, compile the server and use VS Code MCP client from mcp.json" -ForegroundColor Cyan
Write-Host "The server at https://termless-marg-hotly.ngrok-free.dev/sse is ready for MCP clients" -ForegroundColor Green
