import logging
from utils import (build_response, send_to_connection,
    get_message_table, get_body, build_message_index, put_message_to_db, broadcast_message,
                   validate_event, validate_body)

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
    try:
        validate_event(event)
        body = get_body(event)
        validate_body(body)
    except ValueError as v_er:
        return build_response(400, f'Event or body are not in correct shape or format:({v_er})')

    # Todo: fix hardcode once username is known
    username = 'Mate'
    put_message_to_db(username, body)
    logger.debug('Broadcasting message: {}'.format(body['content']))
    return broadcast_message(username, body, event)

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