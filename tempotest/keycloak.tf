# SPDX-FileCopyrightText: Magenta ApS
# SPDX-License-Identifier: MPL-2.0

terraform {
  backend "http" {}
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = "3.6.0"
    }
  }
}

variable "keycloak_admin_password" {
  type        = string
  description = "Keycloak admin password"
}

variable "keycloak_url" {
  type        = string
  description = "Keycloak URL"
}

variable "keycloak_tempotest_client_secret" {
  type        = string
  description = "Keycloak client secret for the performance test client"
  sensitive   = true
}

provider "keycloak" {
  client_id = "admin-cli"
  username  = "admin"
  password  = var.keycloak_admin_password
  url       = var.keycloak_url
}

# Realms
data "keycloak_realm" "mo" {
  realm = "mo"
}

# Clients
resource "keycloak_openid_client" "tempotest" {
  realm_id  = data.keycloak_realm.mo.id
  client_id = "tempotest"
  enabled   = true

  name                     = "TEMPOTEST"
  access_type              = "CONFIDENTIAL"
  service_accounts_enabled = true
  access_token_lifespan    = 3600

  client_secret = var.keycloak_tempotest_client_secret
}
