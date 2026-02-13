output "vpc_id" {
  value = module.vpc.vpc_id
}

output "dynamodb_table_name" {
  value = module.dynamodb.table_name
}
