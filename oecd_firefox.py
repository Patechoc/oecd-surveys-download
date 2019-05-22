import os
import requests
from selenium import webdriver
from pathlib import Path
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# https://developers.google.com/web/updates/2017/04/headless-chrome#drivers which refers to this
# *** recommended setup ***: https://intoli.com/blog/running-selenium-with-headless-chrome/
# Capabilites: https://www.browserstack.com/automate/python

# configuring Selenium to work with headless Chrome
options = webdriver.ChromeOptions()
#### options.binary_location = '/usr/bin/google-chrome-unstable'
options.add_argument('headless')
# set the window size
options.add_argument('window-size=1200x600')
# set download directory
path = os.getcwd()
options.add_argument(f"download.default_directory={path}")
options.add_argument(f"download.prompt_for_download=false")  # TEST
# options.add_argument("profile.default_content_settings.popups=0") # TEST 

prefs = {"profile.default_content_settings.popups": 0,
         "download.prompt_for_download": False,
         "download.default_directory": path,
         "download.directory_upgrade": True,
         "browser.download.folderList": 1}
options.add_experimental_option("prefs", prefs)

os.environ['XDG_DOWNLOAD_DIR'] = path
desired_caps = {
    'prefs': {
            'download': {
                'default_directory': path, 
                "directory_upgrade": "true", 
                "extensions_to_open": "",
                "folderList": 1,
                }
              }
        }
desired_caps['browserstack.video'] = True
desired_caps['browserstack.networkLogs'] = 'true'
desired_caps['browser.download.folderList'] = 1



# initialize the driver
path_to_log = path + "/chromedriver.log" 
driver = webdriver.Chrome(options=options,
                          desired_capabilities=desired_caps,
                          service_args=["--verbose", f"--log-path={path_to_log}"])
print(driver.capabilities)




driver.get("http://www.google.com")
if not "Google" in driver.title:
    raise Exception("Unable to load google page!")
elem = driver.find_element_by_name("q")
elem.send_keys("BrowserStack")
elem.submit()
print(driver.title)





# driver = webdriver.Chrome(str(Path("drivers", "chromedriver").resolve()))
# driver = webdriver.Firefox()



# # https://selenium-python.readthedocs.io/faq.html#how-to-auto-save-files-using-custom-firefox-profile
# content_type = requests.head('https://www.python.org/').headers['content-type']
# print(content_type)




driver.set_page_load_timeout(30)
driver.get("https://qdd.oecd.org/subject.aspx?Subject=ACTION6")
print(driver.title)

btn_create_table = driver.find_element_by_id("updateData")
print(btn_create_table.text)
driver.save_screenshot('screenshot_01.png')
btn_create_table.click()
time.sleep(20)
print(driver.title)
btn_download = driver.find_element_by_id("excel-download")
driver.save_screenshot('screenshot_02.png')
print(btn_download.text)
resp = btn_download.click()
time.sleep(40)


from IPython import embed; embed()

driver.quit()

## TO TRY
## https://www.varunpant.com/posts/download-file-using-webdriver-firefox-and-python-selenium