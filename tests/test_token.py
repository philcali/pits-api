from decimal import Decimal
from pinthesky.token import EncryptedTokenMarshaller

TEST_ACC = "012345678912"


def test_roundtrip_failure():
    marshaller = EncryptedTokenMarshaller()
    token = marshaller.encrypt(TEST_ACC, header="This.Test", last_key={
        "message": 'This is huge!',
        "createTime": Decimal(100)
    })
    try:
        marshaller.decrypt("987654321021", "This.Test", token)
        raise Exception("Not supposed to!")
    except ValueError as e:
        assert "MAC check failed" == str(e)


def test_roundtrip():
    marshaller = EncryptedTokenMarshaller()
    data = {'message': 'This is huge!', 'createTime': Decimal(100)}
    token = marshaller.encrypt(TEST_ACC, "This.Test", data)
    assert data == marshaller.decrypt(TEST_ACC, "This.Test", token)
