# eCourts Cause List Scraper
 * Project Documentation \
 October 18, 2025\
 This application automates downloading judicial cause lists from the official Indian
 eCourts portal. A user can specify a state, district, court complex, and date through a
 simple webinterface, and theapplication will download all available cause list PDFs for
 that day.\
## 1 HowItWorks
 * This project uses Selenium to control a live web browser because the eCourts website is
 dynamic. Content on the site is loaded with JavaScript after user interactions (like select
ing a state), which a standard library like requests cannot handle. Selenium mimics a
 humanuser,allowingit to wait for elements toload, select from dropdowns, andtypeinto
 forms. \
### Key Automation Techniques Used
 • WebDriverWait: Makes the script wait patiently for page elements to appear, pre
venting crashes on slow-loading pages.
 • Dynamic Content Waiting: A custom lambda function is used to wait until drop
downs are populated with options (e.g., waiting for districts to load after a state is
 selected). This is a highly reliable method.
 • XPathSearching: AspecificXPathquery(//table[@id='causelist_table']//a[contains(@href,
 '.pdf')]) is used toprecisely locate and extract all PDF download links from the re
sults table.
 ## 2 QuickStartGuide
 #### 2.1 Prerequisites
 • Python 3.6+
 • Google Chrome browser
 #### 2.2 Setup&Installation
 ##### 1. Organize Files: Your project folder must be structured as follows:
 1
/ecourts_scraper \
 |-- app.py \
 |-- scraper.py\
 |-- README.md \
 |-- /templates \
 |-------- index.html \
 ##### 2. Install Libraries: Open a terminal in your project folder and run:
 * pip install Flask selenium webdriver-manager requests
 ###### Note: webdriver-manager automatically handles the chromedriver setup.
 #### 2.3 RunningtheApplication
 1. In your terminal, navigate to the project folder.
 2. Run the Flask app:\
          python app.py
 4. Openyour webbrowser and go to http://127.0.0.1:5000.   (use this link or open the flask app in 5000 port only)
 ## 3 UsageInstructions
 ### 1. Fill out the form in your browser.
 #### CRITICAL: 
 * TheState, District, and Court Complex names mustbeanexact, case
sensitive match to the names on the eCourts website.
 ### 2. Click the ”Start Download” button.
 ### 3. Aconfirmationmessagewill appear onthepage. Thedownloadwillrunintheback
ground. You can monitor its live progress in your terminal. A new Chrome window
 will open and close on its own; this is normal. \
 #### 3.1 WherearetheFiles Saved?
 Downloaded PDFsaresaved in anewfolder inside your project directory, named with the
 pattern: Causelists_[District Name]_[Date]. \
 Example: Causelists_New_Delhi_18-10-2025
