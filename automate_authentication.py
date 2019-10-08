import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
import xlsxwriter 
  
workbook = xlsxwriter.Workbook('records.xlsx') 
  
worksheet = workbook.add_worksheet() 

worksheet.write(0, 0, "Company")
worksheet.write(0, 1, "First Name")
worksheet.write(0, 2, "Last Name")
worksheet.write(0, 3, "Job Position")
worksheet.write(0, 4, "Email")
    
chrome_options = Options()
chrome_options.add_argument("--headless") 

url = "https://account.ycombinator.com/?continue=https%3A%2F%2Fwww.startupschool.org%2Fusers%2Fsign_in"

driver = webdriver.Chrome('./chromedriver', options=chrome_options)

driver.get(url)

email_input = driver.find_element_by_id('ycid-input')
password_input = driver.find_element_by_id('password-input')

email_input.send_keys('')
password_input.send_keys('')

driver.find_element_by_xpath('//*[@type="submit"]').click()

time.sleep(3)

driver.get("https://www.startupschool.org/directory")

last_height = driver.execute_script("return document.body.scrollHeight")

while True:

    # Scroll down to the bottom.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    main_html = driver.page_source
    main_soup = BeautifulSoup(main_html, features="lxml")
    content = main_soup.findAll("div", {"class": "directory-company-profile"})
    try:

        for i, a in enumerate(content):
            try:
                company_tag = a.find("a", {"class": "company-name"})
                company = company_tag.text
                link = "https://www.startupschool.org/" + company_tag["href"]

                # <----------------Email Part--------------------->

                driver.execute_script("window.open('');")
                time.sleep(3)

                # Switch to the new window
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)

                html = driver.page_source
                soup = BeautifulSoup(html, features="lxml")

                
                for bb in soup.findAll("div", {"class": "founder-name"}):
                    anchor = bb.find('a')
                    if anchor:
                        email = anchor['href']
                        email = email[7:]
                    else:
                        email = None

                time.sleep(3)

                # close the active tab
                driver.close()
                time.sleep(3)

                # Switch to the original window
                driver.switch_to.window(driver.window_handles[0])

                # <----------------Email Part--------------------->
                
                dd = a.find("a", {"class": "founder"})
                full_name = dd.find("div", {"class": "name"}).text.split()
                first_name = full_name[0]
                last_name = full_name[1]
                job_position = dd.find("div", {"class": "expertise"}).text

               
                print(company, first_name, last_name, job_position, email)

                worksheet.write(i+1, 0, company)
                worksheet.write(i+1, 1, first_name)
                worksheet.write(i+1, 2, last_name)
                worksheet.write(i+1, 3, job_position)
                worksheet.write(i+1, 4, email)
            
            except Exception:
                print("Skipping this record due to error.")
                continue
           
    except Exception:
        print("Error has been reported.")
        workbook.close()
        break
    
    # Wait to load the page.
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:

        break

    last_height = new_height



