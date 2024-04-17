from ophis.globals import app_context


def test_connections(connections):
    connection_db = app_context.resolve()['connections']
    session_db = app_context.resolve()['sessions']

    empty = connections()

    assert empty.body['items'] == []
    assert empty.code == 200

    created = connection_db.create(
        connections.account_id(),
        item={
            'connectionId': 'abc-123'
        }
    )

    assert connections().body['items'][0] == created
    assert connections('/' + created['connectionId']).body == created
    assert connections('/not-found').code == 404

    assert connections('/not-found/sessions').code == 404

    empty = connections('/' + created['connectionId'] + '/sessions')
    assert empty.body['items'] == []
    assert empty.code == 200
    assert connections('/' + created['connectionId'] + '/sessions/not-found').code == 404

    session = session_db.create(
        connections.account_id(),
        'Connections',
        created['connectionId'],
        item={
            'invokeId': 'efg-456',
        }
    )

    assert connections('/' + created['connectionId'] + '/sessions').body['items'][0] == session
    assert connections('/' + created['connectionId'] + '/sessions/' + session['invokeId']).body == session
