from pinthesky.globals import app_context


def test_context():
    app_context.inject('foo', 'bar', "MY_SCOPE")
    app_context.inject('some_value', 'This is a global', 'MY_SCOPE')
    app_context.inject('rqu', 'value', 'REQUEST')
    assert app_context.resolve('MY_SCOPE') == {
        'foo': 'bar',
        'some_value': 'This is a global'
    }
