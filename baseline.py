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
from selenium.common.exceptions import UnexpectedAlertPresentException
import platform
import xlsxwriter

logger = logging.getLogger(os.path.basename(__file__))

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(FILE_DIR, 'logs')
BASELINES = os.path.join(FILE_DIR, 'baselines')
SCRAPE_LOG = os.path.join(LOGS, 'scrape.csv')


class ExitException(Exception):
    pass


def get_driver(url):

    # driver
    if platform.system() == 'Darwin':
        driver = webdriver.Chrome()
    else:
        driver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
        chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.add_argument('headless')
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
    driver.maximize_window()

    driver.get(url)
    logger.info('Open url: {}'.format(url))
    return driver


def baseline_course_success(driver):

    page_data = []
    wait = WebDriverWait(driver, 10)

    coll = baseline_colleges(driver)
    page_data.append(coll)

    # select all
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditTerm'))).click()
    term_id = "ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_LBI0T1"
    js_script = "document.getElementById('{}').click();".format(term_id)
    driver.execute_script(js_script)

    term_locator = "#ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_LBT .dxeListBoxItem_Aqua.dxeT"
    all_ = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, term_locator)))
    terms_ = [opt.text.strip() for opt in all_]

    logger.info('Terms:')
    logger.info(terms_)
    page_data.append(terms_)

    # program type
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditTOP_B-1 img'))).click()
    time.sleep(5)

    program_type_locator = "#ASPxRoundPanel1_ASPxDropDownEditTOP_DDD_DDTC_ASPxCallbackPanel1_ASPxTreeView1_CD>ul>li>ul>" \
                           ".dxtv-subnd>div .dxtv-ndTxt"
    all_ = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, program_type_locator)))
    program_type_ = [opt.text.strip() for opt in all_]

    logger.info('Program types:')
    logger.info(program_type_)
    page_data.append(program_type_)

    # type program
    type_id = "ASPxRoundPanel1_ASPxDropDownEditTOP_DDD_DDTC_ASPxCallbackPanel1_ASPxTreeView1_CHK0"
    js_script = "document.getElementById('{}').click();".format(type_id)
    driver.execute_script(js_script)

    # instruction
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxIMType'))).click()

    instruction_locator = "#ASPxRoundPanel1_ASPxComboBoxIMType_DDD_L_LBT .dxeListBoxItem_Aqua"
    all_ = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, instruction_locator)))
    instruction_methods_ = [opt.text.strip() for opt in all_]

    logger.info('Instruction methods:')
    logger.info(instruction_methods_)
    page_data.append(instruction_methods_)

    checks = _get_checkboxes(driver)
    page_data.append(checks)

    _write_to_excel('course success', page_data)


def select_search_type():

    wait = WebDriverWait(driver, 10)

    # state district college
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
    time.sleep(2)

    logger.info('Search type: Collegewide Search')

    css_selector = '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBT tr:nth-of-type(3)'
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()
    time.sleep(2)
    logger.info('Search type selected')


def baseline_colleges(driver):

    wait = WebDriverWait(driver, 10)

    for counter in range(5):

        try:
            select_search_type()

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
            time.sleep(3)
            all_coll = driver.find_elements_by_css_selector('#ASPxRoundPanel1_ASPxDropDownEditDistColl_'
                                                            'DDD_DDTC_checkListBoxDistColl_LBT .dxeListBoxItemRow_Aqua')
            if len(all_coll) == 0:
                raise

            break
        except:
            logger.info('Failed. Will retry up to 5 times to get colleges --> ({})'.format(counter))
            driver.refresh()

    l = [option.text.strip() for option in all_coll]
    logger.info('colleges: ')
    logger.info(l)

    # select all
    college_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI0T1"
    wait.until(EC.presence_of_element_located((By.ID, college_id)))
    js_script = "document.getElementById('{}').click();".format(college_id)
    driver.execute_script(js_script)

    return l


def print_all_colleges_cohort(driver):

    wait = WebDriverWait(driver, 10)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxColl_B-1'))).click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
    time.sleep(3)
    all_coll = driver.find_elements_by_css_selector('#ASPxRoundPanel1_ASPxComboBoxColl_DDD_L_LBT .dxeListBoxItemRow_Aqua')

    l = {}
    logger.info('Total cohort colleges ({})'.format(len(all_coll)))
    for counter, coll in enumerate(all_coll):
        el_id = "ASPxRoundPanel1_ASPxComboBoxColl_DDD_L_LBI{}T0".format(counter)
        el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
        logger.info("no.--> ({}): --> {}".format(counter, el.text))
        l[el.text] = counter
    return l


def _get_checkboxes(driver):

    loctor = ".dxrpCW tr[style*='vertical-align'] input[type='checkbox']~label"
    all_ = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, loctor)))
    chcks = [chck.text.strip() for chck in all_]

    logger.info('Checkboxes: (Total: {})'.format(len(chcks)))
    logger.info(chcks)

    return chcks


def _write_to_excel(file_core, data):

    file_ = os.path.join(BASELINES, '{}.xlsx'.format(file_core))
    workbook = xlsxwriter.Workbook(file_)

    worksheet = workbook.add_worksheet(file_core + ' ' + time.strftime('%d%m%y', time.localtime()))

    # row, column
    # worksheet.write(0, 0, 'Hello')

    for col, colum_write in enumerate(data):
        for row, cell in enumerate(colum_write):
            worksheet.write(row, col, cell)

    workbook.close()

if __name__ == '__main__':
    verbose = None
    log_file = None
    wait_to_load = 3600
    retry = 3
    scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
    baseline_page = 'course success'

    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vc:lpsr:u:", ["verbose", 'log-file', "retry=", "url="])
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-l", "--log-file"):
            log_file = True
        elif opt in ("-r", "--retry"):
            retry = int(arg)
        elif opt in ("-u", "--url"):
            if arg == 'course success':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
                baseline_page = arg
            if arg == 'basic skills':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/BasicSkills_Cohort_Tracker.aspx'
                baseline_page = arg
            elif arg == 'transfer':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Transfer_Velocity.aspx'
                baseline_page = arg
            elif arg == 'retention success':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success_SP.aspx'
                baseline_page = arg
            elif arg == 'program awards':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Program_Awards.aspx'
                baseline_page = arg
                special_population_awards = None
            elif arg == 'program awards population':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Program_Awards_SP.aspx'
                baseline_page = arg
            elif arg == 'student success':
                scrape_url = 'http://datamart.cccco.edu/Services/Student_Success.aspx'
                baseline_page = arg
            elif arg == 'enrollment status':
                scrape_url = 'http://datamart.cccco.edu/Students/Enrollment_Status.aspx'
                baseline_page = arg

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

    # ---------------------------------------
    # course page
    # http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx
    # ---------------------------------------

    if baseline_page == 'course success':

        for retry_attempts in range(retry):
            try:
                driver = get_driver(scrape_url)
                driver.set_page_load_timeout(3600)

                baseline_course_success(driver)
                logger.info('Complete: {}'.format(baseline_page))
                result = 'Complete'
                break
            except TimeoutException:
                logger.warning('TimeoutException. Retry up to {} times'.format(retry))
                logger.debug('err: ', exc_info=True)
                result = 'TimeoutException ({})'.format(retry_attempts)
            except StaleElementReferenceException:
                logger.warning('StaleElementReferenceException. Retry up to {} times'.format(retry))
                logger.debug('err: ', exc_info=True)
                result = 'StaleElementReferenceException ({})'.format(retry_attempts)
            except UnexpectedAlertPresentException:
                logger.warning('UnexpectedAlertPresentException. Retry up to {} times'.format(retry))
                logger.debug('err: ', exc_info=True)
                result = 'UnexpectedAlertPresentException ({})'.format(retry_attempts)
            except:
                logger.warning('UndefinedException. Retry up to {} times'.format(retry))
                logger.debug('err: ', exc_info=True)
                result = 'UndefinedException ({})'.format(retry_attempts)
            finally:
                driver.close()
                driver.quit()
