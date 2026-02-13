output "function_arn" {
  value = aws_lambda_function.crud_function.arn
}

output "function_name" {
  value = aws_lambda_function.crud_function.function_name
}
