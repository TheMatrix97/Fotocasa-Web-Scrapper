import scrapy


class FotocasaSpider(scrapy.Spider):
    name = 'fotocasa'
    allowed_domains = ['fotocasa.es']
    start_urls = ['https://www.fotocasa.es/']

    def parse(self, response):
        pass
