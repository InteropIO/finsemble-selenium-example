from src.selenium_finsemble_launcher import \
    launch_chromedriver_for_finsemble_from_src, launch_chromedriver_for_finsemble_from_exe
from src.finsemble_component_discoverer import FinsembleComponentDiscoverer
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Paths to Finsemble. Change these per your local environment.
# There are two ways that you can launch a Finsemble application with Selenium + ChromeDriver,
# and this script demonstrates using either way:
#   1. Launch "from src", i.e. given a local Finsemble project (e.g. finsemble-seed) that's running in the background
#      via `npm run server`, launch Electron & configure it run your local Finsemble app.
#   2. Launch "from exe", i.e. given a precompiled installed executable of Finsemble (e.g. XyzDev.exe) that's been
#      built & configured to use a Finsemble configuration from a server, launch the executable directly.
PATH_TO_FINSEMBLE_SEED = "%UserProfile%/Dev/Finsemble/finsemble-seed"
PATH_TO_FINSEMBLE_EXE = "%LocalAppData%/XyzDev/app-1.0.0/XyzDev.exe"

# Path to ChromeDriver. Change this per your local environment.
# Please note that the ChromeDriver version you need to use is highly dependent on the underlying
# version of the technology stack (Finsemble <--> Electron <--> Chromium) under test. If there is a version mismatch
# between ChromeDriver and the application's underlying Chromium, your automated test scripts will fail on startup.
PATH_TO_CHROMEDRIVER = "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_78/win32/chromedriver.exe"


# Launch Finsemble with Selenium + ChromeDriver hooked into it.
print("Launching Finsemble + ChromeDriver...")
driver = launch_chromedriver_for_finsemble_from_src(PATH_TO_FINSEMBLE_SEED, PATH_TO_CHROMEDRIVER)
# OR, use: driver = launch_chromedriver_for_finsemble_from_exe(PATH_TO_FINSEMBLE_EXE, PATH_TO_CHROMEDRIVER)


# The `driver` object is now hooked into Finsemble. Finsemble is a multi-window application, so you can query on
# `driver.window_handles` to get a collection of handles that you can switch between using `driver.switch_to.window()`,
# but there's no easy way of locating specific components using that method... Out of 30 windows, how do you tell which
# one corresponds to the Toolbar or to a specific component within your workspace?

# The `FinsembleComponentDiscoverer` is one type of mechanism you can use to abstract that kind of logic out of your
# automation code to make it easy to find specific components by looking for their URL signatures.
print("Preparing to discover Finsemble components with Selenium...")
component_discoverer = FinsembleComponentDiscoverer(driver)


# You can use a combination of UI interactions with Selenium (locate & click on elements in the DOM, like a user would)
# as well as JavaScript calls to the Finsemble API to automate numerous types of functionality. Not every component
# available to use has access to the `FSBL` API, but we know that the Toolbar does, so locate it and use it to execute
# JavaScript to call Finsemble API methods.
print("Locating Finsemble Toolbar with Selenium...")
toolbar_handle = component_discoverer.get_selenium_handle_of_page_containing_url('toolbar.html')
driver.switch_to.window(toolbar_handle)


# Specifics of how to use Finsemble API calls can be found in our online documentation:
# https://documentation.chartiq.com/finsemble/
# You should get comfortable with both the `driver.execute_script()` and `driver.execute_async_script()` methods within
# Selenium, and how you can return values via callbacks or promises back into your automation code.
print("Executing JavaScript to create a new workspace via the Finsemble API...")
driver.execute_async_script(
    """
    FSBL.Clients.WorkspaceClient.createWorkspace(arguments[0], arguments[1], (err, res) => { arguments[2](res); });
    """,
    "Automated Workspace", {})


print("Executing JavaScript to launch a Welcome Component...")
driver.execute_async_script(
    """
    FSBL.Clients.LauncherClient.spawn(arguments[0], arguments[1], (err, res) => { arguments[2](res); });
    """,
    "Welcome Component", {"addToWorkspace": True})


# We can use the same `FinsembleComponentDiscoverer` as above to easily find the new Welcome Component that we
# just launched, and target it with Selenium.
print("Locating Welcome Component with Selenium...")
welcome_component_handle = component_discoverer.get_selenium_handle_of_page_containing_url('welcome.html')
driver.switch_to.window(welcome_component_handle)


# All standard Selenium operations that you would perform in a normal web app are available to you even from within
# Finsemble. You can send keyboard input into a component...
print("Zooming in & out on the Welcome Component via hotkeys...")
welcome_component_body = driver.find_element(By.TAG_NAME, 'body')
for i in range(5):
    welcome_component_body.send_keys(Keys.CONTROL, Keys.ADD)
for i in range(5):
    welcome_component_body.send_keys(Keys.CONTROL, Keys.SUBTRACT)


# ... And you can also locate DOM elements to interact with. In a real-world test automation framework, you should
# adhere to the "page-object-model" and define page objects for each of the components under test. That would also be
# the ideal place to abstract out the effort of manually switching Selenium focus across multiple components, too.
print("Clicking the blue 'Launch Docs' button within the Welcome Component...")
launch_docs_button = driver.find_element(By.ID, 'launchTutorial')
driver.execute_script("arguments[0].click();", launch_docs_button)


# Be sure to clean up at the end of your automated test runs.
print("Executing JavaScript to switch back to Default Workspace...")
driver.execute_async_script(
    """
    FSBL.Clients.WorkspaceClient.switchTo({name: arguments[0]}, (err, res) => { arguments[2](res); });
    """,
    "Default Workspace", {})

print("Closing ChromeDriver...")
driver.quit()

print("Goodbye.")
