from math import floor
from time import time
from ophis.globals import app_context


def test_stats_workflow(stats, cameras):
    stats_data = app_context.resolve('GLOBAL')['stats_data']

    # List, confirm empty
    assert stats().body == {
        'items': [],
        'nextToken': None
    }

    # Let's create a few cameras
    created_stats = []
    historical_views = {}
    start_time = floor(time())
    for i in range(1, 4):
        thing_name = f'PitsCamera{i}'
        assert cameras(method="POST", body={
            'thingName': thing_name,
            'displayName': f'Test Camera {i}'
        }).code == 200

        # Let's inject some stat history
        resp = stats_data.create(stats.account_id(), 'latest', item={
            'SK': thing_name,
            'thing_name': thing_name,
            'ip_addr': '127.0.0.1'
        })
        created_stats.append(resp)

        historical_views[thing_name] = []
        # Let's inject some historical data
        for j in range(0, 9):
            historical_views[thing_name].insert(0, stats_data.create(
                stats.account_id(),
                thing_name,
                item={
                    'SK': str(start_time + (j * 1000)),
                    'thing_name': thing_name,
                    'ip_addr': '127.0.0.1'
                }
            ))

    assert cameras('/PitsCamera1/stats', method="POST", body={}).code == 200

    assert stats().body['items'] == created_stats
    params = {'thingName': ','.join(['PitsCamera1', 'PitsCamera2'])}
    assert stats(query_params=params).body['items'] == created_stats[0:2]

    # Trying to ask for more than the limit
    params['limit'] = 1
    assert stats(query_params=params).code == 400

    for key, items in historical_views.items():
        assert cameras(f'/{key}/stats').body['items'] == items

    # Get a single data point
    first = historical_views['PitsCamera1'][-1]
    assert cameras(f'/PitsCamera1/stats/{start_time}').body == first
    assert cameras(f'/Farts/stats/{start_time}').code == 404
