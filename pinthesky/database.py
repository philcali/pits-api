from ophis.database import Repository
from ophis.token import EncryptedTokenMarshaller


class Groups(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Groups", fields_to_keys={
            'name': 'SK'
        })


class Cameras(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Cameras", fields_to_keys={
            'thingName': 'SK'
        })


class CamerasToGroups(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="CamerasToGroups", fields_to_keys={
            'id': 'SK'
        })


class GroupsToCameras(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="GroupsToCameras", fields_to_keys={
            'id': 'SK'
        })


class MotionVideos(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="MotionVideos", fields_to_keys={
            'motionVideo': 'SK'
        })


class TagsToVideos(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(
            table=table,
            type="TagsToVideos",
            fields_to_keys={'id': 'SK'}
        )


class VideosToTags(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(
            table=table,
            type="VideosToTags",
            fields_to_keys={'id': 'SK'}
        )


class Subscriptions(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Subscriptions", fields_to_keys={
            'id': 'SK'
        })


class Tags(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Tags", fields_to_keys={
            'name': 'SK'
        })


class DeviceHealth(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="DeviceHealth")


class DeviceJobs(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="DeviceJobs", fields_to_keys={
            'jobId': 'SK'
        })


class DeviceToJobs(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="DeviceToJobs", fields_to_keys={
            'jobId': 'SK'
        })


class Versions(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Versions", fields_to_keys={
            'name': 'SK'
        })


class DataTokens(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="DataTokens", fields_to_keys={
            'id': 'SK'
        })


class DataConnections(Repository):
    def __init__(self, table=None)-> None:
        super().__init__(type="DataConnections", table=table, fields_to_keys={
            'connectionId': 'SK'
        })


class DataSessions(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(type="DataSessions", table=table, fields_to_keys={
            'invokeId': 'SK'
        })
