import os
from chat_backend.ws_connection.app import connection_manager
from unittest import mock
from chat_backend.tests.unit.test_data import username_data, web_socket_connect_event as ws_conn_ev
import unittest


@mock.patch.dict(os.environ, {"CONNECTION_TABLE_NAME": "testtable"})
class TestWSConnection(unittest.TestCase):

    @mock.patch('utils.dynamodb.Table')
    @mock.patch('uuid.uuid1', lambda: '42')
    def test_connection_successful(self, dynamo_mock):
        # Given: Api Gateway event with connection Id
        conn_id = ws_conn_ev["requestContext"].get("connectionId")
        # Given: Table name is passed to environment variables
        table_name = os.environ.get('CONNECTION_TABLE_NAME')
        # When: connect function is called with a valid event
        response = connection_manager(ws_conn_ev, "")
        # Then: 200 is returned
        self.assertEqual(response['statusCode'], 200)
        # Then: Dynamo resource is called to pull table with correct table name
        dynamo_mock.assert_called_once_with(table_name)
        target_table = dynamo_mock.return_value
        # Then: The correct value of connection id is put to the table
        target_table.put_item.assert_called_once_with(**{'Item': {'connectionId': conn_id, 'username': 'user_42'}})

    @mock.patch.dict(ws_conn_ev, username_data)
    @mock.patch('utils.dynamodb.Table')
    def test_connection_with_username_passed(self, dynamo_mock):
        # Given: Api Gateway event with connection Id and username as query param
        conn_id = ws_conn_ev["requestContext"].get("connectionId")
        username = ws_conn_ev["queryStringParameters"].get("username")
        # Given: Table name is passed to environment variables
        table_name = os.environ.get('CONNECTION_TABLE_NAME')
        # When: connect function is called with a valid event
        response = connection_manager(ws_conn_ev, "")
        # Then: 200 is returned
        self.assertEqual(response['statusCode'], 200)
        # Then: Dynamo resource is called to pull table with correct table name
        dynamo_mock.assert_called_once_with(table_name)
        target_table = dynamo_mock.return_value
        # Then: The correct value of connection id is put to the table
        target_table.put_item.assert_called_once_with(**{'Item': {'connectionId': conn_id, 'username': username}})

    @mock.patch.dict(ws_conn_ev, {"requestContext": {"connectionId": None, "eventType": "CONNECT"}})
    def test_connection_with_missing_connection_id(self):
        # Given: Api Gateway even with empty connection Id
        assert not ws_conn_ev["requestContext"].get("connectionId")
        # When: connect function is called with a valid event
        response = connection_manager(ws_conn_ev, "")
        # Then: 500 is returned due to missing connection id
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], 'connectionId value must not be empty or missing')

    @mock.patch.dict(ws_conn_ev, {"requestContext": {"connectionId": 'ASD', "eventType": "Unknown"}})
    def test_connection_with_unknown_connect_type(self):
        # Given: Api Gateway even with unknown event type
        assert ws_conn_ev["requestContext"]['eventType'] not in ['CONNECT', 'DISCONNECT']
        # When: connect function is called with a valid event
        response = connection_manager(ws_conn_ev, "")
        # Then: 500 is returned due to missing connection id
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], 'Unrecognized eventType. CONNECT and DISCONNECT are only available.')

    @mock.patch('utils.dynamodb.Table')
    @mock.patch.dict(ws_conn_ev, {"requestContext": {"connectionId": 'ASD', "eventType": "DISCONNECT"}})
    def test_disconnect_successfully(self, dynamo_mock):
        # Given: Api Gateway disconnect event with connection Id
        assert ws_conn_ev["requestContext"]['eventType'] == 'DISCONNECT'
        conn_id = ws_conn_ev["requestContext"].get("connectionId")
        # Given: Table name is passed to environment variables
        table_name = os.environ.get('CONNECTION_TABLE_NAME')
        # When: connect function is called with a valid event
        response = connection_manager(ws_conn_ev, "")
        # Then: 200 is returned
        self.assertEqual(response['statusCode'], 200)
        # Then: Dynamo resource is called to pull table with correct table name
        dynamo_mock.assert_called_once_with(table_name)
        target_table = dynamo_mock.return_value
        # Then: The correct value of connection id is put to the table
        target_table.delete_item.assert_called_once_with(**{'Key': {'connectionId': conn_id}})


if __name__ == '__main__':
    unittest.main()
