import os
from api import VersaTrak
from dotenv import load_dotenv

load_dotenv()


def setup_client():
    client = VersaTrak(base_url=os.getenv("API_URL"))
    return client


def test_create_client():
    client = setup_client()
    assert client is not None
    assert isinstance(client, VersaTrak)


def test_get_instances():
    client = setup_client()
    instances = client.get_instances()
    assert instances is not None
    assert isinstance(instances, list)
    assert len(instances) > 0


def test_get_first_instance_id():
    client = setup_client()
    first_instance_id = client.get_first_instance_id()
    assert first_instance_id is not None
    assert isinstance(first_instance_id, str)
    assert len(first_instance_id) > 0


def test_login():
    client = setup_client()
    client.login()
    assert client.token is not None
    assert client.refresh_token is not None
    assert "Authorization" in client.session.headers
    assert client.session.headers["Authorization"] == "Bearer " + client.token


def test_logoff():
    client = setup_client()
    client.login()
    client.logoff()
    assert client.token == ""
    assert client.refresh_token == ""
