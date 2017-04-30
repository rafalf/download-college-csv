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
import openpyxl

logger = logging.getLogger(os.path.basename(__file__))

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWN_PATH = os.path.join(FILE_DIR, 'download')

DOWNLOADED = 'CourseRetSuccessSumm.csv'
DOWNLOADED_XLSX = 'CourseRetSuccessSumm.xlsx'
DOWNLOADED_PARTIAL = 'CourseRetSuccessSumm.csv.crdownload'

DOWNLOADED_COHORT = 'BSkillsProgressTracker.csv'
DOWNLOADED_COHORT_PARTIAL = 'BSkillsProgressTracker.csv.crdownload'

DOWNLOADED_TRANSFER = 'TransferVelocity.csv'
DOWNLOADED_TRANSFER_PARTIAL = 'TransferVelocity.csv.crdownload'

LOGS = os.path.join(FILE_DIR, 'logs')
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
        prefs = {"download.default_directory": DOWN_PATH}
        chromeOptions.add_experimental_option("prefs", prefs)
        # chromeOptions.add_argument('headless')
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
    driver.maximize_window()

    driver.get(url)
    logger.info('Open url: {}'.format(url))
    return driver


def scrape(college, wait_to_load, screen_cap, driver, convert, search_type):

    wait = WebDriverWait(driver, 10)

    for counter in range(5):

        try:
            driver.refresh()

            select_search_type(search_type)

            # college
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))

            college_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
            wait.until(EC.presence_of_element_located((By.ID, college_id)))
            js_script = "document.getElementById('{}').click();".format(college_id)
            driver.execute_script(js_script)
            break
        except:
            logger.info('Failed. Retry up to 5 times to select the college --> ({})'.format(counter))

    el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
    el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
    logger.info("Selected college: ({}): {}".format(college, el.text))
    college_name = el.text

    down_college_specific = os.path.join(DOWN_PATH, college_name)
    if not os.path.isdir(down_college_specific):
        os.makedirs(down_college_specific)
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
    js_script = "document.getElementById('ASPxRoundPanel1_RunReportASPxButton_CD').click();"
    driver.execute_script(js_script)
    logger.info('View report clicked')

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click checkboxes
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_0'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_1'))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_TopOptions_2'))).click()
    logger.info('Checkboxes selected')

    # click update report
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport_CD'))).click()
    logger.info('Update selected')

    _wait_until_loaded(wait_to_load, driver)
    time.sleep(2)

    # click csv
    logger.info('About to click export to csv')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()
    logger.info('Export to csv clicked')

    if screen_cap:
        driver.save_screenshot(os.path.join(down_college_specific, college_name.lower() + ".png"))

    time.sleep(5)

    # click export as
    logger.info('click export to csv --> browser starts downloading')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')), message='element not clickable').click()

    _move_file(DOWN_PATH, down_college_specific)

    if convert:
        _convert_to_xlsx(os.path.join(down_college_specific, DOWNLOADED),
                         os.path.join(down_college_specific, DOWNLOADED_XLSX))

    return college_name


def scrape_cohort(college, screen_cap, driver, cohort_term, end_term, level, convert):

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
    level_scraped = []

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
                raise Exception('Skills equal 0')

            for counter in range(len(all_skills)):

                all = short_wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxBSSub_DDD_L_LBT .dxeListBoxItem_Aqua')))

                skill_name = all[counter].text
                file_part_skill = skill_name.strip()

                if file_part_skill == '':
                    raise Exception('Skill name not expanded')
                elif file_part_skill in skill_scraped:
                    logger.info('Skill already scraped: {}'.format(file_part_skill))
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
                    logger.info('Cohort level: {}'.format(file_part_level))

                    if file_part_level == '':
                        raise Exception('Cohort level not expanded')
                    elif file_part_skill + " " + file_part_level in level_scraped:
                        logger.info('Level already scraped: {}'.format(file_part_level))
                        logger.info(level_scraped)
                        continue

                    # cohort-level passed in
                    if level:
                        if file_part_level != level:
                            logger.info('Cohort level not matching: {} != {}'.format(level, cohort_level))
                            continue
                        else:
                            logger.info('Cohort level found match: {}'.format(level))

                    logger.info('Select cohort level: {}'.format(file_part_level))
                    all[counter_level].click()

                    # click view report
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_RunReportASPxButton'))).click()
                    logger.info('View report clicked')

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
                    logger.info('Update selected')

                    _wait_until_loaded(wait_to_load, driver)
                    time.sleep(2)

                    # click csv
                    logger.info('About to click export to csv')
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()
                    logger.info('Export to csv clicked')
                    time.sleep(2)

                    # click export as
                    logger.info('Click export to csv --> browser starts downloading')
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')),
                               message='element not clickable').click()

                    file_name = cohort_term + '-' + end_term + '-' + file_part_skill + "-" + file_part_level + '.csv'
                    _move_file_specific(DOWN_PATH, down_college_specific, file_name, DOWNLOADED_COHORT)

                    if convert:
                        file_name_xlsx = cohort_term + '-' + end_term + '-' + file_part_skill + "-" + file_part_level + '.xlsx'
                        _convert_to_xlsx(os.path.join(down_college_specific, file_name),
                                         os.path.join(down_college_specific, file_name_xlsx))

                    if screen_cap:
                        s = cohort_term + '-' + end_term + '-' + file_part_skill + "-" + file_part_level + '.png'
                        driver.save_screenshot(os.path.join(down_college_specific, s))

                    # append level scraped
                    level_scraped.append(file_part_skill + " " + file_part_level)
                    logger.info('Add scraped level: {}'.format(file_part_skill + " " + file_part_level))

                    # level - all
                    wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxPL_B-1'))).click()
                    time.sleep(2)

                # append skill scraped
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

        except UnexpectedAlertPresentException:
            logger.info('UnexpectedAlertPresentException: accepting alert')
            driver.switch_to.alert.accept()
            level_scraped.append(file_part_skill + " " + file_part_level)
            logger.info('Add scraped level: {}'.format(file_part_skill + " " + file_part_level))
            continue
        except:
            logger.info('Retry expand end term')

    else:
        logger.info('Failed skills and level 10 times')
        raise Exception('Failed skills and level 10 times')


def scrape_transfer(college, wait_to_load, screen_cap, driver, convert, search_type, cohort_year):

    wait = WebDriverWait(driver, 10)

    for counter in range(5):

        try:
            driver.refresh()

            select_search_type(search_type)

            # college
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))

            college_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
            wait.until(EC.presence_of_element_located((By.ID, college_id)))
            js_script = "document.getElementById('{}').click();".format(college_id)
            driver.execute_script(js_script)
            break
        except:
            logger.info('Failed. Retry up to 5 times to select the college --> ({})'.format(counter))

    el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(college)
    el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
    logger.info("Selected college: ({}): {}".format(college, el.text))
    college_name = el.text

    # create the transfer folder
    down_college_specific = os.path.join(DOWN_PATH, college_name, 'transfer')
    if not os.path.isdir(down_college_specific):
        os.makedirs(down_college_specific)
        logger.info("Created folder: {}".format(down_college_specific))

    # year
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditTerm_B-1'))).click()

    all_el = '#ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_LBT tr>td:nth-of-type(2)'
    all_ = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, all_el)))

    years_ = [e.text for e in all_]
    if cohort_year not in years_:
        logger.info("Cohort year not found: {}. No data available".format(cohort_year))
        logger.info("Available years:")
        logger.info(years_)
        raise ExitException('Cohort year not found')

    if cohort_year == 'Select All':
        coh_el = "ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_LBI0T1"
    else:
        coh_el = "ASPxRoundPanel1_ASPxDropDownEditTerm_DDD_DDTC_checkListBoxTerm_{}_D".format(cohort_year)

    js_script = "document.getElementById('{}').click();".format(coh_el)
    driver.execute_script(js_script)
    logger.info("Cohort year selected: {}".format(cohort_year))

    years_scraped = []

    for _ in range(10):

        try:
            # years to transfer
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxTW_B-1'))).click()
            time.sleep(2)
            all_years = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxTW_DDD_L_LBT .dxeListBoxItem_Aqua')))

            if len(all_years) == 0:
                logger.info('Years = 0. will retry')
                raise Exception(' Years equal 0')
            else:
                logger.info('Years = {}'.format(len(all_years)))

            for counter, year_ in enumerate(all_years):

                all = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxTW_DDD_L_LBT .dxeListBoxItem_Aqua')))

                year_name = all[counter].text
                file_part_year = year_name.strip()

                if file_part_year == '':
                    raise Exception('Year name not expanded')
                elif file_part_year in years_scraped:
                    logger.info('Year already scraped: {}'.format(file_part_year))
                    continue

                logger.info('Selecting year name: {}'.format(file_part_year))
                all[counter].click()

                # click view report
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_RunReportASPxButton_CD')))
                js_script = "document.getElementById('ASPxRoundPanel1_RunReportASPxButton_CD').click();"
                driver.execute_script(js_script)
                logger.info('View report clicked')

                _wait_until_loaded(wait_to_load, driver)
                time.sleep(2)

                # checkboxes
                if search_type == 'Collegewide Search':

                    checked = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_0')))

                    if not checked.is_selected():
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_0'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_2'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_3'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_4'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_0'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_1'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_2'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_3'))).click()
                        logger.info('Checkboxes selected')
                    else:
                        logger.info('Checkboxes already selected')

                elif search_type == 'Districtwide Search':

                    checked = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_1')))

                    if not checked.is_selected():
                        # click checkboxes
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_1'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_2'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_3'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_DCOptions_4'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_0'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_1'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_2'))).click()
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel3_SpecialOptions_3'))).click()
                        logger.info('Checkboxes selected')
                    else:
                        logger.info('Checkboxes already selected')

                # click update report
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#ASPxRoundPanel3_UpdateReport_CD'))).click()
                logger.info('Update selected')

                _wait_until_loaded(wait_to_load, driver)
                time.sleep(2)

                # click csv
                logger.info('About to click export to csv')
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#listExportFormat_1'))).click()
                logger.info('Export to csv clicked')

                # click export as
                logger.info('Click export to csv --> browser starts downloading')
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSaveAs_CD')),
                           message='element not clickable').click()

                # files
                # ----------------

                file_name = search_type + '-' + cohort_year + '-' + file_part_year + '.csv'
                _move_file_specific(DOWN_PATH, down_college_specific, file_name, DOWNLOADED_TRANSFER)

                if convert:
                    file_name_xlsx = search_type + '-' + cohort_year + '-' + file_part_year + '.xlsx'
                    _convert_to_xlsx(os.path.join(down_college_specific, file_name),
                                     os.path.join(down_college_specific, file_name_xlsx))

                if screen_cap:
                    s = search_type + '-' + cohort_year + '-' + file_part_year + '.png'
                    driver.save_screenshot(os.path.join(down_college_specific, s))

                # append year scraped
                years_scraped.append(file_part_year)
                logger.info('Year scraped level: {}'.format(file_part_year))

                # expand years
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxTW_B-1'))).click()
                time.sleep(2)

            return college_name

        except UnexpectedAlertPresentException:
            logger.info('UnexpectedAlertPresentException: accepting alert')
            driver.switch_to.alert.accept()
            years_scraped.append(file_part_year)
            logger.info('Add scraped year: {}'.format(file_part_year))
            continue
        except:
            logger.info('Retry expand years')

    else:
        logger.info('Failed years 10 times')
        raise Exception('Failed years 10 times')


def select_search_type(_search_type):

    wait = WebDriverWait(driver, 10)

    # state district college
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxComboBoxSDC'))).click()
    time.sleep(2)

    logger.info('Search type: {}'.format(_search_type))
    search = dict()
    search['Collegewide Search'] = 3
    search['Districtwide Search'] = 2
    search['Statewide Search'] = 1

    css_selector = '#ASPxRoundPanel1_ASPxComboBoxSDC_DDD_L_LBT tr:nth-of-type({})'.format(search[_search_type])
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()
    time.sleep(2)
    logger.info('Search type selected')


def print_all_colleges(driver, _search_type):

    wait = WebDriverWait(driver, 10)

    for counter in range(5):

        try:
            select_search_type(_search_type)

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ASPxRoundPanel1_ASPxDropDownEditDistColl'))).click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dxeListBoxItemRow_Aqua')))
            time.sleep(3)
            all_coll = driver.find_elements_by_css_selector('#ASPxRoundPanel1_ASPxDropDownEditDistColl_'
                                                            'DDD_DDTC_checkListBoxDistColl_LBT .dxeListBoxItemRow_Aqua')
            break
        except:
            logger.info('Failed. Will retry up to 5 times to get colleges --> ({})'.format(counter))
            driver.refresh()

    l = {}
    logger.info('Total colleges ({})'.format(len(all_coll)))
    for counter, coll in enumerate(all_coll):
        el_id = "ASPxRoundPanel1_ASPxDropDownEditDistColl_DDD_DDTC_checkListBoxDistColl_LBI{}T1".format(counter)
        el = wait.until(EC.presence_of_element_located((By.ID, el_id)))
        logger.info("no.--> ({}): --> {}".format(counter, el.text))
        if not el.text.count('Select All'):
            l[el.text] = counter
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


def _move_file(source, dest):

    logger.info('checking downloaded file')
    for _ in range(60):
        files_ = os.listdir(source)
        if DOWNLOADED in files_:
            sys.stdout.write('\n')
            sys.stdout.flush()
            logger.info('File downloaded: {}'.format(DOWNLOADED))
            break
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
    else:
        logger.warning("File not downloaded".format(DOWNLOADED))
        raise Exception('File not downloaded')

    try:
        copyfile(os.path.join(source, DOWNLOADED), os.path.join(dest, DOWNLOADED))
        logger.info('Copied as: {}'.format(os.path.join(dest, DOWNLOADED)))

        os.remove(os.path.join(source, DOWNLOADED))
        logger.info('Deleted: {}'.format(os.path.join(source, DOWNLOADED)))
    except:
        logger.warning("Failed to copy, delete file: {}".format(DOWNLOADED))
        raise Exception('Failed to copy, delete file')


def _move_file_specific(source, dest, file_name_dest, file_name_source):

    logger.info('Checking downloaded file')
    for _ in range(60):
        files_ = os.listdir(source)
        if file_name_source in files_:
            sys.stdout.write('\n')
            sys.stdout.flush()
            logger.info('File downloaded: {}'.format(file_name_source))
            break
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
    else:
        logger.warning("File not downloaded".format(file_name_source))
        raise Exception('File not downloaded')

    try:
        copyfile(os.path.join(source, file_name_source), os.path.join(dest, file_name_dest))
        logger.info('Copied as: {}'.format(os.path.join(dest, file_name_dest)))

        os.remove(os.path.join(source, file_name_source))
        logger.info('Deleted: {}'.format(os.path.join(source, file_name_source)))
    except:
        logger.warning("Failed to copy, delete file: {}".format(file_name_source))
        raise Exception('Failed to copy, delete file')


def _convert_to_xlsx(source, destination):

    try:
        wb = openpyxl.Workbook()
        ws = wb.active

        f = open(source)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
        f.close()

        wb.save(destination)
        logger.info('Created xlsx --> {}'.format(destination))
    except:
        logger.warning("Failed to convert source file: {}".format(source))
        raise Exception('Failed to convert')


def _wait_until_loaded(wait_, driver):

    try:
        for _ in range(10):

            try:
                els = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.ID, 'ASPxRoundPanel3_ASPxPivotGrid1_TL')))
                logger.info('Loading present:  count: {}'.format(len(els)))
                for el in els:
                    if el.is_displayed():
                        logger.info('Loading data displaying')
                        displaying = True
                        break
                else:
                    logger.info('Loading data not displaying yet')
                    displaying = False
                    time.sleep(0.3)

                if displaying:
                    break
            except StaleElementReferenceException:
                logger.info('StaleElementReferenceException: while loading data')
        else:
            logger.warning('Loading data element has not displayed')

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
            logger.warning('Loading data element still displays')
    except TimeoutException:
        logger.info('Loading data element not displaying')


def _write_row(row):
    with open(SCRAPE_LOG, 'a') as hlr:
        wrt = csv.writer(hlr, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        wrt.writerow(row)
        logger.info('Added to scraped.csv file: {}'.format(row))


def _clean_up():

    # -------------------------------------------------------
    # clean up
    # -------------------------------------------------------

    files = [DOWNLOADED, DOWNLOADED_PARTIAL, DOWNLOADED_COHORT, DOWNLOADED_COHORT_PARTIAL,
             DOWNLOADED_TRANSFER, DOWNLOADED_TRANSFER_PARTIAL]

    for clean_file in files:
        if os.path.isfile(os.path.join(DOWN_PATH, clean_file)):
            os.remove(os.path.join(DOWN_PATH, clean_file))
            logger.info('Deleted: {}'.format(clean_file))


if __name__ == '__main__':
    verbose = None
    log_file = None
    print_col = None
    screen_cap = None
    wait_to_load = 3600
    college = "all"
    scraped_college = 'Unknown'
    retry = 3
    scrape_url = 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx'
    scrape_page = 'course success'
    cohort_term = None
    end_term = None
    level = None
    convert = None
    search_type = 'Collegewide Search'
    available_searches = ['Collegewide Search', 'Statewide Search', 'Districtwide Search']
    cohort_year = 'Select All'

    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vc:lpsr:u:", ["verbose", "college=", 'log-file', 'print-college',
                                                    'screen-capture', "retry=", "url=", "cohort-term=", "end-term=",
                                                    'level=', 'convert', 'search-type=', "cohort-year="])
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-c", "--college"):
            college = arg
        elif opt in ("-l", "--log-file"):
            log_file = True
        elif opt in ("-p", "--print-college"):
            print_col = True
        elif opt in ("-s", "--screen-capture"):
            screen_cap = True
        elif opt in ("-r", "--retry"):
            retry = int(arg)
        elif opt in ("-u", "--url"):
            if arg == 'basic skills':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/BasicSkills_Cohort_Tracker.aspx'
                scrape_page = 'basic skills'
            elif arg == 'transfer':
                scrape_url = 'http://datamart.cccco.edu/Outcomes/Transfer_Velocity.aspx'
                scrape_page = 'transfer'
        elif opt in "--cohort-term":
            cohort_term = arg
        elif opt in "--end-term":
            end_term = arg
        elif opt in "--level":
            level = arg
        elif opt in "--convert":
            convert = True
        elif opt in "--search-type":
            search_type = arg
        elif opt in "--cohort-year":
            cohort_year = arg

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
    logger.info('DOWN_PATH: {}'.format(DOWN_PATH))
    logger.info('RETRY: {}'.format(retry))

    # ---------------------------------------
    # course page
    # 'http://datamart.cccco.edu/Outcomes/Course_Ret_Success.aspx
    # ---------------------------------------

    if scrape_page == 'course success':

        if search_type not in available_searches:
            logger.info('Search not found: {}. No data available.'.format(search_type))
            sys.exit(0)

        driver = get_driver(scrape_url)
        all_colleges = print_all_colleges(driver, search_type)
        driver.quit()
        if print_col:
            sys.exit(0)

        if college == "all":
            scr_ = [all_colleges[key] for key in all_colleges]
        else:
            try:
                scr_ = [all_colleges[college]]
            except KeyError:
                logger.info('College not found: {}. No data available.'.format(college))
                sys.exit(0)

        logger.info('Ids to scrape:')
        logger.info(scr_)

        for c in scr_:

            for retry_attempts in range(retry):
                try:
                    _clean_up()

                    driver = get_driver(scrape_url)
                    driver.set_page_load_timeout(3600)

                    scraped_college = scrape(c, wait_to_load, screen_cap, driver, convert, search_type)
                    logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
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
                    _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                    if retry_attempts == retry - 1:
                        _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), 'Failed', c, scraped_college])
                    driver.close()
                    driver.quit()

    # ---------------------------------------
    # cohort page
    # http://datamart.cccco.edu/Outcomes/BasicSkills_Cohort_Tracker.aspx
    # ---------------------------------------

    elif scrape_page == 'basic skills':

        driver = get_driver(scrape_url)
        all_colleges = print_all_colleges_cohort(driver)
        driver.quit()
        if print_col:
            sys.exit(0)

        if college == "all":
            scr_ = [all_colleges[key] for key in all_colleges]
        else:
            try:
                scr_ = [all_colleges[college]]
            except KeyError:
                logger.info('College not found: {}. No data available.'.format(college))
                sys.exit(0)

        logger.info('Ids to scrape:')
        logger.info(scr_)

        for c in scr_:
            for retry_attempts in range(retry):
                try:
                    _clean_up()

                    driver = get_driver(scrape_url)
                    driver.set_page_load_timeout(3600)

                    # -------------------------------------------------------
                    # scrape
                    # -------------------------------------------------------

                    scraped_college = scrape_cohort(c, screen_cap, driver, cohort_term, end_term, level, convert)
                    logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
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
                except ExitException:
                    logger.info('Data not available for specified college and cohort. Exit')
                    logger.debug('ExitException. Exit')
                    logger.debug('err: ', exc_info=True)
                    result = 'ExitException: Data not available'
                    sys.exit(0)
                except:
                    logger.warning('UndefinedException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UndefinedException ({})'.format(retry_attempts)
                finally:
                    _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                    if retry_attempts == retry - 1:
                        _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), 'Failed', c, scraped_college])
                    driver.close()
                    driver.quit()

    # ---------------------------------------
    # transfer page
    # http://datamart.cccco.edu/Outcomes/Transfer_Velocity.aspx
    # ---------------------------------------

    elif scrape_page == 'transfer':

        if search_type not in available_searches:
            logger.info('Search not found: {}. No data available.'.format(search_type))
            sys.exit(0)
        elif search_type == 'Statewide Search':
            logger.info('Search found but college not available this search type: {}. '
                        'No data available.'.format(search_type))
            sys.exit(0)

        driver = get_driver(scrape_url)
        all_colleges = print_all_colleges(driver, search_type)
        driver.quit()
        if print_col:
            sys.exit(0)

        if college == "all":
            scr_ = [all_colleges[key] for key in all_colleges]
        else:
            try:
                scr_ = [all_colleges[college]]
            except KeyError:
                logger.info('College not found: {}. No data available.'.format(college))
                sys.exit(0)

        logger.info('Ids to scrape:')
        logger.info(scr_)

        for c in scr_:

            for retry_attempts in range(retry):
                try:
                    _clean_up()

                    driver = get_driver(scrape_url)
                    driver.set_page_load_timeout(3600)

                    scraped_college = scrape_transfer(c, wait_to_load, screen_cap, driver, convert, search_type, cohort_year)
                    logger.info('Complete for college no.{} --> {}'.format(c, scraped_college))
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
                except ExitException:
                    logger.info('Data not available for specified college and cohort year. Exit')
                    logger.debug('ExitException. Exit')
                    logger.debug('err: ', exc_info=True)
                    result = 'ExitException: Data not available'
                    sys.exit(0)
                except:
                    logger.warning('UndefinedException. Retry up to {} times'.format(retry))
                    logger.debug('err: ', exc_info=True)
                    result = 'UndefinedException ({})'.format(retry_attempts)
                finally:
                    _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), result, c, scraped_college])
                    if retry_attempts == retry - 1:
                        _write_row([time.strftime('%H:%M %d-%m-%Y', time.localtime()), 'Failed', c, scraped_college])
                    driver.close()
                    driver.quit()
