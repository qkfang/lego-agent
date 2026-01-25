// Main Bicep template for Azure AI Foundry and Content Understanding Service
targetScope = 'resourceGroup'

@description('Prefix for all resource names')
param resourcePrefix string = 'legobot'

@description('Location for all resources')
param location string = resourceGroup().location


// Storage account for Foundry and application data
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${resourcePrefix}st'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
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

resource legoDocumentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'lego-documents'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault for Foundry
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${resourcePrefix}-kv'
  location: location
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
  name: '${resourcePrefix}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Azure AI Search for knowledge base and RAG scenarios
resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: '${resourcePrefix}-search'
  location: location
  sku: {
    name: 'basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    semanticSearch: 'free'
  }
}

// Azure Document Intelligence for document processing
resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${resourcePrefix}-docint'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'FormRecognizer'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: '${resourcePrefix}-docint'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
}

// Azure AI Foundry Hub (v2 - not classic)
resource aiHub 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
  name: '${resourcePrefix}-foundry'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: '${resourcePrefix}-foundry'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Azure AI Foundry Project
// resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-10-01-preview' = {
//   parent: aiHub
//   name: '${resourcePrefix}-project'
//   location: location
//   identity: {
//     type: 'SystemAssigned'
//   }
// }


// // Content Understanding Service
// resource contentUnderstanding 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
//   name: '${resourcePrefix}-cu'
//   location: location
//   tags: tags
//   sku: {
//     name: contentUnderstandingSku
//   }
//   kind: 'ContentUnderstanding'
//   identity: {
//     type: 'SystemAssigned'
//   }
//   properties: {
//     customSubDomainName: '${resourcePrefix}-cu'
//     publicNetworkAccess: 'Enabled'
//     networkAcls: {
//       defaultAction: 'Allow'
//     }
//     disableLocalAuth: false
//   }
// }

// OpenAI service for Foundry models
// resource openAI 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
//   name: '${resourcePrefix}-${foundryHubName}-openai'
//   location: location
//   tags: tags
//   sku: {
//     name: 'S0'
//   }
//   kind: 'OpenAI'
//   identity: {
//     type: 'SystemAssigned'
//   }
//   properties: {
//     customSubDomainName: '${resourcePrefix}-${foundryHubName}-openai'
//     publicNetworkAccess: 'Enabled'
//     networkAcls: {
//       defaultAction: 'Allow'
//     }
//   }
// }

// GPT-4o deployment for agent
// resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
//   parent: openAI
//   name: 'gpt-4o'
//   sku: {
//     name: 'Standard'
//     capacity: 10
//   }
//   properties: {
//     model: {
//       format: 'OpenAI'
//       name: 'gpt-4o'
//       version: '2024-05-13'
//     }
//     versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
//   }
// }

// Azure Custom Vision - Training resource
resource customVisionTraining 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${resourcePrefix}-cv-training'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'CustomVision.Training'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: '${resourcePrefix}-cv-training'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
}

// Azure Custom Vision - Prediction resource
resource customVisionPrediction 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${resourcePrefix}-cv-prediction'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'CustomVision.Prediction'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: '${resourcePrefix}-cv-prediction'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
}

// Cosmos DB account for storing configurations and data
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: '${resourcePrefix}-cosmos'
  location: location
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
