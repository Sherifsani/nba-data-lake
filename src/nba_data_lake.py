import boto3
import json
import time
import requests
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

api_key = os.getenv("SPORT_DATA_API_KEY")
nba_endpoint = os.getenv("NBA_ENDPOINT")

# AWS congifuration
region = "us-east-1"
bucket_name = "nba-data-lake-2025"
glue_database_name = "glue_nba_data_lake"
athena_output_location = f"s3://{bucket_name}/athena_results/"

# AWS clients
s3 = boto3.client("s3", region_name=region)
glue = boto3.client("glue", region_name=region)
athena = boto3.client("athena", region_name=region)

# Create S3 bucket
def create_bucket():
    '''create an s3 bucket for storing sports data'''
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        print(f"{bucket_name} is successfully created.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

# Create glue database
def create_glue_database():
    try:
        glue.create_database(
            DatabaseInput={
                'Name': glue_database_name,
                'Description': 'Glue database fot NBA sports analytics'
            }
        )
        print(f"Database {glue_database_name} is successfully created.")
    except Exception as e:
        print(f"Error creating database: {e}")

# Fetch NBA data
def fetch_nba_data():
    """Fetch NBA player data from sportsdata.io."""
    try:
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        response = requests.get(nba_endpoint, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Fetched NBA data successfully.")
        return response.json()  # Return JSON response
    except Exception as e:
        print(f"Error fetching NBA data: {e}")
        return []

# Convert to line delimitter
def convert_to_line_delimited_json(data):
    """Convert data to line-delimited JSON format."""
    print("Converting data to line-delimited JSON format...")
    return "\n".join([json.dumps(record) for record in data])

# Upload to S3
def upload_data_to_s3(data):
    """Upload NBA data to the S3 bucket."""
    try:
        # Convert data to line-delimited JSON
        line_delimited_data = convert_to_line_delimited_json(data)

        # Define S3 object key
        file_key = f"raw-data/nba_player_data.json{time.strftime('%Y-%m-%d-%H-%M')}"

        # Upload JSON data to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=line_delimited_data
        )
        print(f"Uploaded data to S3: {file_key}")
    except Exception as e:
        print(f"Error uploading data to S3: {e}")


def create_glue_table():
    """Create a Glue table for the data."""
    try:
        glue.create_table(
            DatabaseName=glue_database_name,
            TableInput={
                "Name": "nba_players",
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "PlayerID", "Type": "int"},
                        {"Name": "FirstName", "Type": "string"},
                        {"Name": "LastName", "Type": "string"},
                        {"Name": "Team", "Type": "string"},
                        {"Name": "Position", "Type": "string"},
                        {"Name": "Points", "Type": "int"}
                    ],
                    "Location": f"s3://{bucket_name}/raw-data/",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe"
                    },
                },
                "TableType": "EXTERNAL_TABLE",
            },
        )
        print(f"Glue table 'nba_players' created successfully.")
    except Exception as e:
        print(f"Error creating Glue table: {e}")

def configure_athena():
    """Set up Athena output location."""
    try:
        athena.start_query_execution(
            QueryString="CREATE DATABASE IF NOT EXISTS nba_analytics",
            QueryExecutionContext={"Database": glue_database_name},
            ResultConfiguration={"OutputLocation": athena_output_location},
        )
        print("Athena output location configured successfully.")
    except Exception as e:
        print(f"Error configuring Athena: {e}")


def main():
    print("Setting up data lake for NBA sports analytics...")
    create_bucket()
    time.sleep(5)  # Ensure bucket creation propagates
    create_glue_database()
    nba_data = fetch_nba_data()
    if nba_data:  # Only proceed if data was fetched successfully
        upload_data_to_s3(nba_data)
    create_glue_table()
    configure_athena()
    print("Data lake setup complete.")

if __name__ == "__main__":
    main()