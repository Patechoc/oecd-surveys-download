import os
import requests
from selenium import webdriver
from pathlib import Path
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

## Objective: download ACTION6_22052019_102544.xlsx


# https://developers.google.com/web/updates/2017/04/headless-chrome#drivers which refers to this
# *** recommended setup ***: https://intoli.com/blog/running-selenium-with-headless-chrome/
# Capabilites: https://www.browserstack.com/automate/python

destination = "/home/patrick/Downloads/OECD"


options = Options()
options.add_argument('window-size=1200x600')
options.headless = True
options.add_argument(f"download.default_directory={destination}")
options.add_argument(f"download.prompt_for_download=false")  # TEST


# configuring Selenium to work with Firefox
profile = webdriver.FirefoxProfile()



# 2 indicates a custom (see: browser.download.dir) folder
profile.set_preference('browser.download.folderList', 2) 
profile.set_preference('browser.download.dir', destination)
# whether or not to show the Downloads window when a download begins.
profile.set_preference('browser.download.manager.showWhenStarting', False)

mime_types = ["image/png",
              "image/jpeg",
              "application/binary",
              "application/pdf",
              "application/csv",
              "application/vnd.ms-excel",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              "application/download",
              "application/octet-stream",
              "application/zip",
              "application/x-rar-compressed",
              "application/x-gzip",
              "application/msword",
              "text/csv",
              "text/csv/xls/zip/exe/msi"]
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', ", ".join(mime_types))

profile.set_preference("browser.download.manager.focusWhenStarting", False)
# profile.set_preference("browser.download.useDownloadDir", True)
profile.set_preference("browser.helperApps.alwaysAsk.force", False)
# profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
profile.set_preference("browser.download.manager.closeWhenDone", True)
profile.set_preference("browser.download.manager.showAlertOnComplete", False)
profile.set_preference("browser.download.manager.useWindow", False)


profile.update_preferences()
driver = webdriver.Firefox(firefox_profile=profile,
                           options=options,
                           executable_path="/home/patrick/Documents/dev/Apenhet/yangle/drivers/geckodriver")




driver.set_page_load_timeout(30)
url = "https://qdd.oecd.org/subject.aspx?Subject=ACTION6"
driver.get(url)

print("title page: ", driver.title)
print("coockies: ", driver.get_cookies() )
print("current URL: ", driver.current_url)
print("session_id: ", driver.session_id)

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



f = []
now = time.time()
seconds = 40
end = now + seconds
while not f and end > now:
    now = time.time()
    for (dirpath, dirnames, filenames) in os.walk(destination):
        f.extend(filenames)
        break
print("files: ", f)
driver.quit()
