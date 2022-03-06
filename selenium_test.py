from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DRIVER_PATH = "C:/Users/Roger/Downloads/chromedriver_win32(1)/chromedriver.exe"
options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")

def _extract_href(item):
    return item.get_attribute('href')

def process_listing_fotocasa(url):
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(url)
    sleep(2)
    js = "const fun = async function scrollToAll(){ do{ var elements = document.getElementsByClassName('re-CardPackPremiumPlaceholder'); for (const index in elements){ const item = elements[index]; console.log(elements); if (item != null && item instanceof HTMLElement){ console.log(item); item.scrollIntoView(); await new Promise(r => setTimeout(r, 1000)); } } }while(elements.length > 0); }; fun().then(function(){alert('done')});"
    driver.execute_script(js)
    WebDriverWait(driver, 30).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
    # Get all links to listings
    elements = driver.find_elements(By.XPATH, '//article[contains(@class, "re-CardPackPremium") or contains(@class, "re-CardPackAdvance") or contains(@class, "re-CardPackMinimal")]/a')
    href_list = list(map(_extract_href, elements))
    driver.quit()
    return href_list

def get_max_page(url): #Requires running process_listing_fotocasa(url) before
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(url)
    max_page = None
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight-4000)")
    sleep(1)
    element = driver.find_elements(By.CSS_SELECTOR, '.re-Pagination a.sui-LinkBasic span.sui-AtomButton-inner')[4]
    if element:
        max_page = element.text
    driver.quit()
    return max_page

