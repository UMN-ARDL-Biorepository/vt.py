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
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        logging.debug(
            f"VersaTrak object created with base url: {self.session.base_url}"
        )

        if instance:
            self.instance = instance
        else:
            self.instance = self.get_first_instance_id()
            logging.debug(
                f"No instance specified, using first instance id: {self.instance}"
            )

        self.is_logged_on = self.isloggedon()

        if not self.is_logged_on:
            if self.instance and self.username and self.password:
                logging.debug(f"Logging in with {self.username}")
                self.login()
            else:
                logging.debug("No credentials specified")

    def get_instances(self):
        try:
            r = self.session.get("usersession/action/instanceList")
            r.raise_for_status()
            instances = r.json()["instances"]
            return instances
        except HTTPError as e:
            logging.error(f"HTTPError: {e}")
            raise

    def get_first_instance_id(self):
        instances = self.get_instances()
        first_instance_id = instances[0]["id"]
        return first_instance_id

    def login(self):
        logon_data = {
            "username": self.username,
            "password": self.password,
            "instance": self.instance,
        }

        r = self.session.post("usersession/action/logon", data=logon_data)
        self.token = r.json()["jwt"]
        logging.debug("Received token: " + self.token)
        self.refresh_token = r.json()["refreshToken"]
        logging.debug("Received refresh token: " + self.refresh_token)
        self.session.headers.update({"Authorization": "Bearer " + self.token})
        self.is_logged_on = self.isloggedon()
        logging.debug(f"Logged on: {self.is_logged_on}")
        return self.is_logged_on

    def isloggedon(self):
        r = self.session.get("usersession/action/isloggedon")
        self.is_logged_on = r.json()["isLoggedOn"]
        return self.is_logged_on

    def currentstatus(self):
        try:
            r = self.session.get("currentstatus")
            r.raise_for_status()
            return r.text
        except HTTPError as e:
            logging.error(f"HTTPError: {e}")
            raise

    def department(self):
        r = self.session.get("department")
        return r.text

    def location(self):
        r = self.session.get("location")
        return r.text

    def uom(self):
        r = self.session.get("uom")
        return r.text

    def policy(self):
        r = self.session.get("policy")
        return r.text

    def monitoredobjecttype(self):
        r = self.session.get("monitoredObjectType")
        return r.text

    def monitorpointtype(self):
        r = self.session.get("monitorPointType")
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
            r = self.session.post(
                f"monitoredObject/action/gethistorydata/{object_id}", data=params
            )
            r.raise_for_status()
            return r.text
        except HTTPError as exc:
            logging.error(f"HTTPError: {exc}")
            raise
        except Exception as exc:
            logging.error(exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name=__name__)
    vt = VersaTrak()
