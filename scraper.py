import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager as cdm
import requests
def download_cause_lists(state_name, district_name, complex_name, date_str):
    driver = None
    try:
        print("--- [Scraper] Starting Selenium ---")
        service = ChromeService(executable_path=cdm().install())
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # You can uncomment this to run without opening a browser window
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        driver.get(url)
        print(f"--- [Scraper] Navigated to: {url} ---")
        # state name
        try:
            print("--- [Scraper] Looking for state dropdown... ---")
            state_dropdown = wait.until(ec.presence_of_element_located((By.ID, "sess_state_code")))
            Select(state_dropdown).select_by_visible_text(state_name)
            print("--- [Scraper] State selected successfully. ---")
        except TimeoutException:
            print("!!! [Scraper] CRITICAL ERROR: Could not find the state dropdown after 20 seconds.")
            print("!!! The website might be down, slow, or its HTML may have changed.")
            return
        # If state and continue Select District
        wait.until(lambda d: len(Select(d.find_element(By.ID, "sess_dist_code")).options) > 1)
        district_dropdown = driver.find_element(By.ID, "sess_dist_code")
        Select(district_dropdown).select_by_visible_text(district_name)
        #Court Complex
        wait.until(lambda d: len(Select(d.find_element(By.ID, "court_complex_code")).options) > 1)
        complex_dropdown = driver.find_element(By.ID, "court_complex_code")
        Select(complex_dropdown).select_by_visible_text(complex_name)
        #date and submit
        date_input = driver.find_element(By.ID, "casedate")
        date_input.send_keys(date_str)
        driver.find_element(By.ID, "searchbtn").click()
        print(f"--- [Scraper] Submitted search for {date_str} ---")
        #find and download all pdf's
        wait.until(ec.presence_of_element_located((By.ID, "causelist_table")))
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
    except Exception as e:
        print(f"--- [Scraper] An error occurred: {e} ---")
    finally:
        if driver:
            driver.quit()
        print("--- [Scraper] Process finished. ---")