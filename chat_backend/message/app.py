import logging
import time
from utils import build_response, send_to_connection, get_message_table, get_body, get_connection_table

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


def default_message(event, context):
    """
    Send back error when unrecognized WebSocket action is received.
    """
    logger.info("Unrecognized WebSocket action received.")
    return build_response(400, "Unrecognized WebSocket action.")


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
        return build_response(500, "connectionId value not set.")

    # Get the 10 most recent chat messages
    table = get_message_table()
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
    send_to_connection(connectionID, data, event)

    return build_response(200, "Sent recent messages to '{}'." \
                         .format(connectionID))


def send_message(event, context):
    """
    When a message is sent on the socket, verify the passed in token,
    and forward it to all connections if successful.
    """
    logger.info('Message sent on WebSocket.')

    # Ensure all required fields were provided
    body = get_body(event, logger)
    if not isinstance(body, dict):
        logger.debug('Failed: message body not in dict format.')
        return build_response(400, 'Message body not in dict format.')
    # for attribute in ['token', 'content']:
    #     if attribute not in body:
    #         logger.debug('Failed: '{}' not in message dict.' \
    #                      .format(attribute))
    #         return build_response(400, "'{}' not in message dict" \
    #                              .format(attribute))

    # Verify the token
    # try:
    #     payload = jwt.decode(body["token"], "FAKE_SECRET", algorithms="HS256")
    #     username = payload.get("username")
    #     logger.info("Verified JWT for '{}'".format(username))
    # except:
    #     logger.debug("Failed: Token verification failed.")
    #     return build_response(400, "Token verification failed.")

    # Get the next message index
    # (Note: there is technically a race condition where two
    # users post at the same time and use the same index, but
    # accounting for that is outside the scope of this project)
    message_table = get_message_table()
    response = message_table.query(KeyConditionExpression='room = :room',
                                   ExpressionAttributeValues={':room': 'general'},
                                   Limit=1, ScanIndexForward=False)
    items = response.get('Items', [])
    print(items)
    index = items[0]['index'] + 1 if len(items) > 0 else 0
    # Todo: fix hardcode once username is known
    username = 'Mate'
    # Add the new message to the database
    timestamp = int(time.time())
    content = body['content']
    message_table.put_item(Item={'room': 'general', 'index': index,
                                 'timestamp': timestamp, 'username': username,
                                 'content': content})

    # Get all current connections
    table = get_connection_table()
    response = table.scan(ProjectionExpression='connectionId')
    items = response.get('Items', [])
    connections = [x['connectionId'] for x in items if 'connectionId' in x]

    # Send the message data to all connections
    message = {'username': username, 'content': content}
    logger.debug('Broadcasting message: {}'.format(message))
    data = {'messages': [message]}
    for connectionID in connections:
        send_to_connection(connectionID, data, event)
    return build_response(200,
                          'Message sent to {} connections.'.format(len(connections)))


