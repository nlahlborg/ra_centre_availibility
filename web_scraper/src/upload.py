"""
web_scraper.src.upload

This module provides functions to handle the uploading of scraped data to a MySQL database.
It includes functions to compare new data with existing data, prepare SQL transactions,
and save data to the database.
"""
from typing import List, Dict, Any
import json
import logging
import boto3
from botocore.exceptions import ClientError

DataObject = List[Dict[str, Any]]

logger = logging.getLogger("data_parser")

def upload_to_s3(
        data: dict,
        bucket_name: str,
        object_name: str,
        region_name: str='us-west-1'
        ) -> str:
    """
    Save the raw data aws s3
    """
    s3_client = boto3.client('s3', region_name=region_name)

    try:
        # Upload the JSON string as an object to S3.
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=json.dumps(data),
            ContentType='application/json',
            IfNoneMatch='*'
        )

        # Check the response for success.
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            successful = True
            error_details = None
        else:
            successful = False
            error_details = (
                "Upload failed with status code: "
                f"{response['ResponseMetadata']['HTTPStatusCode']}"
                )
        return successful, error_details

    except ClientError as e:
        # Handle S3 errors
        return False, f"Error uploading to S3: {e}"
    except Exception as e: # pylint: disable=broad-exception-caught
        # Handle other errors
        return False, f"An unexpected error occurred: {e}"
