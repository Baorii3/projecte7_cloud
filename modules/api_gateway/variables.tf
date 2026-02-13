variable "api_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "inventory-api"
}

variable "lambda_arn" {
  description = "ARN of the Lambda function to invoke"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "user_pool_client_id" {
  description = "The Client ID of the Cognito User Pool"
  type        = string
}

variable "user_pool_issuer" {
  description = "The Issuer URL of the Cognito User Pool"
  type        = string
}
