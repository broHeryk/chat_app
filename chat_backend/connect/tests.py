from socket_chat.connect import connect
test_aws_event = {
    'headers': {'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,uk;q=0.8,ru;q=0.7', 'Cache-Control': 'no-cache', 'Host': 'mdzog1v2pf.execute-api.us-east-2.amazonaws.com', 'Origin': 'chrome-extension://pfdhoblngboilpfeibdedpjgfnlcodoo', 'Pragma': 'no-cache', 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits', 'Sec-WebSocket-Key': 'IC27/6u0YbaQTdowvIeRKQ==', 'Sec-WebSocket-Version': '13', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-5fe4adf0-0be9bb523879d95c2649aad9', 'X-Forwarded-For': '188.163.73.235', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept-Encoding': ['gzip, deflate, br'], 'Accept-Language': ['en-US,en;q=0.9,uk;q=0.8,ru;q=0.7'], 'Cache-Control': ['no-cache'], 'Host': ['mdzog1v2pf.execute-api.us-east-2.amazonaws.com'], 'Origin': ['chrome-extension://pfdhoblngboilpfeibdedpjgfnlcodoo'], 'Pragma': ['no-cache'], 'Sec-WebSocket-Extensions': ['permessage-deflate; client_max_window_bits'], 'Sec-WebSocket-Key': ['IC27/6u0YbaQTdowvIeRKQ=='], 'Sec-WebSocket-Version': ['13'], 'User-Agent': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'], 'X-Amzn-Trace-Id': ['Root=1-5fe4adf0-0be9bb523879d95c2649aad9'], 'X-Forwarded-For': ['188.163.73.235'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'requestContext': {'routeKey': '$connect', 'disconnectStatusCode': None, 'messageId': None, 'eventType': 'CONNECT', 'extendedRequestId': 'YEAdoFAJiYcFrYg=', 'requestTime': '24/Dec/2020:15:04:16 +0000', 'messageDirection': 'IN', 'disconnectReason': None, 'stage': 'Prod', 'connectedAt': 1608822256737, 'requestTimeEpoch': 1608822256737, 'identity': {'cognitoIdentityPoolId': None, 'cognitoIdentityId': None, 'principalOrgId': None, 'cognitoAuthenticationType': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'accountId': None, 'caller': None, 'sourceIp': '188.163.73.235', 'accessKey': None, 'cognitoAuthenticationProvider': None, 'user': None}, 'requestId': 'YEAdoFAJiYcFrYg=', 'domainName': 'mdzog1v2pf.execute-api.us-east-2.amazonaws.com', 'connectionId': 'YEAdod-BCYcCHcQ=', 'apiId': 'mdzog1v2pf'}, 'isBase64Encoded': False }

def test_connect_event():
    assert True
    connect(test_aws_event, None)

test_aws_event()