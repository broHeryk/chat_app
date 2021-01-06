import json
import boto3
import os
import logging
import time

dynamodb = boto3.resource("dynamodb")


def get_body(event):
    try:
        return json.loads(event.get("body", ""))
    except:
        raise ValueError("event body could not be JSON decoded.")


def send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
                              endpoint_url="https://" + event["requestContext"]["domainName"] +
                                           "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
                                         Data=data)


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


def build_message_index(message_table):
    """Get the latest message from dynamo table and return the message index +1"""
    response = message_table.query(KeyConditionExpression='room = :room',
                                   ExpressionAttributeValues={':room': 'general'},
                                   Limit=1, ScanIndexForward=False)
    items = response.get('Items', [])
    index = items[0]['index'] + 1 if len(items) > 0 else 0
    return index


def put_message_to_db(username, body):
    """Composes message body and send it to dynamo table"""
    message_table = get_message_table()
    timestamp = int(time.time())
    content = body['content']
    message_table.put_item(Item={'room': 'general', 'index': build_message_index(message_table),
                                 'timestamp': timestamp, 'username': username,
                                 'content': content})


def build_message_data(username, body):
    """Create encoded api Gateway message"""
    data = {'messages': {'username': username, 'content': body['content']}}
    return json.dumps(data).encode('utf-8')


def broadcast_message(username, body, event):
    """Build message object and send it to all currently available connections"""
    # Get all current connections
    items = get_connection_table().scan(ProjectionExpression='connectionId').get('Items', [])
    connections = [x['connectionId'] for x in items if 'connectionId' in x]
    # Send the message data to all connections
    for connectionID in connections:
        send_to_connection(connectionID, build_message_data(username, body), event)
    return build_response(200,
                          'Message sent to {} connections.'.format(len(connections)))


def validate_event(ev):
    """
    Check if all required fields are included to event.
    Args:
        ev: dict - ApiGateway event
    Raises:
        ValueError: in case of absent required field or data
    """
    # Todo: to be filled in
    pass
    # event["requestContext"]["domainName"] +
    # "/" + event["requestContext"]["stage"]


def validate_body(body):
    """
    Check if all required fields are included to message body.
    Args:
        body: dict - body message sent ws connection
    Raises:
        ValueError: in case of absent required field or data
    """
    # Todo: to be filled in
    #body['content is needed']
    if not isinstance(body, dict):
        raise ValueError('Message body should be a valid dictionary')
        # logger.debug('Failed: message body not in dict format.')

    pass