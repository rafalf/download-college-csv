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
import csv

scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
logger = logging.getLogger(os.path.basename(__file__))

DOWNLOADED = 'CourseRetSuccessSumm.csv'
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWN_PATH = os.path.join(FILE_DIR, 'download')


def get_driver():
    # driver
    if platform.system() == 'Darwin':
        driver = webdriver.Chrome()
    else:
        driver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": DOWN_PATH}
        chromeOptions.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
    driver.maximize_window()

    driver.get(scrape_url)
    logger.info('url opened : {}'.format(scrape_url))
    return driver


def scrape(college, wait_to_load, screen_cap, driver):

    wait = WebDriverWait(driver, 10)

    for counter in range(5):

        try:
            driver.refresh()

            # state district college
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
            time.sleep(2)
            distr_id = 'ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBI2T0'
            wait.until(EC.element_to_be_clickable((By.ID, distr_id)))

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBT tr:nth-of-type(3)'))).click()
            time.sleep(2)

            # college
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))

            college_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
            wait.until(EC.presence_of_element_located((By.ID, college_id)))
            js_script = "document.getElementById('{}').click();".format(college_id)
            driver.execute_script(js_script)
            break
        except:
            logger.info('Failed. Will retry up to 5 times to select the college --> ({})'.format(counter))

    el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
    el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
    logger.info("Selected college: ({}): {}".format(college, el.text))
    college_name = el.text

    down_college_specific = os.path.join(DOWN_PATH, college_name)
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

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click checkboxes
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_0'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_1'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_2'))).click()

    # click update report
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport_CD'))).click()

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click csv
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()

    if screen_cap:
        driver.save_screenshot(os.path.join(down_college_specific, college_name.lower() + ".png"))

    time.sleep(5)

    # click export as
    logger.info('click export to csv --> browser starts downloading')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')), message='element not clickable').click()

    _move_file(DOWN_PATH, down_college_specific)

    return college_name


def print_all_colleges(driver):

    wait = WebDriverWait(driver, 10)

    # state district college
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBT tr:nth-of-type(3)'))).click()
    time.sleep(2)

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
    for _ in range(60):
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
    else:
        logger.warning("file not downloaded".format(DOWNLOADED))
        raise Exception('file not downloaded')

    try:
        copyfile(os.path.join(source, DOWNLOADED), os.path.join(dest, DOWNLOADED))
        logger.info('copied as: {}'.format(os.path.join(dest, DOWNLOADED)))

        os.remove(os.path.join(source, DOWNLOADED))
        logger.info('deleted: {}'.format(os.path.join(source, DOWNLOADED)))
    except:
        logger.warning("failed to copy, delete file: {}".format(DOWNLOADED))
        raise Exception('failed to copy, delete file')


def _wait_until_loaded(wait_, driver):

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


def _write_row(row):
    with open('./logs/scraped.csv', 'ab') as hlr:
        wrt = csv.writer(hlr, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        wrt.writerow(row)
        logger.info('added to scraped.csv file: {}'.format(row))


if __name__ == '__main__':
    verbose = None
    log_file = None
    college = None
    print_col = None
    screen_cap = None
    wait_to_load = 3600
    college = "all"
    scraped_college = 'Unknown'
    retry = 3

    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vc:lpsr:", ["verbose", "college=", 'log-file', 'print-college',
                                                  'screen-capture', "retry="])
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-c", "--college"):
            college = arg.split(',')
        elif opt in ("-l", "--log-file"):
            log_file = True
        elif opt in ("-p", "--print-college"):
            print_col = True
        elif opt in ("-s", "--screen-capture"):
            screen_cap = True
        elif opt in ("-r", "--retry"):
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
    logger.info('Variables:' )
    logger.info('FILE_DIR: {}'.format(FILE_DIR))
    logger.info('DOWN_PATH: {}'.format(DOWN_PATH))

    if college == 'all' or print_col:
        driver = get_driver()
        college = print_all_colleges(driver)
        driver.quit()
        if print_col:
            sys.exit(0)

    for c in college:
        for _ in range(retry):
            try:
                if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED)):
                    os.remove(os.path.join(DOWN_PATH, DOWNLOADED))

                driver = get_driver()
                driver.set_page_load_timeout(3600)

                scraped_college = scrape(c, wait_to_load, screen_cap, driver)
                logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
                result = 'Complete'
                break
            except TimeoutException:
                logger.warning('TimeoutException. Will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
                result = 'TimeoutException'
            except StaleElementReferenceException:
                logger.warning('StaleElementReferenceException. Will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
                result = 'StaleElementReferenceException'
            except:
                logger.warning('UndefinedException. Will retry up to 3 times')
                logger.debug('err: ', exc_info=True)
                result = 'UndefinedException'
            finally:
                _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                driver.quit()