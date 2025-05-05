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
        all_keys_returned = False
        object_names = []
        max_object_names = 10000
        marker = ""
        idx = 0
        while not all_keys_returned and len(object_names) < max_object_names and idx < 100:
            idx += 1 #loop exit safety
            response = client.list_objects(
                Bucket=bucket,
                MaxKeys = 1000,
                Marker=marker,
                Prefix='raw_centre_raw_'
            )
            if 'Contents' in response:
                partial_object_names = sorted([x.get('Key') for x in response["Contents"]])
                object_names += partial_object_names

                if len(partial_object_names) < 1000:
                    all_keys_returned = True
                else:
                    marker = partial_object_names[-1]

            else:
                all_keys_returned = True

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
