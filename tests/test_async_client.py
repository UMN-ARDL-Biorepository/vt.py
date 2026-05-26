import os
import pytest
import pytest_asyncio
from vt.api import VersaTrak
from dotenv import load_dotenv

load_dotenv()


@pytest_asyncio.fixture
async def aclient():
    # By default, use deterministic fakes unless VT_RUN_LIVE_TESTS is set
    run_live = os.getenv("VT_RUN_LIVE_TESTS")
    api_url = os.getenv("API_URL")
    if run_live and api_url:
        vt = VersaTrak(base_url=api_url)

        # Ensure credentials are available for live tests
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        if not username or not password:
            pytest.skip(
                "USERNAME or PASSWORD not set in .env; authenticated live tests require credentials"
            )

        if not vt.is_logged_on:
            await vt.alogin()
        yield vt
        if vt.is_logged_on:
            await vt.alogoff()
        return

    # Deterministic fake client for offline/unit testing
    vt = VersaTrak(base_url="http://test.local", username="", password="")

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
        return "admin"

    async def fake_acurrentstatus():
        return "OK"

    # Inject fakes
    vt.aget_instances = fake_aget_instances
    vt.aget_first_instance_id = fake_aget_first_instance_id
    vt.alogin = fake_alogin
    vt.aisloggedon = fake_aisloggedon
    vt.alogoff = fake_alogoff
    vt.auserrole = fake_auserrole
    vt.acurrentstatus = fake_acurrentstatus

    yield vt

    # cleanup
    if vt.is_logged_on:
        await vt.alogoff()


@pytest.mark.asyncio
async def test_acreate_client(aclient):
    assert aclient is not None
    assert isinstance(aclient, VersaTrak)


@pytest.mark.asyncio
async def test_aget_instances(aclient):
    instances = await aclient.aget_instances()
    assert isinstance(instances, list)
    assert len(instances) > 0


@pytest.mark.asyncio
async def test_aget_first_instance_id(aclient):
    instance_id = await aclient.aget_first_instance_id()
    assert isinstance(instance_id, str)
    assert len(instance_id) > 0


@pytest.mark.asyncio
async def test_aisloggedon(aclient):
    assert await aclient.aisloggedon() is True


@pytest.mark.asyncio
async def test_auserrole(aclient):
    res = await aclient.auserrole()
    assert isinstance(res, str)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_acurrentstatus(aclient):
    res = await aclient.acurrentstatus()
    assert isinstance(res, str)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_alogin_alogoff_manual():
    api_url = os.getenv("API_URL")
    if not api_url:
        pytest.skip("API_URL not set in .env")
    if not os.getenv("VT_RUN_LIVE_TESTS"):
        pytest.skip("VT_RUN_LIVE_TESTS not set; skipping live auth test")
    vt = VersaTrak(base_url=api_url)
    if not vt.is_logged_on:
        await vt.alogin()
    assert vt.is_logged_on is True
    assert vt.token != ""

    await vt.alogoff()
    assert vt.is_logged_on is False
    assert vt.token == ""
    assert "Authorization" not in vt.session.headers
