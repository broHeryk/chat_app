import json
import boto3
import os
import logging

dynamodb = boto3.resource("dynamodb")


def get_body(event, logger=logging.getLogger('default')):
    try:
        return json.loads(event.get("body", ""))
    except:
        logger.debug("event body could not be JSON decoded.")
        return {}


def send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
                              endpoint_url="https://" + event["requestContext"]["domainName"] +
                                           "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
                                         Data=json.dumps(data).encode('utf-8'))


def build_response(status_code, body):
    """Builds appropriate response for api gateway"""
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}


def get_connection_table():
    """ Returns dynamo table resource to store connection ids"""
    return dynamodb.Table(os.environ['CONNECTION_TABLE_NAME'])


def get_message_table():
    """ Returns dynamo table resource to store connection ids"""
    return dynamodb.Table(os.environ['MESSAGE_TABLE_NAME'])


