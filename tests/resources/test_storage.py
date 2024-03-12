
def test_storage(storage):

    info = storage('/info')
    assert info.code == 200
    assert info.body == {
        'bucketName': 'NOT_FOUND',
        'videoPrefix': 'videos',
        'imagePrefix': 'images',
        'deviceVideoPrefix': 'devices',
    }
