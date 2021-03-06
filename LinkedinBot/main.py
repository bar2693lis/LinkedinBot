from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import json
import time
import re

class EasyApplyLinkedin:

    def __init__(self,data):

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome(data['driver_path'])

    def login_linkedin(self):

        self.driver.get("https://www.linkedin.com/")

        login_email = self.driver.find_element_by_name("session_key")
        login_email.clear()
        login_email.send_keys(self.email)

        login_password = self.driver.find_element_by_name("session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)

    def job_search(self):

        jobs_link = self.driver.find_element_by_link_text('Jobs')
        jobs_link.click()
        time.sleep(2)

        search_keyword = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-keyword')]")
        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        
        search_location = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-location')]")
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        easy_apply_button = self.driver.find_element_by_xpath("//button[@class='artdeco-pill artdeco-pill--slate artdeco-pill--2 artdeco-pill--choice ember-view search-reusables__filter-pill-button' and text()='Easy Apply']")
        easy_apply_button.click()
        time.sleep(1)

    def find_offers(self):

        total_results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(str(total_results_int)+' results found for you')
        time.sleep(2)
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
        
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name("disabled.ember-view.job-card-container__link.job-card-list__title")
            
            for title in titles:
                self.submit_application(title)

        if total_results_int > 24:
            time.sleep(2)
            find_pages = self.driver.find_elements_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.click()
            time.sleep(5)
            last_page = self.driver.current_url
            time.sleep(5)
            total_jobs = int(last_page.split('start=',1)[1])

            for page_number in range(25,total_jobs+25,25):
                print("Next Page, Page number "+str((page_number/25)+1))
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
                
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name("disabled.ember-view.job-card-container__link.job-card-list__title")
                    
                    for title_ext in titles_ext:
                        self.submit_application(title_ext)
        
        else:
            print('Closed because there are less than 25 jobs')
            self.close_sesion()

    def submit_application(self,job_ad):

        print('You are applying to the position of: ', job_ad.text)
        job_ad.click()
        time.sleep(2)

        try:
            in_apply = self.driver.find_element_by_xpath("//button[@data-control-name='jobdetails_topcard_inapply']")
            in_apply.click()
        
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        
        time.sleep(1)

        try:
            submit = self.driver.find_element_by_xpath("//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
            time.sleep(5)

        except NoSuchElementException:
            
            try:
                print('Not direct application, going to next...')
                discard = self.driver.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            
            except NoSuchElementException:
                pass
        
        time.sleep(1)

    def close_sesion(self):

        print('End of the session, see you later')
        self.driver.close()

    def apply(self):

        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(5)
        self.find_offers()
        time.sleep(5)
        self.close_sesion()

if __name__ == "__main__": # This line checks if the program ran directly & checks if the system variable __name__ accepts the value __main__
    
    with open('config.json') as config_file:
        data = json.load(config_file)
    
    bot = EasyApplyLinkedin(data)
    bot.apply()