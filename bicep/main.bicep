// Main Bicep template for Azure AI Foundry and Content Understanding Service
targetScope = 'resourceGroup'

@description('Name of the Azure AI Foundry hub')
param foundryHubName string

@description('Name of the Azure AI Foundry project')
param foundryProjectName string

@description('Name of the Content Understanding service')
param contentUnderstandingName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('SKU for Content Understanding service')
@allowed([
  'S0'
  'F0'
])
param contentUnderstandingSku string = 'S0'

@description('Tags to apply to all resources')
param tags object = {
  environment: 'production'
  project: 'lego-agent'
  component: 'video-agent'
}

// Storage account for Foundry
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${toLower(replace(foundryHubName, '-', ''))}storage'
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// Key Vault for Foundry
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${foundryHubName}-kv'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enableRbacAuthorization: true
  }
}

// Application Insights for monitoring
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${foundryHubName}-insights'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Azure AI Foundry Hub (v2 - not classic)
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: foundryHubName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  kind: 'Hub'
  properties: {
    friendlyName: foundryHubName
    description: 'Azure AI Foundry Hub for LEGO Agent'
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    applicationInsights: applicationInsights.id
    publicNetworkAccess: 'Enabled'
    v1LegacyMode: false
  }
}

// Azure AI Foundry Project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: foundryProjectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  kind: 'Project'
  properties: {
    friendlyName: foundryProjectName
    description: 'Azure AI Foundry Project for Video Agent'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

// Content Understanding Service
resource contentUnderstanding 'Microsoft.CognitiveServices/accounts@2024-04-01' = {
  name: contentUnderstandingName
  location: location
  tags: tags
  sku: {
    name: contentUnderstandingSku
  }
  kind: 'ContentUnderstanding'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: contentUnderstandingName
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
}

// OpenAI service for Foundry models
resource openAI 'Microsoft.CognitiveServices/accounts@2024-04-01' = {
  name: '${foundryHubName}-openai'
  location: location
  tags: tags
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: '${foundryHubName}-openai'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// GPT-4o deployment for agent
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01' = {
  parent: openAI
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

// Outputs
output foundryHubId string = aiHub.id
output foundryHubName string = aiHub.name
output foundryProjectId string = aiProject.id
output foundryProjectName string = aiProject.name
output contentUnderstandingId string = contentUnderstanding.id
output contentUnderstandingName string = contentUnderstanding.name
output contentUnderstandingEndpoint string = contentUnderstanding.properties.endpoint
output openAIEndpoint string = openAI.properties.endpoint
output openAIId string = openAI.id
