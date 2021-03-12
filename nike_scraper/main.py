from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import time
import sys
import resource
import schedule
import math
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from selenium.webdriver.common.keys import Keys

from pyvirtualdisplay import Display

resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)


display = Display(visible=0, size=(1366, 768))
logging.basicConfig(filename='nike-app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

sched = BlockingScheduler()
display.start()


def nike_func():
    print("Main Function Executed")

    with open('config.json', "r") as f:
        data = json.load(f)

    cvv = data['cvv']

    shoe_number = data['shoe_number']

    execution_time = data['execution_time']

    options = Options()

    fire_profile = webdriver.FirefoxProfile()
    fire_profile.set_preference("browser.cache.disk.enable", False)
    fire_profile.set_preference("browser.cache.memory.enable", False)
    fire_profile.set_preference("browser.cache.offline.enable", False)
    fire_profile.set_preference("network.http.use-cache", False)
    options.headless = True

    LA = timezone('America/Los_Angeles')
    california_time = datetime.now(LA)

    logging.warning(
        f"Scrapper started of URL => {data['url']} at TIME UTC => {datetime.now()} and California Time => {california_time}")
    counter = 1

    driver = webdriver.Firefox(
        options=options, firefox_profile=fire_profile)
    driver.get(data['url'])

    geo_location = None
    try:
        element_present = EC.presence_of_element_located(
            (By.ID, 'hf-geoselection-title'))
        geo_location = WebDriverWait(driver, 10).until(element_present)

        if geo_location:
            geo_button = driver.find_element_by_css_selector(
                "button.hf-modal-btn-close")
            geo_button.click()
    except:
        pass

    notify_btn = None
    add_to_cart = None
    try:
        notify_btn = driver.find_element_by_xpath(
            '//button[text()="Notify Me"]')
    except Exception as e:
        print("Notify Me Button Not Found")
    try:
        add_to_cart = driver.find_element_by_xpath(
            '//button[@data-qa="feed-buy-cta"]')
    except Exception as e:
        print("Add to Bag Button Not Found")

    if notify_btn or not add_to_cart:
        print("Not released yet")
        driver.quit()
        print("Waiting for 5 seconds")
        time.sleep(5)
        counter += 1
        print("Re executing main function")
        nike_func()
    else:
        print("Shoes Available, Going for Purchase")
        try:
            driver.get('https://www.nike.com/login')

            element_present = EC.visibility_of_element_located(
                (By.XPATH, '//input[@name="emailAddress"]'))
            email_element = WebDriverWait(driver, 20).until(element_present)

            email_element.send_keys(data['email'])

            password_element = driver.find_element_by_xpath(
                '//input[@name="password"]')
            password_element.send_keys(data['password'])

            sign_in_btn = driver.find_element_by_xpath(
                '//input[@value="SIGN IN"]')
            sign_in_btn.click()

            driver.execute_script("window.open('about:blank', 'tab2');")
            driver.switch_to.window("tab2")

            driver.get(data['url'])

            geo_location = None
            try:
                element_present = EC.presence_of_element_located(
                    (By.ID, 'hf-geoselection-title'))
                geo_location = WebDriverWait(driver, 10).until(element_present)

                if geo_location:
                    geo_button = driver.find_element_by_css_selector(
                        "button.hf-modal-btn-close")
                    geo_button.click()
            except:
                pass

        except Exception as e:
            driver.quit()
            logging.warning(f"URL => {data['url']}")
            logging.error(str(e))
            nike_func()

        logging.warning(
            f"Shoes Available, Going for Purchase URL => {data['url']}")
        try:

            try:
                element_present = EC.presence_of_element_located(
                    (By.ID, 'hf-geoselection-title'))
                geo_location = WebDriverWait(driver, 2).until(element_present)

                if geo_location:
                    geo_button = driver.find_element_by_css_selector(
                        "button.hf-modal-btn-close")
                    geo_button.click()
            except:
                pass

            shoe_size_presence_check = EC.presence_of_element_located(
                (By.XPATH, '//*[text()="Muhammad Raza"]'))

            WebDriverWait(driver, 30).until(shoe_size_presence_check)

            time.sleep(3)
            shoe_size_presence_check = EC.presence_of_element_located(
                (By.XPATH, '//li[@data-qa="size-available"]/button'))

            WebDriverWait(driver, 10).until(shoe_size_presence_check)

            driver.execute_script("arguments[0].scrollIntoView();", driver.find_element_by_xpath(
                '//li[@data-qa="size-available"]/button'))

            elems = driver.find_elements_by_xpath(
                '//li[@data-qa="size-available"]/button')

            shoe_size_selected = False
            for button in elems:
                if str(data['shoe_number']) in button.text:
                    shoe_size_selected = True
                    print("size found")
                    logging.warning(
                        f"Shoes Size Found! of URL => {data['url']}")
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", button)
                    button.click()
                    break

                else:
                    elems[0].click()

        except:
            print("shoe size not available")
            logging.error(f"Shoes Size NOT Found :( of URL => {data['url']}")

        try:

            time.sleep(5)
            element_present = EC.presence_of_element_located(
                (By.XPATH, '//button[@data-qa="feed-buy-cta"]'))

            elem_present = WebDriverWait(driver, 15).until(element_present)

            driver.execute_script(
                "arguments[0].scrollIntoView();", driver.find_element_by_xpath('//button[@data-qa="feed-buy-cta"]'))

            time.sleep(2)
            add_to_cart = driver.find_element_by_xpath(
                '//button[@data-qa="feed-buy-cta"]').click()
        except Exception as e:
            driver.quit()
            nike_func()

        # checkout_btn = driver.find_element_by_xpath('//button[text()="Checkout"]')
        try:
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, '//iframe[@title="creditCardIframeForm"]')))

           time.sleep(2)
           cvInput = driver.find_element_by_id('cvNumber')

            cvInput.send_keys(cvv)

            driver.switch_to.default_content()

            if data['purchase']:

                try:
                    time.sleep(2)

                    driver.execute_script(
                        "arguments[0].scrollIntoView();", driver.find_element_by_xpath('//div[@data-qa="payment-section"]//button[@data-qa="save-button"]'))

                    element_present = EC.visibility_of_element_located(
                        (By.XPATH, '//div[@data-qa="payment-section"]//button[@data-qa="save-button"]'))
                    present_element = WebDriverWait(
                        driver, 10).until(element_present)
                except:
                    pass
                time.sleep(4)
                driver.find_element_by_xpath(
                    '//div[@data-qa="payment-section"]//button[@data-qa="save-button"]').click()

                element_present = EC.visibility_of_element_located(
                    (By.XPATH, '//div[@data-qa="checkout-summary-section"]//button[@data-qa="save-button"]'))
                present_element = WebDriverWait(
                    driver, 10).until(element_present)

                driver.find_element_by_xpath(
                    '//div[@data-qa="checkout-summary-section"]//button[@data-qa="save-button"]').click()

                try:
                    time.sleep(3)
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", driver.find_element_by_xpath(
                            '//div[@data-qa="checkout-summary-section"]//button[@data-qa="save-button"]'))

                    driver.find_element_by_xpath(
                        '//div[@data-qa="checkout-summary-section"]//button[@data-qa="save-button"]').click()

                except:
                    pass

                logging.warning(
                    f"Congratualions!! Shoe purchased succesfully {data['url']}")

                time.sleep(3)

                driver.save_screenshot("image.png")

                time.sleep(3)

                driver.save_screenshot("image2.png")

                time.sleep(3)

                driver.save_screenshot("image3.png")

                driver.quit()
                display.stop()
            else:
                logging.warning(
                    f"Congratualions!! Shoe purchased succesfully {data['url']}")
                driver.quit()
                display.stop()

        except Exception as e:
            check = True
            try:
                elem = None
                elem = driver.find_element_by_xpath(
                    '//*[text()="[ Code: ABB4C446 ]"]')
                print(
                    "Sorry, you have reached the quantity limit in your cart. Please remove an item and try again. ")
                logging.error(
                    f"Sorry, you have reached the quantity limit in your cart. Please remove an item and try again :( of URL => {data['url']}")
                check = None
                driver.quit()
                display.stop()

            except Exception as e:
                print(e)
                driver.quit()
                nike_func()

            # if check:
            #     print(e)


with open('config.json', "r") as f:
    data = json.load(f)

# execution_time = data['execution_time']

# schedule.every().day.at(execution_time).do(nike_func)
# print('Script scheduled at ', execution_time)
# while True:
#     schedule.run_pending()
#     time.sleep(1)

# nike_func()
cron_str = '45 14 {} {} *'.format(data['execution_day'],data['execution_month'])
sched.add_job(nike_func, CronTrigger.from_crontab(cron_str))
print(f"Scheduled for {data['url']}")
sched.start()
