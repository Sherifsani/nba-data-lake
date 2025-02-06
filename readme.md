# NBA Data Lake

## Overview

This project sets up a comprehensive data lake architecture for NBA player analytics using AWS services. It fetches NBA player data from sportsdata.io and creates a structured data pipeline using S3, AWS Glue, and Athena for storage and analysis. The `nba_data_lake.py` can be run in your cloudshell or your terminal (must be configured with AWS). Alternatively, you can create a lambda function, upload the code and run as you like which is exactly what I have done with terraform.

---

## Architecture
!(architecture diagram)[/src/diagram/image.png]

 - *IAC*: Terraform
 - *Storage*: Amazon S3
 - *Query engine*: Amazon Athena
 - *Data catalog*: Glue table and database
 - *Data source*: https://sportsdata.io

 ---

 ## Features
 - Creates an S3 bucket for data storage
 - Sets up a Glue database for data cataloging
 - Fetches NBA player data from sportsdata.io
 - Converts data to line-delimited JSON format
 - Uploads data to S3 with timestamped files
 - Creates a Glue table with predefined schema
 - Configures Athena for SQL querying

---

## Data Schema

The NBA players table includes the following columns:

 - PlayerID (int)
 - FirstName (string)
 - LastName (string)
 - Team (string)
 - Position (string)
 - Points (int)

---

## Notes

 - The script includes a 5-second delay after bucket creation to ensure AWS propagation
 - Data files are timestamped for version control
 - Uses external tables in Glue for better data lake management
 - Implements the OpenX JSON SerDe for JSON parsing in Glue