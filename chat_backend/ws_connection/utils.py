import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")


def get_connection_table():
    """ Returns dynamo table resource to store connection ids"""
    return dynamodb.Table(os.environ['CONNECTION_TABLE_NAME'])


def build_response(status_code, body):
    """Builds appropriate response for api gateway"""
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}

