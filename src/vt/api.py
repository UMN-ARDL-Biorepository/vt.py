import logging
import os
from uplink import Consumer, get, post, Path, Body, returns, response_handler

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
        super(VersaTrak, self).__init__(base_url=base_url)

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

    # --- Internal methods returning JSON or Response ---

    @returns.json
    @get("usersession/action/instanceList")
    def _get_instance_list(self):
        """Internal"""

    @returns.json
    @post("usersession/action/logon")
    def _login(self, **data: Body):
        """Internal"""

    @returns.json
    @get("usersession/action/isloggedon")
    def _isloggedon(self):
        """Internal"""

    @returns.json
    @post("usersession/action/refreshAuthToken")
    def _refresh_token(self, **data: Body):
        """Internal"""

    @post("usersession/action/logoff")
    def _logoff_raw(self):
        """Internal"""

    @post("monitoredObject/action/gethistorydata/{object_id}")
    def _get_history(self, object_id: Path, **data: Body):
        """Internal"""

    # --- Public API methods ---

    def get_instances(self):
        res = self._get_instance_list()
        return res.get("instances", [])

    def get_first_instance_id(self):
        instances = self.get_instances()
        if instances:
            return instances[0]["id"]
        return None

    def login(self):
        logon_data = {
            "username": self.username,
            "password": self.password,
            "instance": self.instance,
        }
        res = self._login(**logon_data)
        self.token = res.get("jwt")
        self.refresh_token = res.get("refreshToken")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.is_logged_on = True
        return self.is_logged_on

    def isloggedon(self):
        res = self._isloggedon()
        self.is_logged_on = res.get("isLoggedOn", False)
        return self.is_logged_on

    def refresh_auth_token(self):
        data = {"authToken": self.token, "refreshToken": self.refresh_token}
        res = self._refresh_token(**data)
        self.token = res.get("authToken")
        self.refresh_token = res.get("refreshToken")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.is_logged_on = True
        return self.is_logged_on

    def logoff(self):
        try:
            res = self._logoff_raw()
            return res.text
        finally:
            self.is_logged_on = False
            self.token = ""
            self.refresh_token = ""
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]

    @get("userrole")
    def userrole_raw(self):
        pass

    def userrole(self):
        return self.userrole_raw().text

    @get("userrole/action/functions")
    def functions_raw(self):
        pass

    def functions(self):
        return self.functions_raw().text

    @get("user/action/watchlist")
    def watchlist_raw(self):
        pass

    def watchlist(self):
        return self.watchlist_raw().text

    @post("user/action/getEditUsersList")
    def get_users_list_raw(self):
        pass

    def get_users_list(self):
        return self.get_users_list_raw().text

    @get("user/{user_id}")
    def get_user_raw(self, user_id):
        pass

    def get_user(self, user_id):
        return self.get_user_raw(user_id).text

    @get("user")
    def get_users_raw(self):
        pass

    def get_users(self):
        return self.get_users_raw().text

    @get("currentstatus")
    def currentstatus_raw(self):
        pass

    def currentstatus(self):
        return self.currentstatus_raw().text

    @get("monitoredobject/action/getall")
    def getallmonitoredobjects_raw(self):
        pass

    def getallmonitoredobjects(self):
        return self.getallmonitoredobjects_raw().text

    @get("department")
    def department_raw(self):
        pass

    def department(self):
        return self.department_raw().text

    @get("location")
    def location_raw(self):
        pass

    def location(self):
        return self.location_raw().text

    @get("uom")
    def uom_raw(self):
        pass

    def uom(self):
        return self.uom_raw().text

    @get("policy")
    def policy_raw(self):
        pass

    def policy(self):
        return self.policy_raw().text

    @get("monitoredObjectType")
    def monitoredobjecttype_raw(self):
        pass

    def monitoredobjecttype(self):
        return self.monitoredobjecttype_raw().text

    @get("monitorPointType")
    def monitorpointtype_raw(self):
        pass

    def monitorpointtype(self):
        return self.monitorpointtype_raw().text

    @get("sensortype/probetypes")
    def probetypes_raw(self):
        pass

    def probetypes(self):
        return self.probetypes_raw().text

    @get("system/action/sysinfo")
    def sysinfo_raw(self):
        pass

    def sysinfo(self):
        return self.sysinfo_raw().text

    def gethistorydata(
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
            self.login()
        res = self._get_history(object_id=object_id, **params)
        return res.text


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    vt = VersaTrak()
