resource "aws_dynamodb_table" "inventory" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "itemId"

  attribute {
    name = "itemId"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  global_secondary_index {
    name               = "categoryIndex"
    hash_key           = "category"
    range_key          = "name"
    projection_type    = "ALL"
  }

  tags = {
    Name = var.table_name
  }
}
