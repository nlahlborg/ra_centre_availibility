import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event):
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data that triggered the Lambda function.
        context (LambdaContext): The context object that provides information about the invocation, function, and execution environment.

    Returns:
        dict: The response object.
    """
    logger.info("Received event: %s", json.dumps(event))
    from main import main
    logger.info("preparing to run main")
    n_rows = main(write_to_db=event)

    # Your logic here
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Wrote {n_rows} to DB",
            "input": event
        })
    }

    return response