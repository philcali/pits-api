from unittest.mock import MagicMock
from pinthesky.database import MAX_ITEMS
from pinthesky.globals import app_context


def test_iot_operations(iot):
    iot_client = MagicMock()
    app_context.inject('iot', iot_client, force=True)

    groups = [
        {
            'id': 'first',
            'groupName': 'FirstOne'
        },
        {
            'id': 'second',
            'groupName': 'SecondOne'
        }
    ]

    def list_thing_groups(maxResults):
        assert maxResults == MAX_ITEMS
        return {
            'thingGroups': groups
        }
    iot_client.list_thing_groups = MagicMock()
    iot_client.list_thing_groups.side_effect = list_thing_groups

    assert iot('/groups').body == {
        'items': groups,
        'nextToken': None
    }

    thingNames = ['CameraOne', 'CameraTwo']

    def list_things_in_group(maxResults, thingGroupName):
        assert maxResults == MAX_ITEMS
        assert thingGroupName == 'FirstOne'
        return {
            'things': thingNames
        }
    iot_client.list_things_in_thing_group = MagicMock()
    iot_client.list_things_in_thing_group.side_effect = list_things_in_group

    assert iot('/groups/FirstOne/things').body == {
        'items': thingNames,
        'nextToken': None
    }
