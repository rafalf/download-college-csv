#!/usr/bin/env python

# pip instal -U selenium

import os
import sys
import getopt
import logging
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
import platform
from shutil import copyfile

scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
logger = logging.getLogger(os.path.basename(__file__))

DOWNLOADED = 'CourseRetSuccessSumm.csv'

# driver
if platform.system() == 'Darwin':
    driver = webdriver.Chrome()
else:
    driver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

    chromeOptions = webdriver.ChromeOptions()
    down_path = os.path.join(os.path.dirname(__file__), 'download')
    prefs = {"download.default_directory": down_path}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)

driver.maximize_window()


def scrape(college, wait_to_load, screen_cap):

    driver.get(scrape_url)
    logger.info('url opened : {}'.format(scrape_url))

    wait = WebDriverWait(driver, 10)

    # state district college
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBI2T0'))).click()

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()

    # college
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
    time.sleep(5)

    college_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
    js_script = "document.getElementById('{}').click();".format(college_id)
    driver.execute_script(js_script)

    el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
    el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
    logger.info("Selected college: ({}): {}".format(college, el.text))
    college_name = el.text

    down_college_specific = os.path.join(down_path, college_name)
    if not os.path.isdir(down_college_specific):
        os.mkdir(down_college_specific)
        logger.info("Created folder: {}".format(down_college_specific))

    # term
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditTerm'))).click()
    term_id = "ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_LBI0T1"
    js_script = "document.getElementById('{}').click();".format(term_id)
    driver.execute_script(js_script)

    # type program
    type_id = "ASPxRoundPanel1_ASPxDropDownEditTOP_DDD_DDTC_ASPxCallbackPanel1_ASPxTreeView1_CHK0"
    js_script = "document.getElementById('{}').click();".format(type_id)
    driver.execute_script(js_script)

    # instruction
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxIMType'))).click()
    instruction_id = "ASPxRoundPanel1_ASPxComboBoxIMType_DDD_L_LBI0T0"
    wait.until(EC.element_to_be_clickable((By.ID, instruction_id))).click()

    # click view report
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel1_RunReportASPxButton_CD'))).click()

    _wait_until_loaded(wait_to_load)
    time.sleep(2)

    # click checkboxes
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_0'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_1'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_2'))).click()

    # click update report
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport_CD'))).click()

    _wait_until_loaded(wait_to_load)
    time.sleep(2)

    # click csv
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()

    if screen_cap:
        driver.save_screenshot(os.path.join(down_college_specific, college_name.lower() + ".png"))

    # click export as
    logger.info('click export to csv ... browser starts downloading')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD'))).click()

    _move_file(down_path, down_college_specific)


def print_all_colleges():

    driver.get(scrape_url)
    logger.info('url opened : {}'.format(scrape_url))

    wait = WebDriverWait(driver, 10)

    # state district college
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBI2T0'))).click()

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
    time.sleep(3)
    all_coll = driver.find_elements_by_css_selector('#ASPxRoundPanel1_ASPxDropDownEditDistColl_'
                                                    'DDD_DDTC_checkListBoxDistColl_LBT .dxeListBoxItemRow_Aqua')

    l = []
    logger.info('Total colleges ({})'.format(len(all_coll)))
    for counter, coll in enumerate(all_coll):
        el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(counter)
        el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
        logger.info("no.--> ({}): --> {}".format(counter, el.text))
        l.append(counter)

    # dont return select all
    return l[1:]


def _move_file(source, dest):

    logger.info('checking downloaded file')
    for _ in range(30):
        files_ = os.listdir(source)
        if DOWNLOADED in files_:
            sys.stdout.write('\n')
            sys.stdout.flush()
            logger.info('file downloaded: {}'.format(DOWNLOADED))
            break
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
    try:
        copyfile(os.path.join(source, DOWNLOADED), os.path.join(dest, DOWNLOADED))
        logger.info('copied as: ' + os.path.join(dest, DOWNLOADED))
    except:
        logger.warning("failed to copy file".format(DOWNLOADED))

    try:
        os.remove(os.path.join(source, DOWNLOADED))
        logger.info('deleted as: ' + os.path.join(source, DOWNLOADED))
    except:
        logger.warning("failed to delete file: {}".format(DOWNLOADED))


def _wait_until_loaded(wait_):

    try:
        for _ in range(10):
            el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ASPxRoundPanel3_ASPxPivotGrid1_TL')))
            time.sleep(1)
            if el.is_displayed():
                logger.info('loading data')
                break
        else:
            logger.warning('loading data element not displaying')

        for _ in range(wait_):
            el = driver.find_element_by_id('ASPxRoundPanel3_ASPxPivotGrid1_TL')
            if not el.is_displayed():
                sys.stdout.write('\n')
                sys.stdout.flush()
                logger.info('loaded')
                return
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
    except TimeoutException:
        logger.warning('loading data element not displaying')


if __name__ == '__main__':
    dwn_folder = None
    verbose = None
    log_file = None
    college = None
    print_col = None
    screen_cap = None
    wait_to_load = 3600
    college = ['1']

    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vw:lpt", ["verbose", "college=", 'log-file', 'print-college', 'tree'])
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-c", "--college"):
            college = arg.split(',')
        elif opt in ("-l", "--log-file"):
            log_file = True
        elif opt in ("-p", "--print-college"):
            print_col = True
        elif opt in ("-w", "--wait-to-load"):
            wait_to_load = int(arg)
        elif opt in ("-t", "--tree"):
            screen_cap = True

    if log_file:
        log_file = os.path.join(os.path.dirname(__file__), 'logs',
                                    time.strftime('%d%m%y', time.localtime()) + "_scraper.log")
        file_hndlr = logging.FileHandler(log_file)
        logger.addHandler(file_hndlr)
        file_hndlr.setFormatter(ch)

    if verbose:
        logger.setLevel(logging.getLevelName('DEBUG'))
    else:
        logger.setLevel(logging.getLevelName('INFO'))
    logger.info('CLI args: {}'.format(opts))

    if college == 'all' or print_col:
        college = print_all_colleges()
        driver.delete_all_cookies()
        if print_col:
            driver.quit()
            sys.exit(0)

    for c in college:
        for _ in range(3):
            try:
                scrape(c, wait_to_load, screen_cap)
                logger.info('Completed for college no.{}'.format(c))
                break
            except TimeoutException:
                logger.warning('TimeoutException... will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
            except StaleElementReferenceException:
                logger.warning('StaleElementReferenceException...  will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
            except:
                logger.warning('Undefined exception...  will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
            finally:
                driver.delete_all_cookies()

    driver.quit()