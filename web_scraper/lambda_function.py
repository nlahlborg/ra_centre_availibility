import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data that triggered the Lambda function.
        context (LambdaContext): The context object that provides information about the invocation, function, and execution environment.

    Returns:
        dict: The response object.
    """
    _, write_to_db = next(iter(event.items())) 
    logger.info(f"Received event: {event}")
    from main import main
    logger.info("preparing to run main")
    n_rows = main(write_to_db=write_to_db)

    # Your logic here
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Wrote {n_rows} to DB",
            "input": f"{event}"
        })
    }

    return response