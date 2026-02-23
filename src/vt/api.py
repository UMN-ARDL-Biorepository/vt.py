import asyncio
import logging
import os
from uplink import (
    Consumer,
    get,
    post,
    Path,
    Body,
    returns,
    response_handler,
    AiohttpClient,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def raise_for_status(response):
    response.raise_for_status()
    return response


@response_handler(raise_for_status)
class VersaTrak(Consumer):
    def __init__(
        self,
        base_url=None,
        instance=None,
        username=None,
        password=None,
        token=None,
        refresh_token=None,
    ):
        base_url = (
            base_url
            or os.getenv("API_URL")
            or "http://versatrak.example.com/vtwebapi2/api/"
        )
        super(VersaTrak, self).__init__(base_url=base_url, client=AiohttpClient())

        self.instance = instance or os.getenv("INSTANCE_ID", "")
        self.username = username or os.getenv("USERNAME", "")
        self.password = password or os.getenv("PASSWORD", "")
        self.token = token
        self.refresh_token = refresh_token
        self.is_logged_on = False

        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.is_logged_on = True

        # Automated login if credentials provided
        if not self.is_logged_on and self.username and self.password:
            # We use _run_sync here for the constructor's auto-login
            if not self.instance:
                try:
                    self.instance = self.get_first_instance_id()
                except Exception as e:
                    logger.debug(f"Failed to fetch instance list during init: {e}")

            if self.instance:
                try:
                    self.login()
                except Exception as e:
                    logger.debug(f"Failed to auto-login during init: {e}")

    def _run_sync(self, coro):
        """Helper to run async methods synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()

        return loop.run_until_complete(coro)

    # --- Internal async methods (decorated) ---

    @returns.json
    @get("usersession/action/instanceList")
    async def _aget_instance_list_raw(self):
        pass

    @returns.json
    @post("usersession/action/logon")
    async def _alogon_raw(self, **data: Body):
        pass

    @returns.json
    @get("usersession/action/isloggedon")
    async def _aisloggedon_raw(self):
        pass

    @returns.json
    @post("usersession/action/refreshAuthToken")
    async def _arefresh_token_raw(self, **data: Body):
        pass

    @post("usersession/action/logoff")
    async def _alogoff_raw(self):
        pass

    @post("monitoredObject/action/gethistorydata/{object_id}")
    async def _aget_history_raw(self, object_id: Path, **data: Body):
        pass

    # --- Public Async API methods ---

    async def aget_instances(self):
        res = await self._aget_instance_list_raw()
        return res.get("instances", [])

    async def aget_first_instance_id(self):
        instances = await self.aget_instances()
        return instances[0]["id"] if instances else None

    async def alogin(self):
        logon_data = {
            "username": self.username,
            "password": self.password,
            "instance": self.instance,
        }
        res = await self._alogon_raw(**logon_data)
        self.token = res.get("jwt")
        self.refresh_token = res.get("refreshToken")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.is_logged_on = True
        return self.is_logged_on

    async def aisloggedon(self):
        res = await self._aisloggedon_raw()
        self.is_logged_on = res.get("isLoggedOn", False)
        return self.is_logged_on

    async def arefresh_auth_token(self):
        data = {"authToken": self.token, "refreshToken": self.refresh_token}
        res = await self._arefresh_token_raw(**data)
        self.token = res.get("authToken")
        self.refresh_token = res.get("refreshToken")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.is_logged_on = True
        return self.is_logged_on

    async def alogoff(self):
        try:
            res = await self._alogoff_raw()
            return await res.text()
        finally:
            self.is_logged_on = False
            self.token = ""
            self.refresh_token = ""
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]

    # --- Generic async text getters ---

    @get("userrole")
    async def auserrole_raw(self):
        pass

    async def auserrole(self):
        res = await self.auserrole_raw()
        return await res.text()

    @get("userrole/action/functions")
    async def afunctions_raw(self):
        pass

    async def afunctions(self):
        res = await self.afunctions_raw()
        return await res.text()

    @get("user/action/watchlist")
    async def awatchlist_raw(self):
        pass

    async def awatchlist(self):
        res = await self.awatchlist_raw()
        return await res.text()

    @post("user/action/getEditUsersList")
    async def aget_users_list_raw(self):
        pass

    async def aget_users_list(self):
        res = await self.aget_users_list_raw()
        return await res.text()

    @get("user/{user_id}")
    async def aget_user_raw(self, user_id):
        pass

    async def aget_user(self, user_id):
        res = await self.aget_user_raw(user_id)
        return await res.text()

    @get("user")
    async def aget_users_raw(self):
        pass

    async def aget_users(self):
        res = await self.aget_users_raw()
        return await res.text()

    @get("currentstatus")
    async def acurrentstatus_raw(self):
        pass

    async def acurrentstatus(self):
        res = await self.acurrentstatus_raw()
        return await res.text()

    @get("monitoredobject/action/getall")
    async def agetallmonitoredobjects_raw(self):
        pass

    async def agetallmonitoredobjects(self):
        res = await self.agetallmonitoredobjects_raw()
        return await res.text()

    @get("department")
    async def adepartment_raw(self):
        pass

    async def adepartment(self):
        res = await self.adepartment_raw()
        return await res.text()

    @get("location")
    async def alocation_raw(self):
        pass

    async def alocation(self):
        res = await self.alocation_raw()
        return await res.text()

    @get("uom")
    async def auom_raw(self):
        pass

    async def auom(self):
        res = await self.auom_raw()
        return await res.text()

    @get("policy")
    async def apolicy_raw(self):
        pass

    async def apolicy(self):
        res = await self.apolicy_raw()
        return await res.text()

    @get("monitoredObjectType")
    async def amonitoredobjecttype_raw(self):
        pass

    async def amonitoredobjecttype(self):
        res = await self.amonitoredobjecttype_raw()
        return await res.text()

    @get("monitorPointType")
    async def amonitorpointtype_raw(self):
        pass

    async def amonitorpointtype(self):
        res = await self.amonitorpointtype_raw()
        return await res.text()

    @get("sensortype/probetypes")
    async def aprobetypes_raw(self):
        pass

    async def aprobetypes(self):
        res = await self.aprobetypes_raw()
        return await res.text()

    @get("system/action/sysinfo")
    async def asysinfo_raw(self):
        pass

    async def asysinfo(self):
        res = await self.asysinfo_raw()
        return await res.text()

    async def agethistorydata(
        self, object_id, start_date=0, end_date=0, period="1d", include_events=False
    ):
        params = {
            "tsStartDate": start_date,
            "tsEndDate": end_date,
            "period": period,
            "includeEvents": include_events,
            "jsTimestamps": True,
            "adjustToMostRecent": True,
        }
        if not self.is_logged_on:
            await self.alogin()
        res = await self._aget_history_raw(object_id=object_id, **params)
        return await res.text()

    # --- Public Sync API methods (Wrappers) ---

    def get_instances(self):
        return self._run_sync(self.aget_instances())

    def get_first_instance_id(self):
        return self._run_sync(self.aget_first_instance_id())

    def login(self):
        return self._run_sync(self.alogin())

    def isloggedon(self):
        return self._run_sync(self.aisloggedon())

    def refresh_auth_token(self):
        return self._run_sync(self.arefresh_auth_token())

    def logoff(self):
        return self._run_sync(self.alogoff())

    def userrole(self):
        return self._run_sync(self.auserrole())

    def functions(self):
        return self._run_sync(self.afunctions())

    def watchlist(self):
        return self._run_sync(self.awatchlist())

    def get_users_list(self):
        return self._run_sync(self.aget_users_list())

    def get_user(self, user_id):
        return self._run_sync(self.aget_user(user_id))

    def get_users(self):
        return self._run_sync(self.aget_users())

    def currentstatus(self):
        return self._run_sync(self.acurrentstatus())

    def getallmonitoredobjects(self):
        return self._run_sync(self.agetallmonitoredobjects())

    def department(self):
        return self._run_sync(self.adepartment())

    def location(self):
        return self._run_sync(self.alocation())

    def uom(self):
        return self._run_sync(self.auom())

    def policy(self):
        return self._run_sync(self.apolicy())

    def monitoredobjecttype(self):
        return self._run_sync(self.amonitoredobjecttype())

    def monitorpointtype(self):
        return self._run_sync(self.amonitorpointtype())

    def probetypes(self):
        return self._run_sync(self.aprobetypes())

    def sysinfo(self):
        return self._run_sync(self.asysinfo())

    def gethistorydata(
        self, object_id, start_date=0, end_date=0, period="1d", include_events=False
    ):
        return self._run_sync(
            self.agethistorydata(
                object_id, start_date, end_date, period, include_events
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    vt = VersaTrak()
