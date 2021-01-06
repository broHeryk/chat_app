import boto3
import os
import json
import uuid

dynamodb = boto3.resource("dynamodb")


def get_connection_table():
    """ Returns dynamo table resource to store connection ids"""
    return dynamodb.Table(os.environ['CONNECTION_TABLE_NAME'])


def build_response(status_code, body):
    """Builds appropriate response for api gateway"""
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}


def get_username(event):
    """Gets username from query params if included. Otherwise generate uuid"""
    usr_nm = event.get('queryStringParameters', {}).get('username')
    if not usr_nm:
        usr_nm = f'user_{uuid.uuid1()}'
    return usr_nm
