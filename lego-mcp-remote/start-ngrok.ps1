$env:IS_MOCK="true"
$env:NGROK_AUTHTOKEN="39bNJbabavOvM2lpNpzql9jbaBW_2mwVn6TsBtGa8d1a63oeb"
$env:PORT="3000"
Push-Location c:\repo\lego-agent\lego-mcp
node build/ngrok-server.js
Pop-Location
