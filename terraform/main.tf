# 1. Define the Provider (AWS)
provider "aws" {
  region = "ap-south-1" 
}

# 2. Create the S3 Bucket for Images
resource "aws_s3_bucket" "campus_bucket" {
  bucket = "campus-lostfound-yash-repo" # Must be unique
}

# 3. Create the DynamoDB Table for Items
resource "aws_dynamodb_table" "items_table" {
  name         = "Items-Repo"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "itemId"

  attribute {
    name = "itemId"
    type = "S"
  }
}

# 4. Create the DynamoDB Table for Claims
resource "aws_dynamodb_table" "claims_table" {
  name         = "Claims-Repo"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "claimId"

  attribute {
    name = "claimId"
    type = "S"
  }
}