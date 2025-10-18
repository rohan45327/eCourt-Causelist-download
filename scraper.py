import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
import requests

def download_cause_lists(state_name, district_name, complex_name, date_str):
    driver = None
    try:
        print("--- [Scraper] Starting Selenium ---")
        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") # Run in the background without a visible browser window
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        driver.get(url)
        print(f"--- [Scraper] Navigated to: {url} ---")

        popup_wait = WebDriverWait(driver, 5)
        try:
            close_button = popup_wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='disp_none']/button[2]")))
            close_button.click()
            print("--- [Scraper] Disclaimer pop-up found and closed. ---")
        except TimeoutException:
            print("--- [Scraper] No pop-up found, continuing script. ---")

        try:
            print("--- [Scraper] Looking for state dropdown... ---")
            state_dropdown = wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
            Select(state_dropdown).select_by_visible_text(state_name)
            print("--- [Scraper] State selected successfully. ---")
        except TimeoutException:
            print("!!! [Scraper] CRITICAL ERROR: Could not find the state dropdown after 20 seconds.")
            return

        wait.until(lambda d: len(Select(d.find_element(By.ID, "sess_dist_code")).options) > 1)
        district_dropdown = driver.find_element(By.ID, "sess_dist_code")
        Select(district_dropdown).select_by_visible_text(district_name)
        print("--- [Scraper] District selected successfully. ---")

        wait.until(lambda d: len(Select(d.find_element(By.ID, "court_complex_code")).options) > 1)
        complex_dropdown = driver.find_element(By.ID, "court_complex_code")
        Select(complex_dropdown).select_by_visible_text(complex_name)
        print("--- [Scraper] Court complex selected successfully. ---")
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"--- [Scraper] Found and accepted an alert: {alert.text} ---")
            alert.accept()
            print("--- [Scraper] Alert accepted. Re-verifying page stability... ---")
            wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
            print("--- [Scraper] Page is stable. Proceeding. ---")
        except TimeoutException:
            print("--- [Scraper] No validation alert found, continuing. ---")
        print("--- [Scraper] Waiting for date input to be ready... ---")
        date_input = wait.until(EC.presence_of_element_located((By.ID, "casedate")))
        date_input.send_keys(date_str)
        
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "searchbtn")))
        search_button.click()
        print(f"--- [Scraper] Submitted search for {date_str} ---")

        wait.until(EC.presence_of_element_located((By.ID, "causelist_table")))
        pdf_links = driver.find_elements(By.XPATH, "//table[@id='causelist_table']//a[contains(@href, '.pdf')]")
        
        if not pdf_links:
            print("--- [Scraper] No PDFs found. ---")
            return

        download_dir = f"Causelists_{district_name.replace(' ', '_')}_{date_str}"
        os.makedirs(download_dir, exist_ok=True)
        print(f"--- [Scraper] Saving files to: {download_dir} ---")
        
        for link in pdf_links:
            pdf_url = link.get_attribute('href')
            court_name = link.find_element(By.XPATH, "./ancestor::tr/td[2]").text.strip().replace('/', '_').replace('\\', '_')
            filename = f"{court_name}.pdf"
            filepath = os.path.join(download_dir, filename)
            pdf_response = requests.get(pdf_url)
            
            if pdf_response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"--- [Scraper] Downloaded {filename} ---")
            else:
                print(f"--- [Scraper] Failed to download {filename}. Status code: {pdf_response.status_code} ---")

    except Exception as e:
        print(f"--- [Scraper] An error occurred: {e} ---")
    finally:
        if driver:
            driver.quit()
        print("--- [Scraper] Process finished. ---")

