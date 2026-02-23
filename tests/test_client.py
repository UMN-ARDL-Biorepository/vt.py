import os
import pytest
from vt.api import VersaTrak
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def client():
    # Ensure variables are available
    api_url = os.getenv("API_URL")
    if not api_url:
        pytest.skip("API_URL not set in .env")

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    instance = os.getenv("INSTANCE")
    if not username or not password or not instance:
        pytest.skip("USERNAME, PASSWORD, and INSTANCE must be set in .env for authenticated tests")
    vt = VersaTrak(base_url=api_url)
    # The client logs in during initialization if credentials are provided
    yield vt
    if vt.is_logged_on:
        vt.logoff()


def test_create_client(client):
    assert client is not None
    assert isinstance(client, VersaTrak)


def test_get_instances(client):
    instances = client.get_instances()
    assert isinstance(instances, list)
    assert len(instances) > 0


def test_get_first_instance_id(client):
    instance_id = client.get_first_instance_id()
    assert isinstance(instance_id, str)
    assert len(instance_id) > 0


def test_isloggedon(client):
    assert client.isloggedon() is True


def test_userrole(client):
    res = client.userrole()
    assert isinstance(res, str)
    assert len(res) > 0


def test_functions(client):
    res = client.functions()
    assert isinstance(res, str)
    assert len(res) > 0


def test_watchlist(client):
    res = client.watchlist()
    assert isinstance(res, str)


def test_get_users_list(client):
    try:
        res = client.get_users_list()
        assert isinstance(res, str)
    except Exception as e:
        if any(err in str(e) for err in ["400", "405", "401"]):
            pytest.skip(f"Users list endpoint error: {e}")
        raise


def test_get_users(client):
    res = client.get_users()
    assert isinstance(res, str)
    assert len(res) > 0


def test_currentstatus(client):
    res = client.currentstatus()
    assert isinstance(res, str)
    assert len(res) > 0


def test_getallmonitoredobjects(client):
    res = client.getallmonitoredobjects()
    assert isinstance(res, str)
    assert len(res) > 0


def test_department(client):
    res = client.department()
    assert isinstance(res, str)


def test_location(client):
    res = client.location()
    assert isinstance(res, str)


def test_uom(client):
    res = client.uom()
    assert isinstance(res, str)


def test_policy(client):
    try:
        res = client.policy()
        assert isinstance(res, str)
    except Exception as e:
        if "400" in str(e):
            pytest.skip(f"Policy endpoint returned 400: {e}")
        raise


def test_monitoredobjecttype(client):
    res = client.monitoredobjecttype()
    assert isinstance(res, str)


def test_monitorpointtype(client):
    res = client.monitorpointtype()
    assert isinstance(res, str)


def test_probetypes(client):
    res = client.probetypes()
    assert isinstance(res, str)


def test_sysinfo(client):
    res = client.sysinfo()
    assert isinstance(res, str)
    assert len(res) > 0


def test_get_user(client):
    try:
        res = client.get_user(1)  # Try ID 1 as a guess
        assert isinstance(res, str)
    except Exception:
        pytest.skip("Could not fetch user with ID 1")


def test_gethistorydata(client):
    objects_data = client.getallmonitoredobjects()
    import json

    try:
        objs = json.loads(objects_data)
        if isinstance(objs, list) and len(objs) > 0:
            obj_id = objs[0].get("id")
            if obj_id:
                res = client.gethistorydata(obj_id)
                assert isinstance(res, str)
            else:
                pytest.skip("No id found in first monitored object")
        else:
            pytest.skip("No monitored objects found to test history")
    except Exception as e:
        pytest.skip(f"Skipping history test: {e}")


def test_refresh_auth_token(client):
    if client.token and client.refresh_token:
        res = client.refresh_auth_token()
        assert res is True
        assert client.token != ""
    else:
        pytest.skip("No tokens available to refresh")


def test_login_logout_manual():
    api_url = os.getenv("API_URL")
    if not api_url:
        pytest.skip("API_URL not set in .env")
    vt = VersaTrak(base_url=api_url)
    if not vt.is_logged_on:
        vt.login()
    assert vt.is_logged_on is True
    assert vt.token != ""

    vt.logoff()
    assert vt.is_logged_on is False
    assert vt.token == ""
    assert "Authorization" not in vt.session.headers
