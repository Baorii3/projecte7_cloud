data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = var.source_file
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "crud_function" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = var.function_name
  role          = data.aws_iam_role.lab_role.arn
  handler       = "inventory.lambda_handler"
  runtime       = "python3.9"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }
}
