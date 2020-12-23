import json
import boto3
import logging
import os
import time

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource("dynamodb")


def get_dynamo_table(table_name_env_var='TABLE_NAME'):
    return dynamodb.Table(os.environ.get(table_name_env_var))


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    table = get_dynamo_table()
    timestamp = int(time.time())
    table.put_item(Item={"connection_id":  "0",
            "Timestamp": timestamp, "Username": "ping-user",
            "Content": "PING!"})
    logger.debug("Item added to the database.")


    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello poc",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }
