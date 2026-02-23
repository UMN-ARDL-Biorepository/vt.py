import os
import pytest
import pytest_asyncio
from vt.api import VersaTrak
from dotenv import load_dotenv

load_dotenv()


@pytest_asyncio.fixture
async def aclient():
    # Ensure variables are available
    api_url = os.getenv("API_URL")
    if not api_url:
        pytest.skip("API_URL not set in .env")

    vt = VersaTrak(base_url=api_url)
    # The client logs in during initialization if credentials are provided
    yield vt
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
    vt = VersaTrak(base_url=api_url)
    if not vt.is_logged_on:
        await vt.alogin()
    assert vt.is_logged_on is True
    assert vt.token != ""

    await vt.alogoff()
    assert vt.is_logged_on is False
    assert vt.token == ""
    assert "Authorization" not in vt.session.headers
