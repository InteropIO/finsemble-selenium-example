from src.selenium_finsemble_launcher import \
    launch_chromedriver_for_finsemble_from_src, launch_chromedriver_for_finsemble_from_exe


# Paths to Finsemble. There are two ways that you can launch a Finsemble application with Selenium + ChromeDriver,
# and this script demonstrates using either way:
#   1. Launch "from src", i.e. given a local Finsemble project (e.g. finsemble-seed) that's running in the background
#      via `npm run server`, launch Electron & configure it run your local Finsemble app.
#   2. Launch "from exe", i.e. given a precompiled installed executable of Finsemble (e.g. XyzDev.exe) that's been
#      built & configured to use a Finsemble configuration from a server, launch the executable directly.
PATH_TO_FINSEMBLE_SEED = "%UserProfile%/Dev/Finsemble/finsemble-seed"
PATH_TO_FINSEMBLE_EXE = "%LocalAppData%/XyzDev/app-1.0.0/XyzDev.exe"

# Path to ChromeDriver. Please note that the ChromeDriver version you need to use is highly dependent on the underlying
# version of the technology stack (Finsemble <--> Electron <--> Chromium) under test. If there is a version mismatch
# between ChromeDriver and the application's underlying Chromium, your automated test scripts will fail on startup.
PATH_TO_CHROMEDRIVER = "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_78/win32/chromedriver.exe"


# Launch Finsemble with Selenium + ChromeDriver hooked into it.
print("Launching ChromeDriver...")
driver = launch_chromedriver_for_finsemble_from_src(PATH_TO_FINSEMBLE_SEED, PATH_TO_CHROMEDRIVER)
# OR, use: driver = launch_chromedriver_for_finsemble_from_exe(PATH_TO_FINSEMBLE_EXE, PATH_TO_CHROMEDRIVER)

print("Iterating window handles...")
for window_handle in driver.window_handles:
    driver.switch_to.window(window_handle)
    print(f">> Window Handle {window_handle}: {driver.current_url}")

print("Closing ChromeDriver...")
driver.quit()

print("Goodbye.")
