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
from shutil import copyfile
import csv

logger = logging.getLogger(os.path.basename(__file__))

DOWNLOADED = 'CourseRetSuccessSumm.csv'
DOWNLOADED_PARTIAL = 'CourseRetSuccessSumm.csv.crdownload'
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWN_PATH = os.path.join(FILE_DIR, 'download')

DOWNLOADED_COHORT = 'BSkillsProgressTracker.csv'
DOWNLOADED_COHORT_PARTIAL = 'BSkillsProgressTracker.csv.crdownload'


class ExitException(Exception):
    pass


def get_driver(url):

    # driver
    if platform.system() == 'Darwin':
        driver = webdriver.Chrome()
    else:
        driver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": DOWN_PATH}
        prefs["credentials_enable_service"] = False
        prefs["password_manager_enabled"] = False
        chromeOptions.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
    driver.maximize_window()

    driver.get(url)
    logger.info('url opened : {}'.format(url))
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
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_RunReportASPxButton_CD')))
    js_script = "document.getElementById('ASPxRoundPanel1_RunReportASPxButton_CD').click();".format(type_id)
    driver.execute_script(js_script)
    logger.info('view report clicked')

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click checkboxes
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_0'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_1'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_2'))).click()
    logger.info('Checkboxes selected')

    # click update report
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport_CD'))).click()
    logger.info('update selected')

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click csv
    logger.info('About to click export to csv')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()
    logger.info('export to csv clicked')

    if screen_cap:
        driver.save_screenshot(os.path.join(down_college_specific, college_name.lower() + ".png"))

    time.sleep(5)

    # click export as
    logger.info('click export to csv --> browser starts downloading')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')), message='element not clickable').click()

    _move_file(DOWN_PATH, down_college_specific)

    return college_name


def scrape_cohort(college, screen_cap, driver, cohort_term, end_term):

    wait = WebDriverWait(driver, 10)
    short_wait = WebDriverWait(driver, 3)

    for counter in range(10):

        try:
            driver.refresh()

            # college
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxColl_B-1'))).click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
            time.sleep(2)

            college_id = "ASPxRoundPanel1_ASPxComboBoxColl_DDD_L_LBI{}T0".format(college)
            el = wait.until(EC.presence_of_element_located((By.ID, college_id)))
            college_name = el.text
            el.click()
            time.sleep(2)
            logger.info("Selected college: ({}): {}".format(college, college_name))

            # cohort term
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSTerm_B-1'))).click()
            time.sleep(2)
            all_cohorts = short_wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSTerm_DDD_L_LBT .dxeListBoxItem_Aqua')))

            logger.info('----------')
            logger.info('Search cohort terms:')
            for cohort in all_cohorts:
                cohort_term_option = cohort.text
                if cohort_term_option == cohort_term:
                    logger.info('Found match: {}'.format(cohort_term_option))
                    sel_id = cohort.get_attribute('id')
                    logger.debug('Selector: {}'.format(sel_id))

                    wait.until(EC.element_to_be_clickable((By.ID, sel_id))).click()
                    logger.info('Cohort term selected: {}'.format(cohort_term_option))
                    break
                elif cohort_term_option == '':
                    raise Exception('Cohort term not expanded')
                else:
                    logger.info('Option: {} not matching'.format(cohort_term_option))
            else:
                logger.info('EXIT: --> Match for: {} not found'.format(cohort_term))
                logger.info('----------')
                raise ExitException('Match not found')

            logger.info('----------')
            break
        except ExitException:
            raise ExitException('Match not found')
        except:
            logger.info('Failed cohort term. Will retry up to 10 times. --> ({})'.format(counter))

    else:
        logger.info('Failed cohort term 10 times')
        raise Exception('Failed cohort term 10 times')
    # ----------------------------------------------------
    # end term
    # ----------------------------------------------------
    for _ in range(10):

        try:
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxETerm #ASPxRoundPanel1_ASPxComboBoxETerm_B-1'))).click()
            time.sleep(2)
            all_end_terms = short_wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxETerm_DDD_L_LBT .dxeListBoxItem_Aqua')))

            logger.info('----------')
            logger.info('End terms:')
            for end in all_end_terms:
                end_option = end.text
                if end_option == end_term:
                    logger.info('Found match: {}'.format(end_option))
                    sel_id = end.get_attribute('id')
                    logger.debug('Selector: {}'.format(sel_id))

                    wait.until(EC.element_to_be_clickable((By.ID, sel_id))).click()
                    logger.info('End term selected: {}'.format(end_option))
                    break
                elif end_option == '':
                    raise Exception('End term not expanded')
                else:
                    logger.info('Option: {} not matching'.format(end_option))
            else:
                logger.info('EXIT: --> Match for: {} not found'.format(cohort_term))
                logger.info('----------')
                raise ExitException('Match not found')

            logger.info('----------')
            break
        except ExitException:
            raise ExitException('Match not found')
        except:
            logger.info('Retry expand end term')

    else:
        logger.info('Failed end term 10 times')
        raise Exception('Failed end term 10 times')

    # ----------------------------------------------------
    # Create folder
    # ----------------------------------------------------

    down_college_specific = os.path.join(DOWN_PATH, college_name, 'cohort')
    if not os.path.isdir(down_college_specific):
        os.makedirs(down_college_specific)
        logger.info("Created folder: {}".format(down_college_specific))

    # ----------------------------------------------------
    # Basic skills
    # ----------------------------------------------------

    skill_scraped = []

    for _ in range(10):

        try:

            # expand skills
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxBSSub_ET #ASPxRoundPanel1_ASPxComboBoxBSSub_B-1'))).click()
            time.sleep(2)
            all_skills = short_wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxBSSub_DDD_L_LBT .dxeListBoxItem_Aqua')))

            if len(all_skills) == 0:
                logger.info('Skills = 0. will retry')

            for counter in range(len(all_skills)):

                all = short_wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxBSSub_DDD_L_LBT .dxeListBoxItem_Aqua')))

                skill_name = all[counter].text
                file_part_skill = skill_name.strip()

                if file_part_skill == '':
                    raise Exception('Skill name not expanded')
                elif file_part_skill in skill_scraped:
                    logger.info('skill already scraped: {}'.format(file_part_skill))
                    continue

                logger.info('Selecting skill: {}'.format(file_part_skill))
                all[counter].click()

                # ----------------------------------------------------
                # Starting cohort level
                # ----------------------------------------------------

                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxPL_B-1'))).click()
                time.sleep(2)

                all_starting = short_wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxPL_DDD_L_LBT .dxeListBoxItem_Aqua')))

                for counter_level in range(len(all_starting)):
                    all = short_wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxPL_DDD_L_LBT .dxeListBoxItem_Aqua')))

                    cohort_level = all[counter_level].text
                    file_part_level = cohort_level.strip()

                    if file_part_skill == '':
                        raise Exception('Cohort level not expanded')

                    logger.info('Selecting cohort level: {}'.format(file_part_level))
                    all[counter_level].click()

                    # click view report
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_RunReportASPxButton'))).click()
                    logger.info('view report clicked')

                    _wait_until_loaded(wait_to_load, driver)
                    time.sleep(2)

                    checked = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_0')))
                    if not checked.is_selected():
                        # click checkboxes
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_0'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_1'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_2'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_3'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_4'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DemoOptions_5'))).click()

                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_FinAidOptions_0'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_FinAidOptions_1'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_FinAidOptions_2'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_FinAidOptions_3'))).click()
                        short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_FinAidOptions_4'))).click()
                        logger.info('Checkboxes selected')
                    else:
                        logger.info('Checkboxes already selected')

                    # click update report
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport'))).click()
                    logger.info('update selected')

                    _wait_until_loaded(wait_to_load, driver)
                    time.sleep(2)

                    # click csv
                    logger.info('About to click export to csv')
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()
                    logger.info('export to csv clicked')
                    time.sleep(2)

                    # click export as
                    logger.info('click export to csv --> browser starts downloading')
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')),
                               message='element not clickable').click()

                    file_name = file_part_skill + "-" + file_part_level + '.csv'
                    _move_file_cohort(DOWN_PATH, down_college_specific, file_name)

                    if screen_cap:
                        s = file_part_skill + "-" + file_part_level + '.png'
                        driver.save_screenshot(os.path.join(down_college_specific, s))

                    # level - all
                    wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxPL_B-1'))).click()
                    time.sleep(2)

                skill_scraped.append(file_part_skill)
                logger.info('DONE: added {} to skill scraped'.format(file_part_skill))

                if len(skill_scraped) == len(all_skills):
                    logger.info('SUCCESS: all skills scraped:')
                    logger.info(skill_scraped)
                    return college_name

                # basic skills - all
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxBSSub_B-1'))).click()
                time.sleep(2)

        except:
            logger.info('Retry expand end term')

    else:
        logger.info('Failed skills and level 10 times')
        raise Exception('Failed skills and level 10 times')


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


def print_all_colleges_cohort(driver):

    wait = WebDriverWait(driver, 10)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxColl_B-1'))).click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
    time.sleep(3)
    all_coll = driver.find_elements_by_css_selector('#ASPxRoundPanel1_ASPxComboBoxColl_DDD_L_LBT .dxeListBoxItemRow_Aqua')

    l = []
    logger.info('Total cohort colleges ({})'.format(len(all_coll)))
    for counter, coll in enumerate(all_coll):
        el_id = "ASPxRoundPanel1_ASPxComboBoxColl_DDD_L_LBI{}T0".format(counter)
        el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
        logger.info("no.--> ({}): --> {}".format(counter, el.text))
        l.append(counter)
    return l


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


def _move_file_cohort(source, dest, file_name):

    logger.info('checking downloaded file')
    for _ in range(60):
        files_ = os.listdir(source)
        if DOWNLOADED_COHORT in files_:
            sys.stdout.write('\n')
            sys.stdout.flush()
            logger.info('file downloaded: {}'.format(DOWNLOADED_COHORT))
            break
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
    else:
        logger.warning("file not downloaded".format(DOWNLOADED_COHORT))
        raise Exception('file not downloaded')

    try:
        copyfile(os.path.join(source, DOWNLOADED_COHORT), os.path.join(dest, file_name))
        logger.info('copied as: {}'.format(os.path.join(dest, file_name)))

        os.remove(os.path.join(source, DOWNLOADED_COHORT))
        logger.info('deleted: {}'.format(os.path.join(source, DOWNLOADED_COHORT)))
    except:
        logger.warning("failed to copy, delete file: {}".format(DOWNLOADED_COHORT))
        raise Exception('failed to copy, delete file')


def _wait_until_loaded(wait_, driver):

    try:
        for _ in range(10):

            try:
                els = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.ID, 'ASPxRoundPanel3_ASPxPivotGrid1_TL')))
                logger.info('_wait_until_loaded: loading present:  count: {}'.format(len(els)))
                for el in els:
                    if el.is_displayed():
                        logger.info('loading data displaying')
                        displaying = True
                        break
                else:
                    logger.info('loading data not displaying yet')
                    displaying = False
                    time.sleep(0.3)

                if displaying:
                    break
            except StaleElementReferenceException:
                logger.info('_wait_until_loaded: StaleElementReferenceException')
        else:
            logger.warning('loading data element has not displayed')

        for _ in range(wait_):
            els = driver.find_elements_by_id('ASPxRoundPanel3_ASPxPivotGrid1_TL')

            counter_displaying = 0
            for counter, el in enumerate(els):
                if not el.is_displayed():
                    logger.info('({}) not displaying --> loaded'.format(counter))
                    counter_displaying += 1
                else:
                    logger.info('({}) displaying'.format(counter))
                    time.sleep(0.5)
            if counter_displaying == len(els):
                return
        else:
            logger.warning('loading data element still displays')
    except TimeoutException:
        logger.info('loading data element not displaying')


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
    scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
    scrape_page = 'course'
    cohort_term = None
    end_term = None

    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vc:lpsr:u:", ["verbose", "college=", 'log-file', 'print-college',
                                                  'screen-capture', "retry=", "url=", "cohort-term=", "end-term="])
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
            retry = int(arg)
        elif opt in ("-u", "--url"):
            if arg  == 'cohort':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/BasicSkills_Cohort_Tracker.aspx'
                scrape_page = 'cohort'
        elif opt in ("--cohort-term"):
            cohort_term = arg
        elif opt in ("--end-term"):
            end_term = arg

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
    logger.info('RETRY: {}'.format(retry))
    logger.info('SCRAPE_URL: {}'.format(scrape_url))

    # ---------------------------------------
    # course page
    # ---------------------------------------

    if scrape_page == 'course':

        if college == 'all' or print_col:
            driver = get_driver(scrape_url)
            college = print_all_colleges(driver)
            driver.quit()
            if print_col:
                sys.exit(0)

        for c in college:
            for _ in range(retry):
                try:
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED))
                        logger.info('Deleted: {}'.format(DOWNLOADED))
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED_PARTIAL)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED_PARTIAL))
                        logger.info('Deleted: {}'.format(DOWNLOADED_PARTIAL))

                    driver = get_driver(scrape_url)
                    driver.set_page_load_timeout(3600)

                    scraped_college = scrape(c, wait_to_load, screen_cap, driver)
                    logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
                    result = 'Complete'
                    break
                except TimeoutException:
                    logger.warning('TimeoutException. Will retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'TimeoutException'
                except StaleElementReferenceException:
                    logger.warning('StaleElementReferenceException. Will retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'StaleElementReferenceException'
                except UnexpectedAlertPresentException:
                    logger.warning('UnexpectedAlertPresentException. Will retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UnexpectedAlertPresentException'
                except:
                    logger.warning('UndefinedException. Will retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UndefinedException'
                finally:
                    _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                    driver.close()
                    driver.quit()

    # ---------------------------------------
    # cohort page
    # ---------------------------------------

    elif scrape_page == 'cohort':

        if college == 'all' or print_col:
            driver = get_driver(scrape_url)
            college = print_all_colleges_cohort(driver)
            driver.quit()
            if print_col:
                sys.exit(0)

        for c in college:
            for _ in range(retry):
                try:
                    # -------------------------------------------------------
                    # clean up
                    # -------------------------------------------------------
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED))
                        logger.info('Deleted: {}'.format(DOWNLOADED))
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED_PARTIAL)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED_PARTIAL))
                        logger.info('Deleted: {}'.format(DOWNLOADED_PARTIAL))
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED_COHORT)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED_COHORT))
                        logger.info('Deleted: {}'.format(DOWNLOADED_COHORT))
                    if os.path.isfile(os.path.join(DOWN_PATH, DOWNLOADED_COHORT_PARTIAL)):
                        os.remove(os.path.join(DOWN_PATH, DOWNLOADED_COHORT_PARTIAL))
                        logger.info('Deleted: {}'.format(DOWNLOADED_COHORT_PARTIAL))

                    driver = get_driver(scrape_url)
                    driver.set_page_load_timeout(3600)

                    # -------------------------------------------------------
                    # scrape
                    # -------------------------------------------------------

                    scraped_college = scrape_cohort(c, screen_cap, driver, cohort_term, end_term)
                    logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
                    result = 'Complete'
                    break
                except TimeoutException:
                    logger.warning('TimeoutException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'TimeoutException'
                except StaleElementReferenceException:
                    logger.warning('StaleElementReferenceException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'StaleElementReferenceException'
                except UnexpectedAlertPresentException:
                    logger.warning('UnexpectedAlertPresentException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UnexpectedAlertPresentException'
                except ExitException:
                    logger.info('Data not available for specified college and cohort. Exit')
                    logger.debug('ExitException. Exit')
                    logger.debug('err: ', exc_info=True)
                    result = 'ExitException: Data not available'
                    sys.exit(0)
                except:
                    logger.warning('UndefinedException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UndefinedException'
                finally:
                    _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                    driver.close()
                    driver.quit()