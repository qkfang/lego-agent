
az login --tenant 9d2116ce-afe6-4ce8-8bc3-c7c7b69856c2 --use-device-code
# az login --tenant 285f1bcc-8795-4823-b35e-c6f15d78e70b --use-device-code

az group create --name "rg-legobot" --location "eastus2"

az deployment group create --resource-group "rg-legobot" --template-file "main.bicep" --parameters "main.parameters.json" --debug


