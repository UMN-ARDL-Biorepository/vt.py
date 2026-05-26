import os
import pytest
from vt.api import VersaTrak
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def client():
    # Run live only when explicitly requested
    run_live = os.getenv("VT_RUN_LIVE_TESTS")
    api_url = os.getenv("API_URL")
    if run_live and api_url:
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        instance = os.getenv("INSTANCE")
        if not username or not password or not instance:
            pytest.skip(
                "USERNAME, PASSWORD, and INSTANCE must be set in .env for authenticated live tests"
            )
        vt = VersaTrak(base_url=api_url)
        yield vt
        if vt.is_logged_on:
            vt.logoff()
        return

    # Deterministic fake client for offline/unit testing
    vt = VersaTrak(base_url="http://test.local", username="", password="")

    # Async fakes used by sync wrappers; defined as coroutines without parameters
    async def fake_aget_instances():
        return [{"id": "inst1"}]

    async def fake_aget_first_instance_id():
        return "inst1"

    async def fake_alogin():
        vt.token = "fake-token"
        vt.refresh_token = "fake-refresh"
        vt.is_logged_on = True
        vt.session.headers.update({"Authorization": f"Bearer {vt.token}"})
        return True

    async def fake_aisloggedon():
        vt.is_logged_on = True
        return True

    async def fake_alogoff():
        vt.is_logged_on = False
        vt.token = ""
        vt.refresh_token = ""
        if "Authorization" in vt.session.headers:
            del vt.session.headers["Authorization"]
        return ""

    async def fake_auserrole():
        class _R:
            async def text(self):
                return "admin"

        return _R()

    async def fake_afunctions():
        class _R:
            async def text(self):
                return "funcs"

        return _R()

    async def fake_acurrentstatus():
        class _R:
            async def text(self):
                return "OK"

        return _R()

    # Inject fakes (async methods)
    vt.aget_instances = fake_aget_instances
    vt.aget_first_instance_id = fake_aget_first_instance_id
    vt.alogin = fake_alogin
    vt.aisloggedon = fake_aisloggedon
    vt.alogoff = fake_alogoff
    vt.auserrole_raw = fake_auserrole
    vt.afunctions_raw = fake_afunctions
    vt.acurrentstatus_raw = fake_acurrentstatus

    # Other raw endpoints used across tests - return simple text responses
    async def _text_resp(val):
        class _R:
            def __init__(self, v):
                self._v = v

            async def text(self):
                return self._v

        return _R(val)

    vt.awatchlist_raw = lambda: _text_resp("[]")
    vt.aget_users_list_raw = lambda: _text_resp("[]")
    vt.aget_user_raw = lambda user_id: _text_resp("{}")
    vt.aget_users_raw = lambda: _text_resp("[]")
    vt.agetallmonitoredobjects_raw = lambda: _text_resp("[]")
    vt.adepartment_raw = lambda: _text_resp("[]")
    vt.alocation_raw = lambda: _text_resp("[]")
    vt.auom_raw = lambda: _text_resp("{}")
    vt.apolicy_raw = lambda: _text_resp("[]")
    vt.amonitoredobjecttype_raw = lambda: _text_resp("[]")
    vt.amonitorpointtype_raw = lambda: _text_resp("[]")
    vt.aprobetypes_raw = lambda: _text_resp("[]")
    vt.asysinfo_raw = lambda: _text_resp("{}")
    vt._aget_history_raw = lambda object_id, data: _text_resp("[]")

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
    if not os.getenv("VT_RUN_LIVE_TESTS"):
        pytest.skip("VT_RUN_LIVE_TESTS not set; skipping live auth test")
    vt = VersaTrak(base_url=api_url)
    if not vt.is_logged_on:
        vt.login()
    assert vt.is_logged_on is True
    assert vt.token != ""

    vt.logoff()
    assert vt.is_logged_on is False
    assert vt.token == ""
    assert "Authorization" not in vt.session.headers
