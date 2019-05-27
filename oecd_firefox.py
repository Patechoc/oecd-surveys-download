"""
This module downloads OECD surveys through automated series of clicks using Selenium.
"""

import os
import time
import pandas as pd
from typing import List, Set
from pathlib import Path
from loguru import logger
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def get_oecd_urls_from_excel(input_dir: str = "data/inputs",
                             xlsx_file: str = "OECD_datasets_urls.xlsx") -> pd.DataFrame:
    """
    Get OECD URLs.

    Parameters
    ----------
    xlsx_file : str, optional
        Input file containing infos on the surveys, by default "OECD_datasets_urls.xlsx"

    Returns
    -------
    pd.DataFrame
        Pandas dataframe containing the codes, title and URLs of the surveys.
    """
    if input_dir:
        inputs_path = Path(input_dir)
    else:
        inputs_path = Path(".") / "data" / "inputs"
    path = inputs_path / xlsx_file
    df = pd.read_excel(path)
    return df


def get_current_outputs(destination_path: str, show: bool=True) -> List[str]:
    """
    Read surveys (Excel files) already present in destination_path/.
    
    Parameters
    ----------
    destination_path : str
        The path to the output folder
    show : bool, optional
        Print the content of the output folder if True, by default True
    
    Returns
    -------
    List[str]
        The names of surveys (Excel files) present in the output folder.
    """
    f = []
    for (dirpath, dirnames, filenames) in os.walk(
            destination_path.resolve()):
        f.extend(filenames)
    if show:
        print("surveys in data/outputs/: ")
        pprint(sorted(f))
    return sorted(f)


def get_survey_from_url(url: str,
                        destination_dir: str = "data/inputs") -> Set:
    """
    Download the OECD survey given the URL of its main page.
    
    Parameters
    ----------
    url : str
        The URL to the main page of an OECD report.
    destination_dir : str, optional
        Local output folder, by default "data/inputs"
    
    Returns
    -------
    Set
        The set of new file(s) downloaded.
    """
    if destination_dir:
        destination_path = Path(destination_dir)
    else:
        destination_path = Path(".") / "data" / "outputs"
    downloaded_surveys = get_current_outputs(destination_path, show=False)
    driver = setup_webdriver(destination_dir=destination_dir)
    driver.get(url)

    
    print("\n" + "#" * 100)
    print("Current URL: ", driver.current_url)
    print("Title page: ", driver.title)
    print("Coockies: ", driver.get_cookies())
    print("Session_id: ", driver.session_id)

    button_create_table = driver.find_element_by_id("updateData")
    driver.save_screenshot('./screenshots/screenshot_01.png')
    button_create_table.click()
    time.sleep(10)
    while not ("complete" in driver.execute_script('return document.readyState;')):
        print("waiting for page to finish loading...")
        time.sleep(1)

    button_download = driver.find_element_by_id("excel-download")
    driver.save_screenshot('./screenshots/screenshot_02.png')
    resp = button_download.click()
    # time.sleep(30)
    # while not ("complete" in driver.execute_script('return document.readyState;')):
    #     time.sleep(2)

    nb_outputs = len(downloaded_surveys)
    surveys_xlsx = get_current_outputs(destination_path, show=False)
    new_files = set(surveys_xlsx) - set(downloaded_surveys)
    start = time.time()
    now = start
    sec = 0
    while len(surveys_xlsx) == nb_outputs and now < start + 40:
        now = time.time()
        sec += 1
        print(f"downloading... ({sec}s)", end="\r")
        time.sleep(2)
        surveys_xlsx = get_current_outputs(destination_path, show=False)
        new_files = set(surveys_xlsx) - set(downloaded_surveys)
    print("New downloads: ", new_files)
    driver.quit()
    return new_files


def setup_webdriver(destination_dir: str = "/tmp"):
    """
    Configure and setup the Firefox webdriver.
    
    Parameters
    ----------
    destination_dir : str, optional
        The default folder for browser download, by default "/tmp".
    
    Returns
    -------
    webdriver
        A configured webdriver.
    """
    if destination_dir:
        destination_path = Path(destination_dir)
    else:
        destination_path = Path(".") / "data" / "outputs"
    destination_fullpath = str(destination_path.resolve())
    options = Options()
    options.add_argument('window-size=1200x600')
    options.headless = True  # True if running on headless remote server
    options.add_argument(
        f"download.default_directory={destination_fullpath}")
    options.add_argument(f"download.prompt_for_download=false")

    # configuring Selenium to work with Firefox
    profile = webdriver.FirefoxProfile()

    mime_types = ["image/png", "image/jpeg", "application/binary",
                  "application/pdf", "application/csv", "application/vnd.ms-excel",
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  "application/download", "application/octet-stream", "application/zip",
                  "application/x-rar-compressed", "application/x-gzip", "application/msword",
                  "text/csv", "text/csv/xls/zip/exe/msi"]

    # 2 indicates a custom (see: browser.download.dir) folder
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir',
                           destination_fullpath)
    # whether or not to show the Downloads window when a download begins.
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference(
        'browser.helperApps.neverAsk.saveToDisk',
        ", ".join(mime_types))
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    # profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    # profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference(
        "browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.useWindow", False)

    profile.update_preferences()
    driver = webdriver.Firefox(firefox_profile=profile,
                               options=options)
    driver.set_page_load_timeout(30)
    return driver


def main():
    destination_path = Path("data/outputs")
    destination_dir = destination_path.resolve()
    downloaded_surveys = get_current_outputs(destination_path, show=True)
    df = get_oecd_urls_from_excel(xlsx_file="OECD_datasets_urls.xlsx")
    for url in set(sorted(df.URL.to_list())):
        # url = "https://qdd.oecd.org/subject.aspx?Subject=ACTION6"
        try:
            surveys_xlsx = get_survey_from_url(
                url, destination_dir="data/outputs")
        except Exception as e:
            print("Error message: ", e)
            msg = f"The url '{url}' doesn't allow to download the survey!"
            print(msg)
            # logger.add("output.log", backtrace=True, diagnose=True)
            # logger.info(msg)

        # TODO: only add new survey if the excel file has changes
        # (https://matthewkudija.com/blog/2018/07/21/excel-diff/)


if __name__ == '__main__':
    main()
