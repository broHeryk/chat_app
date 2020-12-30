import boto3
import json
import logging
import time
from utils import get_response
from handlers import handler_map

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


def _get_body(event):
    try:
        return json.loads(event.get("body", ""))
    except:
        logger.debug("event body could not be JSON decoded.")
        return {}


def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
                              endpoint_url="https://" + event["requestContext"]["domainName"] +
                                           "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
                                         Data=json.dumps(data).encode('utf-8'))


def connect_manager(event, context):
    """
    Handles connecting and disconnecting for the Websocket.
    Connect verifes the passed in token, and if successful,
    adds the connectionID to the database.
    Disconnect removes the connectionID from the database.
    """
    connection_id = event["requestContext"].get("connectionId")
    event_type = event["requestContext"]["eventType"]

    if not connection_id:
        logger.error("Failed: connectionId value not set.")
        return get_response(500, "connectionId value must not be empty or missing")

    if event_type not in handler_map:
        logger.error("Connection manager received unrecognized eventType '{}'" \
                     .format(event["requestContext"]["eventType"]))
        return get_response(500, "Unrecognized eventType. CONNECT and DISCONNECT are only available.")

    return handler_map[event_type](connection_id, logger)


def default_message(event, context):
    """
    Send back error when unrecognized WebSocket action is received.
    """
    logger.info("Unrecognized WebSocket action received.")
    return get_response(400, "Unrecognized WebSocket action.")


def get_recent_messages(event, context):
    """
    Return the 10 most recent chat messages.
    """
    connectionID = event["requestContext"].get("connectionId")
    logger.info("Retrieving most recent messages for CID '{}'" \
                .format(connectionID))

    # Ensure connectionID is set
    if not connectionID:
        logger.error("Failed: connectionId value not set.")
        return get_response(500, "connectionId value not set.")

    # Get the 10 most recent chat messages
    table = dynamodb.Table("serverless-chat_Messages")
    response = table.query(KeyConditionExpression="Room = :room",
                           ExpressionAttributeValues={":room": "general"},
                           Limit=10, ScanIndexForward=False)
    items = response.get("Items", [])

    # Extract the relevant data and order chronologically
    messages = [{"username": x["Username"], "content": x["Content"]}
                for x in items]
    messages.reverse()

    # Send them to the client who asked for it
    data = {"messages": messages}
    _send_to_connection(connectionID, data, event)

    return get_response(200, "Sent recent messages to '{}'." \
                         .format(connectionID))


def send_message(event, context):
    """
    When a message is sent on the socket, verify the passed in token,
    and forward it to all connections if successful.
    """
    logger.info("Message sent on WebSocket.")

    # Ensure all required fields were provided
    body = _get_body(event)
    if not isinstance(body, dict):
        logger.debug("Failed: message body not in dict format.")
        return get_response(400, "Message body not in dict format.")
    for attribute in ["token", "content"]:
        if attribute not in body:
            logger.debug("Failed: '{}' not in message dict." \
                         .format(attribute))
            return get_response(400, "'{}' not in message dict" \
                                 .format(attribute))

    # Verify the token
    try:
        payload = jwt.decode(body["token"], "FAKE_SECRET", algorithms="HS256")
        username = payload.get("username")
        logger.info("Verified JWT for '{}'".format(username))
    except:
        logger.debug("Failed: Token verification failed.")
        return get_response(400, "Token verification failed.")

    # Get the next message index
    # (Note: there is technically a race condition where two
    # users post at the same time and use the same index, but
    # accounting for that is outside the scope of this project)
    table = dynamodb.Table("serverless-chat_Messages")
    response = table.query(KeyConditionExpression="Room = :room",
                           ExpressionAttributeValues={":room": "general"},
                           Limit=1, ScanIndexForward=False)
    items = response.get("Items", [])
    index = items[0]["Index"] + 1 if len(items) > 0 else 0

    # Add the new message to the database
    timestamp = int(time.time())
    content = body["content"]
    table.put_item(Item={"Room": "general", "Index": index,
                         "Timestamp": timestamp, "Username": username,
                         "Content": content})

    # Get all current connections
    table = dynamodb.Table("serverless-chat_Connections")
    response = table.scan(ProjectionExpression="ConnectionID")
    items = response.get("Items", [])
    connections = [x["ConnectionID"] for x in items if "ConnectionID" in x]

    # Send the message data to all connections
    message = {"username": username, "content": content}
    logger.debug("Broadcasting message: {}".format(message))
    data = {"messages": [message]}
    for connectionID in connections:
        _send_to_connection(connectionID, data, event)
    return get_response(200, "Message sent to {} connections." \
                         .format(len(connections)))


