import os
from message.app import send_message
from unittest import mock
from chat_backend.tests.unit.test_data import send_message_event as send_ev
import unittest
from freezegun import freeze_time
from utils import get_body


@freeze_time("1970-01-01")
@mock.patch.dict(os.environ, {"CONNECTION_TABLE_NAME": "test_conn_table"})
@mock.patch.dict(os.environ, {"MESSAGE_TABLE_NAME": "test_message_table"})
class TestMessaging(unittest.TestCase):

    @mock.patch('utils.dynamodb.Table')
    @mock.patch('boto3.client')
    def test_sending_successful(self, api_gateway_mock, dynamo_mock):
        # Given: Api Gateway event with connection Id
        conn_id = send_ev["requestContext"].get("connectionId")
        # Given: Message and connection tables with content inside
        message_index = 5_000_000
        message_content = get_body(send_ev)["content"]
        message_table = mock.Mock(name='mess_table',
                                  query=lambda *_, **__: {'Items': [{'Index': message_index}]})
        connection_table = mock.Mock(name='conn_table',
                                     scan=lambda*_, **__: {'Items': [{'connectionId': 'mate_conn'}]})
        dynamo_mock.side_effect = [message_table, connection_table]
        # When: send message function is called with a valid event
        response = send_message(send_ev, "")
        # Then: 200 is returned
        self.assertEqual(response['statusCode'], 200)
        # Then: Dynamo resource is called to pull table with correct table name
        message_table.put_item.assert_called_once_with(
            Item={'room': 'general', 'index': message_index+1,
                  'timestamp': 0, 'username': 'Mate',
                  'content': message_content}
        )


if __name__ == '__main__':
    unittest.main()
