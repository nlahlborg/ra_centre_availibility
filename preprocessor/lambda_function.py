"""
web_scraper.lambda_function

This module defines the AWS Lambda handler function for the web scraping application
that retrieves availability data from the RA Centre website and optionally saves it
to a MySQL database. The lambda_handler function orchestrates the entire process,
including setting up the environment, establishing database connections, scraping data,
and saving new data to the database.

Functions:
    lambda_handler(event, context): The AWS Lambda handler function that runs the web
                                    scraping and data saving process.

Usage:
    Deploy this module as an AWS Lambda function to execute the web scraping and data
    saving process. The function can be triggered by various AWS services such as API
    Gateway, S3, or CloudWatch Events.

Example:
    def lambda_handler(event, context):
        # Your code here
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data that triggered the Lambda function.
        context (LambdaContext): The context object that provides information 
        about the invocation, function, and execution environment.

    Returns:
        dict: The response object.
    """
    # pylint: disable=unused-argument, logging-fstring-interpolation, import-outside-toplevel
    _, write_to_db = next(iter(event.items()))
    logger.info(f"Received event: {event}")
    from main import main
    logger.info("preparing to run main")
    rdb_response = main(write_to_db=write_to_db)

    # Your logic here
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"s3 response: {rdb_response}",
            "input": f"{event}"
        })
    }

    return response
