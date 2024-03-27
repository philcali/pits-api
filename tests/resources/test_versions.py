from ophis.globals import app_context


def test_versions(versions):
    version_data = app_context.resolve('GLOBAL')['version_data']

    tags = [
        "0.7.0",
        "0.6.0",
        "0.5.1",
        "0.5.0",
        "0.4.1",
        "0.4.0",
    ]

    for tag in tags:
        version_data.create("123456789012", item={
            'name': tag,
        })

    list_versions = versions()
    assert list_versions.code == 200
    assert [item['name'] for item in list_versions.body['items']] == tags

    assert versions('/latest').code == 404

    created = version_data.create("123456789012", "latest", item={
        'name': 'current',
        'tag': '0.7.0',
    })

    latest = versions('/latest')
    assert latest.code == 200
    assert latest.body == {
        'name': '0.7.0',
        'createTime': created['createTime'],
        'updateTime': created['updateTime'],
    }
