provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"

  vpc_name             = "main-vpc"
  vpc_cidr             = "10.104.0.0/16"
  azs                  = ["us-east-1a", "us-east-1b"]
  public_subnets_cidr  = ["10.104.4.0/24", "10.104.5.0/24"]
  private_subnets_cidr = ["10.104.6.0/24", "10.104.7.0/24"]
}

module "dynamodb" {
  source = "./modules/dynamodb"

  table_name = "Inventory"
}

module "lambda" {
  source = "./modules/lambda"

  function_name = "InventoryCRUD"
  table_name    = module.dynamodb.table_name
  source_file   = "${path.module}/src/lambda/inventory.py"
}

module "cognito" {
  source          = "./modules/cognito"
  user_pool_name  = "InventoryUsers"
  client_name     = "InventoryAppClient"
}

module "api_gateway" {
  source               = "./modules/api_gateway"

  api_name             = "InventoryAPI"
  lambda_arn           = module.lambda.function_arn
  lambda_function_name = module.lambda.function_name

  user_pool_client_id = module.cognito.user_pool_client_id
  user_pool_issuer    = "https://${module.cognito.user_pool_endpoint}"
}

output "api_url" {
  description = "URL de la API Gateway"
  value       = module.api_gateway.api_endpoint
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.user_pool_client_id
}

module "frontend" {
  source      = "./modules/s3-website"
  bucket_name = "projecte7-cloud-inventory-frontend"
}

output "frontend_url" {
  description = "URL del Frontend"
  value       = module.frontend.website_endpoint
}
