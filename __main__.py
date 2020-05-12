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
print("Launching ChromeDriver...")
driver = launch_chromedriver_for_finsemble_from_src(PATH_TO_FINSEMBLE_SEED, PATH_TO_CHROMEDRIVER)
# OR, use: driver = launch_chromedriver_for_finsemble_from_exe(PATH_TO_FINSEMBLE_EXE, PATH_TO_CHROMEDRIVER)


print("Preparing to discover Finsemble components with Selenium...")
component_discoverer = FinsembleComponentDiscoverer(driver)


print("Locating Finsemble Toolbar with Selenium...")
toolbar_handle = component_discoverer.get_selenium_handle_of_page_containing_url('toolbar.html')
driver.switch_to.window(toolbar_handle)


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


print("Locating Welcome Component with Selenium...")
welcome_component_handle = component_discoverer.get_selenium_handle_of_page_containing_url('welcome.html')
driver.switch_to.window(welcome_component_handle)


print("Zooming in & out on the Welcome Component via hotkeys...")
welcome_component_body = driver.find_element(By.TAG_NAME, 'body')
for i in range(5):
    welcome_component_body.send_keys(Keys.CONTROL, Keys.ADD)
for i in range(5):
    welcome_component_body.send_keys(Keys.CONTROL, Keys.SUBTRACT)


print("Clicking the blue 'Launch Docs' button within the Welcome Component...")
launch_docs_button = driver.find_element(By.ID, 'launchTutorial')
driver.execute_script("arguments[0].click();", launch_docs_button)


print("Executing JavaScript to switch back to Default Workspace...")
driver.execute_async_script(
    """
    FSBL.Clients.WorkspaceClient.switchTo({name: arguments[0]}, (err, res) => { arguments[2](res); });
    """,
    "Default Workspace", {})


print("Closing ChromeDriver...")
driver.quit()

print("Goodbye.")
