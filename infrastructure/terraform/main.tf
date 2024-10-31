terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "security_platform" {
  name     = "security-platform-rg"
  location = "eastus"
  tags = {
    environment = "development"
    project     = "serverless-security-platform"
  }
}

resource "azurerm_key_vault" "platform_vault" {
  name                = "security-platform-kv"
  location            = azurerm_resource_group.security_platform.location
  resource_group_name = azurerm_resource_group.security_platform.name
  tenant_id          = data.azurerm_client_config.current.tenant_id
  sku_name           = "standard"
}