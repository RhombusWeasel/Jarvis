import requests, re, os, sys
from readability import Document
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import logger

log = logger.Logger('webtools', log_level=logger.Logger.INFO)

# Set the path to the WebDriver executable (change this to the path on your system)
chrome_driver_path = "/path/to/chromedriver"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--enable-features=ReaderMode")
chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})
#chrome_options.add_argument("--user-data-dir=C:/Users/peter/AppData/Local/Google/Chrome/User Data/Profile {#}/")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

path = 'file:///C:/Users/peter/PycharmProjects/Jarvis/'
current_page = f'{path}/home.html'

# Create a new instance of the Chrome WebDriver
browser = webdriver.Chrome(
  chrome_options=chrome_options
)
# Open the first website
browser.get(current_page)

def new_tab(site):
  global browser, current_page
  log.info(f"Opening new tab: {site}")
  # Open a new tab
  browser.execute_script(f"window.open('{site}');")
  # Switch to the new tab
  browser.switch_to.window(browser.window_handles[-1])
  current_page = get_text_from_url(site)


def google_it(query):
  new_tab('https://www.google.com')
  log.info(f"Searching Google for: {query}")
  # Find the search box element by its name attribute
  search_box = browser.find_element(By.NAME, "q")
  # Type a query and submit it
  search_box.send_keys(Keys.SHIFT + Keys.HOME)
  search_box.send_keys(Keys.BACKSPACE)
  search_box.send_keys(query)
  search_box.send_keys(Keys.RETURN)


def get_text_from_url(url):
  log.info(f"Getting text from: {url}")
  r = requests.get(url)
  doc = Document(r.text)
  text = doc.summary()
  return re.sub('<[^>]*>', ' ', text)


def open_code_editor(data):
    log.info(f"Opening code editor for: {data['language']}")
    global browser, path
    mode = {
        "python": "ace/mode/python",
        "javascript": "ace/mode/javascript",
        "java": "ace/mode/java",
        "csharp": "ace/mode/csharp",
        "lua": "ace/mode/lua",
        "ruby": "ace/mode/ruby"
    }.get(data['language'].lower(), "ace/mode/plain_text")
    new_tab("http://localhost:8000")

    # Wait for the Ace Editor to be initialized
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "editor")))

    # Set the content of the editor
    browser.execute_script(f"editor.session.setMode(arguments[0]); console.log('mode set to ' + arguments[0]);", mode)
    browser.execute_script(f"editor.setValue(arguments[0]); console.log('code set to ' + arguments[0]);", data['code'])


requested_files = []
def read_file(name):
  log.info(f"Reading file: {name}")
  try:
    global requested_files, nu_prompt, prompt
    if not name in requested_files:
        path = '../files/'
        with open(path + name, 'r') as f:
          data = f.read()
        f.close()
        log.json(data)
        requested_files.append(name)
        return data
  except:
    return False