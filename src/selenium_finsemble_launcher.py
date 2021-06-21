from __future__ import annotations
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from os import path, environ

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions


def launch_chromedriver_for_finsemble_from_src(path_to_finsemble_project: str, path_to_chromedriver: str) -> WebDriver:
    """
    Given that Finsemble server is already running (e.g. `yarn server` in finsemble-seed), this method will launch
    a local Finsemble project from src as an Electron app with Selenium + ChromeDriver hooked into it, allowing you
    to use the resulting `WebDriver` object to interact with Finsemble for use in automated testing.

    :param path_to_finsemble_project: The path to the location of the local Finsemble project (e.g. finsemble-seed) to
                                      launch. The project's underlying installations of `Electron` and
                                      `@finsemble/finsemble-electron-adapter` within `node_modules` will be used
                                      to launch Selenium + ChromeDriver.
                                      E.g.: "%UserProfile%/Dev/Finsemble/finsemble-seed"
    :type path_to_finsemble_project: str

    :param path_to_chromedriver: The path to the location of the chromedriver.exe binary to use. Please note that the
                                 ChromeDriver version is highly dependent on the underlying version of Finsemble,
                                 Electron, and Chromium under test. If a version of ChromeDriver is used that does not
                                 match the underlying Chromium <--> Electron <--> Finsemble under test, then Selenium
                                 will fail to start and this method will raise an exception.
                                 E.g.: "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_78/win32/chromedriver.exe"
    :type path_to_chromedriver: str

    :return: A Selenium `WebDriver` object that is hooked into the newly-launched Finsemble application under test.
    :rtype: WebDriver
    """

    try:
        # BEFORE launching ChromeDriver, we need to set the `ELECTRON_DEV` environment variable so that Finsemble is
        # launched in development mode. (Electron-applications can't be tested via e2e while in production mode.)
        # Without setting this flag, you'll get an "Unable to find embedded manifest URL." error on startup.
        environ['ELECTRON_DEV'] = 'true'

        # Generate the specific `ChromeOptions` needed to launch Finsemble from src and then pass those options in
        # to launch Finsemble as an Electron app with Selenium + ChromeDriver hooked in.
        chrome_options = _get_chrome_options_for_finsemble_from_src(path_to_finsemble_project)
        driver = _launch_chromedriver_for_electron_app(path_to_chromedriver, chrome_options)
        return driver
    except WebDriverException as e:
        if 'unable to discover open pages' in e.msg:
            raise Exception(f"WebDriverException encountered: {e.msg}\n\n"
                            f"This probably means you're either using the wrong version of ChromeDriver (see README),\n"
                            f"or Finsemble is not running. (Try `yarn server` in finsemble-seed)")
        else:
            raise


def launch_chromedriver_for_finsemble_from_exe(path_to_finsemble_exe: str, path_to_chromedriver: str) -> WebDriver:
    """
    Given that Finsemble has been built and installed as an exe on this machine, this method will launch
    the compiled Finsemble exe as an Electron app with Selenium + ChromeDriver hooked into it, allowing you
    to use the resulting `WebDriver` object to interact with Finsemble for use in automated testing.

    :param path_to_finsemble_exe: The path to the location of the installed Finsemble executable to launch. Keep in
                                  mind that this should be the application executable itself, NOT the installer
                                  executable. (i.e. this should probably be a location within %LocalAppData%)
                                  E.g.: "%LocalAppData%/XyzDev/app-1.0.0/XyzDev.exe"
    :type path_to_finsemble_exe: str

    :param path_to_chromedriver: The path to the location of the chromedriver.exe binary to use. Please note that the
                                 ChromeDriver version is highly dependent on the underlying version of Finsemble,
                                 Electron, and Chromium under test. If a version of ChromeDriver is used that does not
                                 match the underlying Chromium <--> Electron <--> Finsemble under test, then Selenium
                                 will fail to start and this method will raise an exception.
                                 E.g.: "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_78/win32/chromedriver.exe"
    :type path_to_chromedriver: str

    :return: A Selenium `WebDriver` object that is hooked into the newly-launched Finsemble application under test.
    :rtype: WebDriver
    """

    try:
        # Generate the specific `ChromeOptions` needed to launch Finsemble from exe and then pass those options in
        # to launch Finsemble as an Electron app with Selenium + ChromeDriver hooked in.
        chrome_options = _get_chrome_options_for_finsemble_from_exe(path_to_finsemble_exe)
        driver = _launch_chromedriver_for_electron_app(path_to_chromedriver, chrome_options)
        return driver
    except WebDriverException as e:
        if 'unable to discover open pages' in e.msg:
            raise Exception(f"WebDriverException encountered: {e.msg}\n\n"
                            f"This probably means you're either using the wrong version of ChromeDriver (see README),\n"
                            f"or the Finsemble configuration referenced by the target Finsemble exe is not valid.\n"
                            f"(Was the exe properly built to target a server that's currently running?)")
        else:
            raise


def _get_chrome_options_for_finsemble_from_src(path_to_finsemble_project: str) -> ChromeOptions:
    """
    Depending on whether we're launching from src or from a pre-built exe, we need to pass a different set of
    `ChromeOptions` when we later go to instantiate a Chrome `WebDriver` object with Selenium.

    This method will generate the necessary `ChromeOptions` for launching Finsemble from src with Selenium.

    :param path_to_finsemble_project: The path to the location of the local Finsemble project (e.g. finsemble-seed) to
                                      launch. The project's underlying installations of `Electron` and
                                      `@finsemble/finsemble-electron-adapter` within `node_modules` will be used
                                      to launch Selenium + ChromeDriver.
                                      E.g.: "%UserProfile%/Dev/Finsemble/finsemble-seed"
    :type path_to_finsemble_project: str

    :return: A set of Chrome Options with the necessary fields set in order to launch the Finsemble project from src
             via Selenium + ChromeDriver.
    :rtype: ChromeOptions
    """

    # Convert partial paths & environment shortcuts to full-fledged paths.
    path_to_finsemble_project = path.abspath(path.expandvars(path_to_finsemble_project))

    # In order to launch Finsemble from src (e.g. a locally-hosted `finsemble-seed` repo), we need to pass two things
    # into the `ChromeOptions` object that will eventually be used to launch Selenium + ChromeDriver:
    #   1. A path to `electron.exe` itself, which we'll get from the `node_modules` directory.
    #   2. A path to the Finsemble Electron Adapter's `app.js` startup script, which boot-straps
    #      the entire process of starting a Finsemble application. This is also installed under `node_modules`.

    path_to_electron_exe = path.join(
        path_to_finsemble_project, 'node_modules', 'electron', 'dist', 'electron.exe')
    path_to_fea_startup = path.join(
        path_to_finsemble_project, 'node_modules', '@finsemble', 'finsemble-electron-adapter', 'dist', 'app.js')

    # Generate a new `ChromeOptions` object with the above two pieces of information so that Finsemble can be
    # launched with Selenium + ChromeDriver.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = path_to_electron_exe
    chrome_options.add_argument(f'app={path_to_fea_startup}')

    return chrome_options


def _get_chrome_options_for_finsemble_from_exe(path_to_finsemble_exe: str) -> ChromeOptions:
    """
    Depending on whether we're launching from src or from a pre-built exe, we need to pass a different set of
    `ChromeOptions` when we later go to instantiate a Chrome `WebDriver` object with Selenium.

    This method will generate the necessary `ChromeOptions` for launching an installed Finsemble exe with Selenium.

    :param path_to_finsemble_exe: The path to the location of the installed Finsemble executable to launch. Keep in
                                  mind that this should be the application executable itself, NOT the installer
                                  executable. (i.e. this should probably be a location within %LocalAppData%)
                                  E.g.: "%LocalAppData%/XyzDev/app-1.0.0/XyzDev.exe"
    :type path_to_finsemble_exe: str

    :return: A set of Chrome Options with the necessary fields set in order to launch the Finsemble project from src
             via Selenium + ChromeDriver.
    :rtype: ChromeOptions
    """

    # Convert partial paths & environment shortcuts to full-fledged paths.
    path_to_finsemble_exe = path.abspath(path.expandvars(path_to_finsemble_exe))

    # Generate a new `ChromeObjects` object so that a pre-compiled Finsemble exe
    # can be launched with Selenium + ChromeDriver.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = path_to_finsemble_exe
    chrome_options.add_argument('--no-sandbox')

    return chrome_options


def _launch_chromedriver_for_electron_app(path_to_chromedriver: str, chrome_options: ChromeOptions) -> WebDriver:
    """
    Launch the Electron application defined by the given Chrome Options and hook Selenium + ChromeDriver into it.

    :param path_to_chromedriver: The path to the location of the chromedriver.exe binary to use. Please note that the
                                 ChromeDriver version is highly dependent on the underlying version of Finsemble,
                                 Electron, and Chromium under test. If a version of ChromeDriver is used that does not
                                 match the underlying Chromium <--> Electron <--> Finsemble under test, then Selenium
                                 will fail to start and this method will raise an exception.
                                 E.g.: "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_78/win32/chromedriver.exe"
    :type path_to_chromedriver: str

    :param chrome_options: A set of Chrome Options that define how to launch the desired Electron application.
    :type chrome_options: ChromeOptions

    :return: A Selenium WebDriver object that is hooked into the newly-launched Electron application under test.
    :rtype: WebDriver
    """

    # Convert partial paths & environment shortcuts to full-fledged paths.
    path_to_chromedriver = path.abspath(path.expandvars(path_to_chromedriver))

    # Set any additional ChromeOptions needed to hook Selenium + ChromeDriver into an Electron app.
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_experimental_option('w3c', False)

    # Launch and return the Electron app with Selenium + ChromeDriver hooked into it.
    driver = webdriver.Chrome(executable_path=path_to_chromedriver, options=chrome_options)
    return driver
