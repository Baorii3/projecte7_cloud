variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "table_name" {
  description = "Name of the DynamoDB table to access"
  type        = string
}

variable "source_file" {
  description = "Path to the Python source file"
  type        = string
}
