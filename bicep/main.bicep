// Main Bicep template for Azure AI Foundry and Content Understanding Service
targetScope = 'resourceGroup'

@description('Prefix for all resource names')
param resourcePrefix string = 'legobot'

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

// Storage account for Foundry and application data
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${resourcePrefix}${toLower(replace(foundryHubName, '-', ''))}st'
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

// Blob container for application data (sustineo)
resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource sustineoContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'sustineo'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault for Foundry
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${resourcePrefix}-${foundryHubName}-kv'
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
  name: '${resourcePrefix}-${foundryHubName}-insights'
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
  name: '${resourcePrefix}-${foundryHubName}-openai'
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
    customSubDomainName: '${resourcePrefix}-${foundryHubName}-openai'
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

// Cosmos DB account for storing configurations and data
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: '${resourcePrefix}-${toLower(replace(foundryHubName, '-', ''))}-cosmos'
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    publicNetworkAccess: 'Enabled'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

// Cosmos DB database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosDbAccount
  name: 'sustineo'
  properties: {
    resource: {
      id: 'sustineo'
    }
  }
}

// Cosmos DB container for voice configurations
resource voiceConfigContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: cosmosDatabase
  name: 'VoiceConfigurations'
  properties: {
    resource: {
      id: 'VoiceConfigurations'
      partitionKey: {
        paths: [
          '/id'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
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
output storageAccountName string = storageAccount.name
output storageAccountEndpoint string = storageAccount.properties.primaryEndpoints.blob
output cosmosDbAccountName string = cosmosDbAccount.name
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output applicationInsightsName string = applicationInsights.name
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString
