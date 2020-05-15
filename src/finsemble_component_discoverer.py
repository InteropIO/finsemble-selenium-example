from __future__ import annotations
import time
from src.chromedriver_remote_debugger import RemoteDebugger
from typing import TYPE_CHECKING, Callable, List
if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class FinsembleComponentDiscoverer:
    """
    Finsemble can be thought of as, essentially, a multi-window web app, where each component within Finsemble
    (including "system components", like the Finsemble Toolbar) exist as separate Chromium instances that can be
    individually hooked into with Selenium.

    This class provides a few mechanisms to make it easier to search across all of the Chromium instances visible to
    Selenium for a specific component.
    """

    def __init__(self, driver: WebDriver) -> None:
        self._driver: WebDriver = driver
        self._remote_debugger: RemoteDebugger = RemoteDebugger(driver)

    def discover_all_available_pages(self) -> dict:
        """
        Return every single window handle (each one corresponding to a separate Chromium instance) that is currently
        "visible" to Selenium, along with the page URL & title for each one.

        :return: A dictionary keyed on every "window handle" (that can be used with the `driver.window.switch_to()`
                 method) representing all of the Chromium instances currently visible to the Selenium WebDriver object.
                 Each entry in this dictionary will contain the following attributes:
                 - "title" (str): The current title of this web page / Chromium instance / Finsemble component
                 - "url" (str): The current URL of this web page / Chromium instance / Finsemble component
        :rtype: dict
        """

        # Use Remote Debugging to discover all pages available to Selenium.
        if self._remote_debugger.is_available:
            return self._remote_debugger.get_pages()

        # Remote Debugging is not available for some reason...
        # Naively iterate over all available window handles with Selenium to generate the requested data structure.
        pages = {}
        for window_handle in self._driver.window_handles:
            self._driver.switch_to.window(window_handle)
            pages[window_handle] = {
                'title': self._driver.title,
                'url': self._driver.current_url
            }

        return pages

    def get_selenium_handle_of_page_containing_url(self, desired_url: str) -> str:
        """
        Search all of the available window handles (i.e. Chromium instances / web pages / Finsemble components)
        that are visible to Selenium and locate the specific one corresponding to the provided URL.

        :param desired_url: The URL of the window / web page / Finsemble component to search for. This is matched
                            on a "partial" basis, e.g. providing "toolbar.html" will match on a component whose full
                            URL is "http://localhost:3375/components/toolbar/toolbar.html"
        :type desired_url: str

        :return: The Selenium window handle corresponding to the window / web page / Finsemble component matching
                 the given URL. This window handle can then be passed directly into the `driver.switch_to.window()`
                 method.
        :rtype: str

        :raises Exception: If no matching Finsemble component can be found.
        """

        # Define an inline method that will search for the desired page so that we can pass it in as a callable
        # predicate in order to wait for the page to become visible.
        # (Components may still be loading when this method is called - wait for them to become visible.)
        def _locate_page():
            all_pages = self.discover_all_available_pages()
            matching_page_handle = next((handle for handle, page_data in all_pages.items()
                                         if desired_url.lower() in page_data['url'].lower()), None)
            return matching_page_handle

        # Wait for the desired window to exist & return its handle.
        try:
            return FinsembleComponentDiscoverer._wait_until(_locate_page, timeout_in_seconds=10)
        except TimeoutError:
            raise Exception(f'No component whose URL contains "{desired_url}" can be found.')

    def get_selenium_handles_of_all_pages_containing_url(self, desired_url: str) -> List[str]:
        """
        Search all of the available window handles (i.e. Chromium instances / web pages / Finsemble components)
        that are visible to Selenium and locate each one that corresponds to the provided URL.

        :param desired_url: The URL of the windows / web pages / Finsemble components to search for. This is matched
                            on a "partial" basis, e.g. providing "toolbar.html" will match on a component whose full
                            URL is "http://localhost:3375/components/toolbar/toolbar.html"
        :type desired_url: str

        :return: A collection of Selenium window handles corresponding to all of the windows / web pages / Finsemble
                 components that match the given URL. Any of these individual handles can then be passed directly into
                 the `driver.switch_to.window()` method. If no matching Finsemble components are found, then an empty
                 list will be returned.
        :rtype: List[str]
        """

        all_pages = self.discover_all_available_pages()
        matching_page_handles = [handle for handle, page_data in all_pages.items()
                                 if desired_url.lower() in page_data['url'].lower()]
        return matching_page_handles

    @staticmethod
    def _wait_until(predicate: Callable, timeout_in_seconds: int, *args, **kwargs):
        """
        Repeatedly call and wait for the specified callable predicate to return a "truth-y" value.

        :param predicate: A callable method or function that you wish to wait on. This method will be called repeatedly.
                          If the result resolves to a "false-y" value, then the method will continue to be called.
                          If the result resolves to a "truth-y" value, then the result of the predicate will be
                          immediately returned.
        :type predicate: Callable

        :param timeout_in_seconds: The maximum time, in seconds, to wait for the specified predicate to eventually
                                   return a "truth-y" value.
        :type timeout_in_seconds: int

        :param args: Arbitrary non-keyworded args to pass into the callable predicate when it is invoked.

        :param kwargs: Arbitrary keyworded args to pass into the callable predicate when it is invoked.

        :return: The return value of the given callable predicate once it resolves to a "truth-y" value.

        :raises TimeoutError: If the given callable predicate does not resolve to a "truth-y" value before the given
                              timeout elapses.
        """

        # Invoke the method once first before starting any countdown, to guarantee that we can call the method at
        # least twice before timing out with an error.
        # (Handle cases in which the duration to execute the given predicate is longer than the allotted timeout.)
        result = predicate(*args, **kwargs)
        if bool(result):
            return result

        # Begin to repeatedly invoke the predicate within a countdown.
        end_time = time.time() + timeout_in_seconds
        while time.time() < end_time:
            result = predicate(*args, **kwargs)
            if bool(result):
                return result
            else:
                time.sleep(0.25)
        raise TimeoutError()
