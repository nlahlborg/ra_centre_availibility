import json
from web_scraper.main import main
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("running app with Python")
    result = main()
    return {
        'statusCode': 200,
        'body': json.dumps(f'number of rows written is {result}')
    }