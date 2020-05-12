from __future__ import annotations
import requests
from json import JSONDecodeError
from requests.exceptions import HTTPError, ConnectionError
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class RemoteDebugger:
    """
    ChromeDriver supports an additional "remote debugger" that is accessible outside of Selenium and the standard
    WebDriver WIRE protocol. This means that if ChromeDriver was instantiated with the `--remote-debugging-port`
    flag, an additional server is opened up that we can query to get some additional info and details that Selenium
    by itself may not provide. (So we can sometimes do things in a more efficient / clever way than may be possible
    otherwise with "pure" Selenium.)

    Further reading: https://blog.chromium.org/2011/05/remote-debugging-with-chrome-developer.html

    For our purposes, the main benefit here is that we can use the remote debugger to quickly "discover" all
    available Chromium handles visible to the Selenium ChromeDriver, along with their associated page URLs & titles,
    in a single query - something that is not possible with the native Selenium API.
    (We'd have to naively iterate one-by-one over all Selenium handles and query for URLs & titles, otherwise.)
    """

    def __init__(self, driver: WebDriver) -> None:
        self.debugger_address: Optional[str] = \
            RemoteDebugger._get_remote_debugger_address_from_selenium_driver_instance(driver)

    @property
    def is_available(self) -> bool:
        """
        Returns whether or not ChromeDriver Remote Debugging is available for the Selenium WebDriver object that
        this object was instantiated with.

        :return: True if Remote Debugging, and thus, any other methods defined in this class are available to the
                 Selenium WebDriver instance that this object was instantiated with; False otherwise.
        :rtype: bool
        """

        return bool(self.debugger_address)

    @staticmethod
    def _get_remote_debugger_address_from_selenium_driver_instance(driver: WebDriver) -> Optional[str]:
        """
        Query Selenium directly to determine the ChromeDriver Remote Debugger URL for the given WebDriver instance,
        if one is available.

        :param driver: A Selenium `WebDriver` object that is hooked into a Chromium-based application.
        :type driver: WebDriver

        :return: The URL of the Remote Debugger associated with Chromium instance that the given Selenium Driver is
                 hooked into, if one is available. If not (e.g. the application associated with the given Selenium
                 WebDriver instance does not support ChromeDriver Remote Debugging), then `None` is returned.
        :rtype: Optional[str]
        """

        try:
            # noinspection PyProtectedMember
            selenium_command_executor_url = driver.command_executor._url

            # Query the underlying Selenium server to get details about the remote debugger address.
            sessions_data = requests.get(f'{selenium_command_executor_url}/sessions').json()
            debugger_address = sessions_data['value'][0]['capabilities']['goog:chromeOptions']['debuggerAddress']
            if not debugger_address.startswith('http'):
                debugger_address = f'http://{debugger_address}'

            # Verify that the reported remote debugger address is actually valid.
            test_request = requests.get(f'{debugger_address}/json')
            test_request.raise_for_status()

            # There is a valid Remote Debugger address associated with this Selenium ChromeDriver instance that we
            # can query against.
            return debugger_address
        except (HTTPError, ConnectionError, JSONDecodeError, ConnectionRefusedError, KeyError):
            # Anything that goes wrong with querying or parsing the Selenium command executor URL for data about
            # a ChromeDriver Remote Debugger means that there is no valid Remote Debugger that we can use.
            return None

    def get_pages(self) -> Optional[dict]:
        """
        Use the Remote Debugger to query for all available Chromium instances that can be hooked into with Selenium.
        This is similar to using Selenium's built-in `driver.window_handles`, but this method will also return the
        page URLs and titles associated with each window handle, whereas if you wanted to get this same information
        without using the Remote Debugger (i.e. with native Selenium), you'd have to naively iterate over
        `driver.window_handles` to query for each page URL & title, one-by-one.

        :return: If Remote Debugging is available for the associated Selenium WebDriver instance, this will return a
                 dictionary keyed on Selenium window handles, with each key containing the values "title" and "url"
                 corresponding to that page.
                 If Remote Debugging is not available for the associated Selenium WebDriver instance, `None`
                 is returned instead.
        :rtype: Optional[dict]
        """

        if not self.is_available:
            return None

        pages = {}

        debugger_data = requests.get(f'{self.debugger_address}/json').json()
        pages_data = [obj for obj in debugger_data if obj['type'] == 'page']

        for page_data in pages_data:
            page_id = f'CDwindow-{page_data["id"]}'
            page = {
                'title': page_data['title'],
                'url': page_data['url']
            }
            pages[page_id] = page

        return pages
