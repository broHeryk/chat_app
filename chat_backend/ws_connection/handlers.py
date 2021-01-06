from utils import get_connection_table, build_response


def connect(connection_id, username, logger):
    """Connect client to chat by adding new connection id to db"""
    logger.info("Connect requested (CID: {})".format(connection_id))
    # Add connectionID to the database
    table = get_connection_table()
    table.put_item(Item={"connectionId": connection_id, 'username': username})
    return build_response(200, "Connect successful.")


def disconnect(connection_id, username, logger):
    """Remove client from connection table.  """
    logger.info("Disconnect requested (CID: {})".format(connection_id))
    # Remove the connectionID from the database
    table = get_connection_table()
    table.delete_item(Key={"connectionId": connection_id})
    return build_response(200, "Disconnect successful.")


handler_map = {
    'CONNECT': connect,
    'DISCONNECT': disconnect
}