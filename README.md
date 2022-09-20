# finsemble-selenium-example
This is a very simple example Python project demonstrating how to integrate Finsemble and Selenium WebDriver for
end-to-end automated testing.

Although this example project is written in Python, the Selenium WebDriver bindings are available in a number of
languages & frameworks, and so the ideas presented in this implementation should be possible to port to any existing e2e
automation framework in a language of your choice.

## Recommended reading & prior knowledge
Some prior knowledge with [Selenium WebDriver](https://www.selenium.dev/documentation/en/webdriver/) is assumed. This
README and the accompanying code is designed to serve as a "getting started" repo to bootstrap your process of
integrating Selenium with Finsemble to write your own end-to-end test automation against your Finsemble applications,
but the basics of how to use Selenium at a high level is not covered here.

Similarly, this guide assumes that you already have a Finsemble application (e.g. `finsemble-seed`) ready to automate.
Details on setting up & configuring Finsemble are not covered here, so please reference the
[official Finsemble documentation](https://documentation.finsemble.com/docs/welcome/introduction/) and the 
[example Finsemble Seed README](https://github.com/ChartIQ/finsemble-seed/).

## Pre-requisites
1. [Python 3.7](https://www.python.org/downloads/release/python-373/)
2. The following items added to your `PATH` variable (basic Python dev environment setup), e.g. for Windows:
    1. `%LocalAppData%\Programs\Python\Python37`
    2. `%LocalAppData%\Programs\Python\Python37\Scripts`
    3. `%AppData%\Python\Python37\Scripts`
3. `$ pip3 install pipenv` for package installation and virtual environment management.
4. A Finsemble application (e.g. `finsemble-seed`) to automate.
5. An appropriate version of ChromeDriver downloaded (see below.)

## Install
```
$ git clone https://github.com/ChartIQ/finsemble-selenium-example.git
$ cd finsemble-selenium-example
$ pipenv install
```

## Selenium v3 vs. v4
Note that this example repo was written using the [Selenium v3](https://pypi.org/project/selenium/3.141.0/) API. Selenium v4 is a newer release but introduces a number of breaking changes to its API and thus will not work with this example repo without [code modifications](https://www.selenium.dev/documentation/webdriver/getting_started/upgrade_to_selenium_4/). The provided Pipfile in this repo specifically targets the latest v3 release, so following the above installation steps should install the correct working version without any further modifications. If you are deploying to other environments where you are not performing a standard `pipenv install`, ensure that Selenium v3 is referenced instead of v4.

## ChromeDriver
In addition to the example code provided in this repo, you also need an appropriate version of
[ChromeDriver](https://chromedriver.chromium.org/downloads) downloaded onto your machine. ChromeDriver is what actually
connects the automation code (i.e. this repo) to the application-under-test (i.e. Finsemble) via the Selenium API.

![](images/chromedriver_integration.png)

### ChromeDriver versioning
The version of ChromeDriver you need to use is highly dependent on the version of the underlying Chromium used in the
application-under-test, which in our case correlates directly with the version of Electron & Finsemble under test. Thus,
in order to download the correct version of ChromeDriver, you need to check the version of Chromium that is in use by
the Electron version in use by Finsemble.

The easiest way to do this is to simply launch the `node_modules/electron/dist/electron.exe` binary located within the
Finsemble application-under-test. (E.g. `finsemble-seed`)

Launching the `electron.exe` binary should result in a screen like the following:

![](images/electron_version.png)

The Chromium version associated with any given version of Electron is displayed at the top - this version is what should
be targeted when deciding on an appropriate version of ChromeDriver to download & use. For example, in the above image,
Chromium v78 is in use, so
[ChromeDriver v78](https://chromedriver.storage.googleapis.com/index.html?path=78.0.3904.105/) would be the proper
version to download & use for automation.

Keep in mind that, each time Electron (and thus, Chromium) is updated within your Finsemble application-under-test, you
will also need to keep ChromeDriver updated to an appropriate version.

## Setting up Finsemble for end-to-end automation
The example code provided in this repo demonstrates how you can automate Finsemble while launching either "from src"
(i.e., similar to how you run Finsemble in a dev environment via `yarn dev`) or "from exe" (i.e., using a
pre-compiled executable that's been installed to the system.)

Regardless of how you wish to launch Finsemble for automated testing, you still need to serve the Finsemble manifest
in order for the application to run.

When building from src, the Finsemble manifest is almost always locally-hosted, so you will need to run the following
command from your Finsemble application-under-test (e.g. `finsemble-seed`), *prior* to starting the automated testing:
```
$ yarn server
```

When launching from an exe, whether or not you need to locally-host depends entirely on how you've configured Finsemble
during the build phase. Executables may need to be locally-hosted in the same way as running from src, but in most
production or staging environments, the you will configure the exe to point to some external server.

## Running the automation code
The file `__main__.py` is the main entry-point for this example repo. There are a few lines of code at the very top that
you'll need to change locally:
```python
# [...]
PATH_TO_FINSEMBLE_SEED = "%UserProfile%/Dev/Finsemble/finsemble-seed"
PATH_TO_FINSEMBLE_EXE = "%UserProfile%/Dev/Finsemble/finsemble-seed/Finsemble-win32-x64/Finsemble.exe"

# [...]
PATH_TO_CHROMEDRIVER = "%UserProfile%/Dev/Utils/WebDrivers/chromedriver_102/win32/chromedriver.exe"
```

- `PATH_TO_FINSEMBLE_SEED`: The filepath pointing to the local dev environment of the Finsemble application-under-test 
(e.g. `finsemble-seed`), if you want to run the automation on a Finsemble application that's been built "from src".
  - As described above, the Finsemble manifest still needs to be served before launching any Finsemble automation with
    the example code in this repo. When running Finsemble "from src", you are usually locally-hosting the Finsemble
    server, so ensure that `yarn server` has been run from the application before kicking off any automation.
- `PATH_TO_FINSEMBLE_EXE`: The filepath pointing to the local Finsemble application executable under-test, if you want
to run the automation on a pre-built installed Finsemble standalone executable.
  - NOTE: Ensure that this is pointing to the unpacked/loose build (e.g. `/Finsemble-win32-x64/Finsemble.exe`) and NOT
    the installer executable. (e.g. `/installer/Finsemble.exe`)
- `PATH_TO_CHROMEDRIVER`: The filepath pointing to the `chromedriver.exe` that is versioned according to the version of
the underlying Electron/Chromium version in use by the Finsemble application-under-test (see above.)

With these variables set, and with the Finsemble manifest being served (either locally or externally), you can run the
`__main__.py` script. You should see Finsemble launch, create a new workspace, launch an example ChartIQ app, interact
with the ChartIQ app and utilize some of its specific features, switch Finsemble back to a standard workspace, and
finally shut down. Information about what the e2e script is doing will also be printed to the stdout console.

The `__main__.py` script, and the other supporting scripts are documented with comments, so you should be able to use
this is a jumping-off point to expand to build out automated functionality for your Finsemble application using the
standard Selenium WebDriver library in your language of choice.

## Limitations with WebDriver-based testing
Given that Finsemble is built on Electron, ChromeDriver-based automation tools like Selenium WebDriver are a perfect
starting point for building integrated end-to-end automated test cases within Finsemble. However, there are areas and
functionality within Finsemble that will not integrate as easily with Selenium, and will require additional technologies
not covered here. A few such common cases are:

- **Native & assimilated applications.** The code in this project demonstrates one way to easily locate specific types of
  windows with Selenium, including both system-level components like the Finsemble Toolbar, as well as user-defined
  workspace applications like the example ChartIQ app. All web components can be automated in this same fashion, but
  native or assimilated components (i.e. applications that have been integrated into Finsemble that are *not*
  Electron-based web apps, such as C#/.NET WPF apps or Java apps) will not be visible to Selenium and thus cannot have
  their UI automated in the same way. You will either need to communicate through these apps solely via Finsemble's API
  (e.g. use Selenium to execute JavaScript calls that will broadcast Router or FDC3 messages that your component responds
  to) or you will need to integrate additional UI automation technologies that can hook into these applications.
- **Mouse movement and dragging.** Selenium is primarily used to inspect & interact with the DOM,
  send keyboard input into, and execute JavaScript, within arbitrary web applications (including web-based Finsemble
  components.) More advanced UI interactions, such as drag-and-drop via the mouse, are not natively supported through
  the Selenium API, so additional technologies will need to be employed if you wish to automate this type of
  interaction.

## Troubleshooting common issues

### WebDriverException (unable to discover open pages) during initialization
An exception containing the following information may be thrown during the initialization of Selenium + ChromeDriver:
```
Exception: WebDriverException encountered: unknown error: unable to discover open pages
  (Driver info: chromedriver=78.0.3904.105 (60e2d8774a8151efa6a00b1f358371b1e0e07ee2-refs/branch-heads/3904@{#877}),platform=Windows NT 10.0.18362 x86_64) 
```

This means that Selenium + ChromeDriver was unable to hook into Finsemble. This is usually due to one of the following
reasons:
- **Finsemble may be unreachable.** Be sure that the Finsemble manifest is being served from an accessible location. If
  you are running Finsemble locally, you will need to start the Finsemble server with `yarn server` before running
  your automation. If you are running Finsemble from a production executable that pulls the Finsemble manifest and
  component configurations from an external server, be sure that the external server is reachable.
- **There may be a ChromeDriver mismatch.** Be sure that the version of `chromedriver.exe` you're using is supported
  for the version of Chromium / Electron / Finsemble under-test. (See above for more details on this.) If your
  automation has been working fine but you suddenly start encountering this error after upgrading to a newer version of
  Finsemble and/or Electron, this is the most likely scenario.
- **You may be targeting the wrong application.** This can occur especially if you're trying to automate & launch
  Finsemble from a compiled exe. Be aware that the `yarn makeInstaller` script generates two different directories, and
  you do not want the contents of the `/installer/` directory, but instead the directory with the loose/unpacked files.

### WebDriverException (no chrome binary at [...]) during initialization
An exception containing the following information may be thrown during the initialization of Selenium + ChromeDriver:
```
selenium.common.exceptions.WebDriverException: Message: unknown error: no chrome binary at C:\Users\Name\Dev\Finsemble\finsemble-seed\node_modules\electron\dist\electron.exe
  (Driver info: chromedriver=78.0.3904.105 (60e2d8774a8151efa6a00b1f358371b1e0e07ee2-refs/branch-heads/3904@{#877}),platform=Windows NT 10.0.18362 x86_64)
```

This means that no Finsemble application was found at the provided file path. Double-check to make sure file paths are
valid and also make sure that you've installed and built Finsemble at least once with (e.g. via 
`yarn install && yarn build`) if you're building from src.

### NoSuchWindowException (target window already closed) when using Selenium
An exception containing the following information may be thrown when interacting with the Selenium `WebDriver` object:
```
selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed
from unknown error: web view not found
  (Session info: chrome=78.0.3904.113)
  (Driver info: chromedriver=78.0.3904.105 (60e2d8774a8151efa6a00b1f358371b1e0e07ee2-refs/branch-heads/3904@{#877}),platform=Windows NT 10.0.18362 x86_64)
```

Simply put, this means you're trying to interact with a window that no longer exists. All calls that you make on the
Selenium `WebDriver` object will always target one specific window - this can be controlled via the
`driver.switch_to.window()` method. If your automation script performs an action that causes the current target window
to close, and then you attempt to use Selenium to execute JavaScript or query DOM elements without first switching to a
different window, you will get this error.

This commonly happens, for instance, after a workspace switch. Your e2e script may be focused on a specific
Finsemble workspace window, and then you reload or switch workspaces. The window that you were focused on will be
closed, so it's up to you to ensure that you switch to a valid window handle again before attempting to access the
Finsemble API.

### TimeoutException (script timeout) when executing async JavaScript through Selenium
An exception containing the following information may be thrown when using Selenium to execute JavaScript directly
within the Finsemble application:
```
selenium.common.exceptions.TimeoutException: Message: script timeout
  (Session info: chrome=78.0.3904.113)
  (Driver info: chromedriver=78.0.3904.105 (60e2d8774a8151efa6a00b1f358371b1e0e07ee2-refs/branch-heads/3904@{#877}),platform=Windows NT 10.0.18362 x86_64)
```

This generally means that the asynchronous script you are executing is not resolving to a return value that is getting
passed back into your automation code. While this could indicate a problem with the underlying asynchronous JavaScript
code within your application itself, this problem often arises from improperly calling & returning your JavaScript code
through Selenium.

#### Callbacks
If the underlying asynchronous JavaScript code is implemented using Callbacks, then the `execute_async_script()` method
should be used. It's important to make sure you invoke Selenium's own callback method when you are ready to return a
value, which is always injected to the very end of the `arguments[]` array.

E.g.:

WRONG (will result in a TimeoutException due to Selenium's injected callback never being invoked):
```python
result = driver.execute_async_script(
    "someAsyncFunctionWithCallback(arguments[0], arguments[1], cb => { return cb; });",
    first_arg, second_arg
)
```

RIGHT (invoke the final `arguments[]` item as a callback method for Selenium):
```python
result = driver.execute_async_script(
    "someAsyncFunctionWithCallback(arguments[0], arguments[1], cb => { arguments[2](cb); });",
    first_arg, second_arg
)
```

#### Promises
If the underlying asynchronous JavaScript code is implemented using Promises, then you don't even need to use the
`execute_async_script()` method. Simply treat the script as a synchronous call and use `execute_script()`.

E.g.:

WRONG (no need to use `execute_async_script()` when returning from a Promise):
```python
result = driver.execute_async_script(
    "return await someAsyncFunctionWithPromise(arguments[0], arguments[1]);",
    first_arg, second_arg
)
```

RIGHT (use `execute_script()` and simply `return` from the `await`ed Promise):
```python
result = driver.execute_script(
    "return await someAsyncFunctionWithPromise(arguments[0], arguments[1]);",
    first_arg, second_arg
)
```
