# 1. Define the Provider (AWS)
provider "aws" {
  region = "ap-south-1" 
}

# 2. Create the DynamoDB Table for Users
resource "aws_dynamodb_table" "users_table" {
  name           = "Users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "email"

  attribute {
    name = "email"
    type = "S"
  }

  tags = {
    Project     = "Campus Lost and Found"
    Environment = "production"
  }
}