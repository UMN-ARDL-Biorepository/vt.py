import logging
import os

from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry
from requests_toolbelt.sessions import BaseUrlSession

load_dotenv()  # take environment variables from .env file


class VersaTrak(object):
    def __init__(
        self,
        base_url=os.getenv(
            key="API_URL", default="http://versatrak.example.com/vtwebapi2/api/"
        ),
        instance=os.getenv(key="INSTANCE_ID", default=""),
        username=os.getenv(key="USERNAME", default=""),
        password=os.getenv(key="PASSWORD", default=""),
        token=None,
        refresh_token=None,
        is_logged_on=False,
    ):
        self.username = username
        self.password = password
        self.token = token
        self.refresh_token = refresh_token

        self.session = BaseUrlSession(base_url=base_url)
        assert_status_hook = (
            lambda response, *args, **kwargs: response.raise_for_status()
        )
        self.session.hooks["response"] = [assert_status_hook]

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(prefix="https://", adapter=adapter)
        self.session.mount(prefix="http://", adapter=adapter)

        logging.debug(
            msg=f"VersaTrak object created with base url: {self.session.base_url}"
        )

        if instance:
            self.instance = instance
        else:
            self.instance = self.get_first_instance_id()
            logging.debug(
                msg=f"No instance specified, using first instance id: {self.instance}"
            )

        self.is_logged_on = self.isloggedon()

        if not self.is_logged_on:
            if self.instance and self.username and self.password:
                logging.debug(msg=f"Logging in with {self.username}")
                self.login()
            else:
                logging.debug(msg="No credentials specified")

    def get_instances(self):
        try:
            r = self.session.get(url="usersession/action/instanceList")
            r.raise_for_status()
            instances = r.json()["instances"]
            return instances
        except HTTPError as e:
            logging.error(msg=f"HTTPError: {e}")
            raise

    def get_first_instance_id(self):
        instances = self.get_instances()
        first_instance_id = instances[0]["id"]
        return first_instance_id

    def update_token(self, token=None, refresh_token=None):
        logging.debug(msg=f"Received token: {token}")
        self.token = token
        logging.debug(msg=f"Received refresh token: {refresh_token}")
        self.refresh_token = refresh_token
        self.session.headers.update({"Authorization": "Bearer " + self.token})
        self.is_logged_on = self.isloggedon()
        logging.debug(msg=f"Logged on: {self.is_logged_on}")
        return self.is_logged_on

    def login(self):
        logon_data = {
            "username": self.username,
            "password": self.password,
            "instance": self.instance,
        }

        r = self.session.post(url="usersession/action/logon", data=logon_data)
        return self.update_token(
            token=r.json()["jwt"], refresh_token=r.json()["refreshToken"]
        )

    def isloggedon(self):
        r = self.session.get(url="usersession/action/isloggedon")
        self.is_logged_on = r.json()["isLoggedOn"]
        return self.is_logged_on

    def refresh_auth_token(self):
        r = self.session.post(
            url="usersession/action/refreshAuthToken",
            data={"authToken": self.token, "refreshToken": self.refresh_token},
        )
        logging.debug(msg=r.json())
        return self.update_token(
            token=r.json()["authToken"], refresh_token=r.json()["refreshToken"]
        )

    def logoff(self):
        r = self.session.post(url="usersession/action/logoff")
        self.is_logged_on = False
        return r.text

    def userrole(self):
        r = self.session.get(url="userrole")
        return r.text

    def functions(self):
        r = self.session.get(url="userrole/action/functions")
        return r.text

    def watchlist(self):
        r = self.session.get(url="user/action/watchlist")
        return r.text

    def get_users_list(self):
        r = self.session.get(url="user/action/getEditUsersList")
        return r.text

    def get_user(self, user_id):
        r = self.session.get(url=f"user/{user_id}")
        return r.text

    def get_users(self):
        r = self.session.get(url="user")
        return r.text

    def currentstatus(self):
        try:
            r = self.session.get(url="currentstatus")
            r.raise_for_status()
            return r.text
        except HTTPError as e:
            logging.error(msg=f"HTTPError: {e}")
            raise

    def getallmonitoredobjects(self):
        r = self.session.get(url="monitoredobject/action/getall")
        return r.text

    def department(self):
        r = self.session.get(url="department")
        return r.text

    def location(self):
        r = self.session.get(url="location")
        return r.text

    def uom(self):
        r = self.session.get(url="uom")
        return r.text

    def policy(self):
        r = self.session.get(url="policy")
        return r.text

    def monitoredobjecttype(self):
        r = self.session.get(url="monitoredObjectType")
        return r.text

    def monitorpointtype(self):
        r = self.session.get(url="monitorPointType")
        return r.text

    def probetypes(self):
        r = self.session.get(url="sensortype/probetypes")
        return r.text

    def sysinfo(self):
        r = self.session.get(url="system/action/sysinfo")
        return r.text

    def gethistorydata(
        self, object_id, start_date=0, end_date=0, period="1d", include_events=False
    ):
        try:
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
            r = self.session.post(
                url=f"monitoredObject/action/gethistorydata/{object_id}", data=params
            )
            r.raise_for_status()
            return r.text
        except HTTPError as exc:
            logging.error(msg=f"HTTPError: {exc}")
            raise
        except Exception as exc:
            logging.error(msg=exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name=__name__)
    vt = VersaTrak()
