import re

import scrapy
from scrapy.utils.response import open_in_browser

from web_scrapper.items import PropertyItem
from scrapy_splash import SplashRequest

script = """
function main(splash)
        local num_scrolls = 20
        local scroll_delay = 1

        local scroll_to = splash:jsfunc("window.scrollTo")
        local get_body_height = splash:jsfunc(
            "function() {return document.body.scrollHeight;}"
        )
        assert(splash:go(splash.args.url))
        splash:wait(splash.args.wait)

        for _ = 1, num_scrolls do
            local height = get_body_height()
            for i = 1, 10 do
                scroll_to(0, height * i/10)
                splash:wait(scroll_delay/10)
            end
        end        
        return splash:html()
end

"""



class FotocasaSpider(scrapy.Spider):
    name = 'fotocasa'
    allowed_domains = ['fotocasa.es']
    start_urls = ['https://www.fotocasa.es/es/alquiler/viviendas/barcelona-capital/todas-las-zonas/l']

    def start_requests(self):
        yield SplashRequest(url=self.start_urls[0], callback=self.parse, endpoint='execute', args={'wait': 2, 'lua_source': script})


    def parse(self, response):
        listings = response.xpath("//article[@class='re-CardPackPremium']/a[@class='re-CardPackPremium-carousel']/@href").getall()
        for listing_url in listings:
            yield SplashRequest(
                url=response.urljoin(listing_url),
                callback=self.parse_listing
            )
        print("Next page")
        next_page = response.xpath("//a[@class ='sui-AtomButton--empty']/@href").get()
        #if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), self.parse)
        #else:
        #    print("finish")

    def parse_listing(self, response):
        property = PropertyItem()
        # Property
        title = response.xpath("//*[@class='re-DetailHeader-propertyTitle']/text()").get()
        property["url"] = response.url
        property["title"] = title
        property["location"] = re.search('Piso de alquiler en (.*)', title).group(1)
        property["body"] = "".join(response.css('.fc-DetailDescription::text').getall())
        property["type"] = response.xpath('//*[@class="re-DetailHeader-features"]//text()').getall()[6]

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



