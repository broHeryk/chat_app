import boto3
import json
import logging
from utils import build_response
from handlers import handler_map

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
                              endpoint_url="https://" + event["requestContext"]["domainName"] +
                                           "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
                                         Data=json.dumps(data).encode('utf-8'))


def connection_manager(event, context):
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
        return build_response(500, "connectionId value must not be empty or missing")

    if event_type not in handler_map:
        logger.error("Connection manager received unrecognized eventType '{}'" \
                     .format(event["requestContext"]["eventType"]))
        return build_response(500, "Unrecognized eventType. CONNECT and DISCONNECT are only available.")

    return handler_map[event_type](connection_id, logger)

