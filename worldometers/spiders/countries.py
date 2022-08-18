import logging
from urllib.request import Request
import scrapy


class CountriesSpider(scrapy.Spider):
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']

    def parse(self, response):
        # title = response.xpath("//h1/text()").get()
        # countries = response.xpath("//td/a/text()").getall()
        # yield {
        #     "title" : title,
        #     "countries": countries
        # }

        countries = response.xpath("//td/a")
        for country in countries:
            name = country.xpath(".//text()").get()
            link = country.xpath(".//@href").get()
            
            ### REQUEST further to crawl data in each country link ###
            
            ### METHOD 1 ### --> WORKED
            # yield {
            #     'country_name': name,
            #     'country_link': link
            # }

            
            ### Debug:  
            # ERROR 1: Missing scheme in request url: --> use absolute_url, By default the link could be http:// or https:// --> let try both
            # ERROR 2: Filtered offsite request to 'worldometers.info' -> remove "/" in alowed_domain

            ### METHOD 2 ### --> NOT WORK
            # absolute_url = f"https://worldometers.info{link}" 
            # yield scrapy.Request(url = absolute_url)

            ### METHOD 3 ### --> WORKED
            # absolute_url = response.urljoin(link) 
            # yield scrapy.Request(url = absolute_url)

            ### METHOD 4 ### --> WORKED
            # yield response.follow(url=link)

            ### STORE DATA after request for each country link - Use callback function ###
            yield response.follow(url=link, callback = self.parse_country, meta={"country_name" : name}) # meta used to sync variable between 2 parse functions
            # If we not used meta method, use global country_name variable can return only one country name.
    def parse_country(self, response): # Response if get from above for loop in countries objects
        # logging.info(response.url)
        name = response.request.meta['country_name'] # "name" in above function pass to this "name" by meta method and middleware "country_name"
        rows = response.xpath("(//table[@class='table table-striped table-bordered table-hover table-condensed table-list'])[1]/tbody/tr")
        for row in rows:
            year = row.xpath(".//td[1]/text()").get()
            population = row.xpath("./td[2]/strong/text()").get()
            yield {
                "country_name": name,
                "year" : year,
                "population": population
            }