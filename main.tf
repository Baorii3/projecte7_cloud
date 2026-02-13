provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"

  vpc_name             = "main-vpc"
  vpc_cidr             = "10.0.104.0/16"
  azs                  = ["us-east-1a", "us-east-1b"]
  public_subnets_cidr  = ["10.0.104.0/24", "10.0.104.1/24"]
  private_subnets_cidr = ["10.0.104.2/24", "10.0.104.3/24"]
}

module "dynamodb" {
  source = "./modules/dynamodb"

  table_name = "Inventory"
}
