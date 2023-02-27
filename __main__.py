from src.selenium_finsemble_launcher import \
    launch_chromedriver_for_finsemble_from_src, launch_chromedriver_for_finsemble_from_exe
from src.finsemble_component_discoverer import FinsembleComponentDiscoverer
from src.wait import wait_until
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Paths to Finsemble. Change these per your local environment.
# There are two ways that you can launch a Finsemble application with Selenium + ChromeDriver,
# and this script demonstrates using either way:
#   1. Launch "from src", i.e. given a local Finsemble project (e.g. finsemble-seed) that's running in the background
#      via `yarn server`, launch Electron & configure it run your local Finsemble app.
#   2. Launch "from exe", i.e. given a precompiled installed executable of Finsemble (e.g. Finsemble.exe) that's been
#      built & configured to use a Finsemble configuration from a server, launch the executable directly.
PATH_TO_FINSEMBLE_SEED = "%UserProfile%/Dev/finsemble-seed"
PATH_TO_FINSEMBLE_EXE = "%UserProfile%/Dev/Finsemble/finsemble-seed/Finsemble-win32-x64/Finsemble.exe"

# Path to ChromeDriver. Change this per your local environment.
# Please note that the ChromeDriver version you need to use is highly dependent on the underlying
# version of the technology stack (Finsemble <--> Electron <--> Chromium) under test. If there is a version mismatch
# between ChromeDriver and the application's underlying Chromium, your automated test scripts will fail on startup.
PATH_TO_CHROMEDRIVER = "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_98/win32/chromedriver.exe"


# Launch Finsemble with Selenium + ChromeDriver hooked into it.
print("Launching Finsemble + ChromeDriver...")
driver = launch_chromedriver_for_finsemble_from_src(PATH_TO_FINSEMBLE_SEED, PATH_TO_CHROMEDRIVER)
# OR, use the following if you want to test a build .exe instead of running from src:
# driver = launch_chromedriver_for_finsemble_from_exe(PATH_TO_FINSEMBLE_EXE, PATH_TO_CHROMEDRIVER)


# The `driver` object is now hooked into Finsemble. Finsemble is a multi-window application, so you can query on
# `driver.window_handles` to get a collection of handles that you can switch between using `driver.switch_to.window()`,
# but there's no easy way of locating specific components using that method... Out of 30 windows, how do you tell which
# one corresponds to the Toolbar or to a specific component within your workspace?

# The `FinsembleComponentDiscoverer` is one type of mechanism you can use to abstract that kind of logic out of your
# automation code to make it easy to find specific components by looking for their URL signatures.
print("Preparing to discover Finsemble components with Selenium...")
component_discoverer = FinsembleComponentDiscoverer(driver)


# You can use a combination of UI interactions with Selenium (locate & click on elements in the DOM, like a user would)
# as well as JavaScript calls to the Finsemble API to automate numerous types of functionality.
#
# We specifically know that Finsemble's Toolbar has access to the `FSBL` API, so we can hook into the Toolbar with
# Selenium and then execute JavaScript in order to interact directly with Finsemble's API.
print("Locating the Finsemble Toolbar with Selenium...")
toolbar_handle = component_discoverer.get_selenium_handle_of_page_containing_url('Toolbar/toolbar.html')
driver.switch_to.window(toolbar_handle)


# Specifics of how to use Finsemble API calls can be found in our online documentation:
# https://documentation.finsemble.com/docs/reference/APIReference
print("Creating a new workspace via the Finsemble API...")
driver.execute_script(
    "await FSBL.Clients.WorkspaceClient.createWorkspace(arguments[0], arguments[1]);",
    "Automated Workspace", {}
)


print("Launching an example ChartIQ app via the Finsemble API...")
driver.execute_script(
    "await FSBL.Clients.LauncherClient.spawn(arguments[0], arguments[1]);",
    "ChartIQ Example App", {"addToWorkspace": True}
)


# We can use the same `FinsembleComponentDiscoverer` as above to easily find the new app window that we
# just launched, and target it with Selenium.
print("Locating the example ChartIQ app window with Selenium...")
chartiq_app_handle = component_discoverer.get_selenium_handle_of_page_containing_url('chart/technical-analysis-chart.html')
driver.switch_to.window(chartiq_app_handle)


# All standard Selenium operations that you would perform in a normal web app are available to you even from within
# Finsemble. You can send keyboard input into an app's window...
print("Zooming out & in of the example ChartIQ app via hotkeys...")
chartiq_window_body = driver.find_element(By.TAG_NAME, 'body')
for i in range(5):
    chartiq_window_body.send_keys(Keys.CONTROL, Keys.SUBTRACT)  # Ctrl -
for i in range(5):
    chartiq_window_body.send_keys(Keys.CONTROL, Keys.ADD)  # Ctrl +


# ... And you can also locate DOM elements to interact with. In a larger e2e test framework, you should
# adhere to the "page-object-model" and define page objects for each of the app windows under test.
print("Clicking the example ChartIQ app's Share button with Selenium...")
driver.find_element(By.TAG_NAME, 'cq-share-button').click()
driver.find_element(By.TAG_NAME, 'cq-share-create').click()


# Use explicit "wait logic" to pause the e2e execution until the underlying app finishes working...
# (Better than hard-coded sleeps.)
def _get_share_url_when_complete() -> str:
    try:
        url = driver.find_element(By.CLASS_NAME, 'share-link-div').text
        return url if url.startswith("http") else ""
    except:
        return ""


print("Waiting for the example ChartIQ app to finish generating a screenshot...")
share_link_result = wait_until(lambda: _get_share_url_when_complete(), timeout_in_seconds=10)
print(f"Your screenshot generated by an e2e script is available at: {share_link_result}")


# Be sure to clean up at the end of your automated test runs.
print("Switching back to Default Workspace via the Finsemble API...")
driver.execute_script(
    "await FSBL.Clients.WorkspaceClient.switchTo({name: arguments[0]});",
    "Default Workspace"
)

print("Closing ChromeDriver...")
driver.quit()

print("Goodbye.")
