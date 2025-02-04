terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "nba_function_role" {
  name = "nba_function_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

}

resource "aws_iam_policy" "nba_policy" {
  name        = "na_policy"
  description = "Policy for NBA function to create s3, glue crawlers and athena queries"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:CreateBucket",
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject",
            "s3:ListBucket"
          ],
          "Resource" : [
            "arn:aws:s3:::sports-analytics-data-lake",
            "arn:aws:s3:::sports-analytics-data-lake/*"
          ]
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "glue:CreateDatabase",
            "glue:DeleteDatabase",
            "glue:GetDatabase",
            "glue:GetDatabases",
            "glue:CreateTable",
            "glue:DeleteTable",
            "glue:GetTable",
            "glue:GetTables",
            "glue:UpdateTable"
          ],
          "Resource" : [
            "arn:aws:glue:*:*:catalog",
            "arn:aws:glue:*:*:database/glue_nba_data_lake",
            "arn:aws:glue:*:*:table/glue_nba_data_lake/*"
          ]
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "athena:StartQueryExecution",
            "athena:GetQueryExecution",
            "athena:GetQueryResults"
          ],
          "Resource" : "*"
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:PutObject"
          ],
          "Resource" : [
            "arn:aws:s3:::sports-analytics-data-lake/athena-results/*"
          ]
        }
      ]
    }


  )
}

resource "aws_iam_role_policy_attachment" "nba_function_policy_attachment" {
  role       = aws_iam_role.nba_function_role.name
  policy_arn = aws_iam_policy.nba_policy.arn
}

resource "aws_lambda_function" "nba_function" {
  function_name    = "nba_function"
  role             = aws_iam_role.nba_function_role.arn
  runtime          = "python3.12"
  handler          = "lambda.lambda_handler"
  filename         = "lambda/lambda.zip"
  source_code_hash = base64sha256("lambda/lambda.zip")

  environment {
    variables = {
      SPORT_DATA_API_KEY = "24b3cd5349c9471581dbe3a843cc36ec"
      NBA_ENDPOINT       = "https://api.sportsdata.io/v3/nba/scores/json/Players"
    }
  }
}
