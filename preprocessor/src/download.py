"""
functions to get data from s3
"""
import json
from json import JSONDecodeError
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_object_names(
        bucket,
        region_name: str='us-west-1'
        ):
    """
    get the object names from the listed s3 bucket, sorted ascending
    """

    try:
        client = boto3.client('s3', region_name=region_name)
        response = client.list_objects(
            Bucket=bucket,
            Prefix='raw_centre_raw_'
        )

        if 'Contents' in response:
            object_names = [x.get('Key') for x in response["Contents"]]
        else:
            object_names = []

        return sorted(object_names)

    except ClientError as e:
        logger.error(f"Error reading from S3: {e}")
        return []

def get_json_data(bucket, object_name, region_name: str='us-west-1'):
    """
    get the specified object from s3
    """

    try:
        client = boto3.client('s3', region_name=region_name)

        response = client.get_object(
            Bucket=bucket,
            Key=object_name,
            )

        json_data = json.load(response.get("Body"))
        return json_data

    except ClientError as e:
        logger.error(f"Error reading from S3: {e}")
        return None
    except JSONDecodeError as e:
        logger.exception(f"Error decoding json: {e}")
        return None
