# Fotocasa Web Scrapper

A fotocasa Web Scrapper using Selenium and Scrappy with Splash.

## Install

- `pip install -r requirements.txt`
- Start Splash service using docker: `docker run --net="host" -p 8050:8050 scrapinghub/splash`


### Selenium

Selenium library requires a webdriver file, used for issuing commands to 
the host browser. I'm providing a google chrome 99.0 Win32 webdriver inside /drivers folder
- Chrome web driver: https://chromedriver.chromium.org/home

## How does it work?

The program entrypoint is located inside spiders/fotocasa.py. Using Selenium we navigate to the 
url indicated in start_urls array, it is expected to be a results search url, like: https://www.fotocasa.es/es/alquiler/viviendas/barcelona-capital/todas-las-zonas/l/1

Then, we navigate through the page, collecting all the advertisements urls, that will be scrapped using scrappy.

Finally, Selenium navigates to the next page, and the process is repeated, until no more pages are available.

## Run 

`scrapy crawl fotocasa -o output.json`
