import re

import scrapy
from scrapy.utils.response import open_in_browser

from selenium_test import process_listing_fotocasa, get_max_page
from web_scrapper.items import PropertyItem
from scrapy_splash import SplashRequest




class FotocasaSpider(scrapy.Spider):
    name = 'fotocasa'
    allowed_domains = ['fotocasa.es']
    start_urls = ['https://www.fotocasa.es/es/alquiler/viviendas/barcelona-capital/todas-las-zonas/l/1']

    def start_requests(self):
        urls = process_listing_fotocasa(self.start_urls[0])
        max_page = get_max_page(self.start_urls[0])
        print('max page -> ' + max_page)
        for i in range(int(max_page)):
            for url in urls:
                yield SplashRequest(
                    url=url,
                    callback=self.parse_listing
                )
            urls = process_listing_fotocasa(self.get_next_url(i+1))
            print('URLS to process')
            print(urls)
        print("finish")

    def get_next_url(self, i):
        url = self.start_urls[0]
        substr = url[url.rfind('/'):]
        return url.replace(substr, '/'+str(i+1))


    def parse_listing(self, response):
        property = PropertyItem()
        # Property
        title = response.xpath("//*[@class='re-DetailHeader-propertyTitle']/text()").get()
        property["url"] = response.url
        property["title"] = title
        regex = re.search('en (.*)', title)
        if regex:
            property["location"] = regex.group(1)
        property["neigborhood"] = response.css('ol.re-Breadcrumb-links .re-Breadcrumb-text::text').get()
        property["body"] = "".join(response.css('.fc-DetailDescription::text').getall())
        types = response.xpath('//*[@class="re-DetailHeader-features"]//text()').getall()
        property["type"] = types[6] if 6 < len(types) else '' #safe access

        # Price
        property["current_price"] = response.xpath('//*[@class="re-DetailHeader-price"]/text()').re_first('(.+) €')
        property["last_price"] = response.xpath('//dd[@class="re-DetailRentReferenceIndex-detail"][3]//text()').re_first('(.+) €')
        property["area_market_price"] = response.xpath('//dd[@class="re-DetailRentReferenceIndex-detail"][2]//text()').re_first('(.+) €')
        property["square_meters"] = response.xpath('//*[@class="re-DetailHeader-features"][4]//text()').get()

        # Details
        property["tags"] = self.get_tags(response)
        property["bedrooms"] = response.xpath('//*[@class="re-DetailHeader-features"]//text()').getall()[0]
        property["bathrooms"] = response.xpath('//*[@class="re-DetailHeader-features"]//text()').getall()[2]
        consumption = self.get_consumption(response)
        emissions = self.get_emissions(response)
        property["certification_status"] = True if consumption and emissions else None
        property["consumption"] = consumption
        property["emissions"] = emissions

        # Multimedia
        property["main_image_url"] = response.css('.re-DetailMosaicPhotoWrapper-photo1 picture img::attr(src)').get()

        # Agents
        property["seller_name"] = response.xpath('//*[@class="re-ContactDetail-inmoContainer-clientName"]//text()').get()
        property["seller_logo"] = response.xpath('//*[@class="re-ContactDetail-inmoLogo"]//@src').get()
        property["ref_agent"] = response.xpath('//*[@class="re-ContactDetail-inmoContact"]//text()').re_first("Referencia: (.+)")
        property["phone_number"] = response.xpath('//*[@class="re-ContactDetail-phone"]//text()').get()

        yield property

    def get_tags(self, response):
        tags = ''
        top_tags_list = response.xpath('//*[@class="re-DetailFeaturesList-feature"]')  # upper tag block
        bottom_tags_list = response.xpath('//li[@class="re-DetailExtras-listItem"]/text()').getall()  # lower tag block

        for block in top_tags_list:
            label = block.css('::text').extract()[0]
            tag = block.css('::text').extract()[1]
            tags += "{}: {};".format(label, tag)

        bottom_tags = ';'.join(bottom_tags_list)
        tags += bottom_tags

        return tags

    def get_consumption(self, response):
        consumption = ''
        rating_list = response.css('.re-DetailEnergyCertificate-item::text').getall()
        units_list = response.css('.re-DetailEnergyCertificate-itemUnits::text').re('\w.+')
        if rating_list and units_list:
            consumption += "{};{} {}".format(rating_list[0], units_list[0], units_list[1])
            return consumption
        else:
            return None

    def get_emissions(self, response):
        emissions = ''
        rating_list = response.css('.re-DetailEnergyCertificate-item::text').getall()
        units_list = response.css('.re-DetailEnergyCertificate-itemUnits::text').re('\w.+')
        if len(units_list) > 2:  # checking if emission is included in list
            emissions += "{};{} {}".format(rating_list[1], units_list[2], units_list[3])
            return emissions
        else:
            return None



