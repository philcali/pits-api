from unittest.mock import patch, MagicMock


TEST_TIME = 1711747711


@patch('time.time', MagicMock(return_value=TEST_TIME))
def test_tokens(tokens):
    list_resp = tokens()

    assert list_resp.code == 200

    not_found = tokens('/not-found')
    assert not_found.code == 404
    assert not_found.body == {
        'message': 'Token with id not-found was not found'
    }

    create = tokens(method="POST", body={
        'timeoutInSeconds': 10
    })

    assert create.code == 200
    assert create.body['expiresIn'] == TEST_TIME + (10 * 1000)

    assert tokens(f'/{create.body["id"]}').body == create.body

    assert tokens().body['items'][0] == create.body
