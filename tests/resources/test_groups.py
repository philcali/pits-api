
def test_groups_crud_workflow(cameras, groups):
    # List, confirm empty
    assert groups.request().body == {
        'items': [],
        'nextToken': None
    }

    created_group = groups(method="POST", body={
        'name': 'Home',
        'description': 'This is the home group'
    })

    assert created_group.code == 200
    home = created_group.body
    assert 'createTime' in home
    assert 'updateTime' in home
    assert home['name'] == 'Home'

    assert groups(method="POST", body=home).code == 409

    # Get Group
    assert groups('/Home').body == home
    assert groups('/Farts').code == 404
    # Confirm in list
    assert home in groups().body['items']

    # Update is allowed
    assert groups('/Home', method="PUT", body=home).code == 200

    assert groups(query_params={'name': 'Home'}).body['items'][0] == home

    cameras(method="POST", body={
        'thingName': 'homeCamera1'
    }).code == 200

    assert groups('/Home/cameras', method='POST', body={
        'cameras': ['homeCamera1']
    }).code == 200

    assert cameras('/homeCamera1/groups').body["items"][0]['id'] == 'Home'
    assert groups('/Home/cameras').body["items"][0]['id'] == 'homeCamera1'

    assert groups('/Home/cameras/homeCamera1', method="DELETE").code == 200

    assert cameras('/homeCamera1/groups').body["items"] == []
    assert groups('/Home/cameras').body["items"] == []

    assert groups('/Home', method="DELETE").code == 200
