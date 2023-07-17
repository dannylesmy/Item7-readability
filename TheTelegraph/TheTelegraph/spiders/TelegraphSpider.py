# Not working anymore. 
# The newspaper change its policy and now one need to pay for downloading the archive (2022)


import scrapy, string, re
from TheTelegraph.items import ThetelegraphItem


class TelegraphSpider(scrapy.Spider):
    name = "TelegraphSpider"
    #allowed_domains = ["www.telegraph.co.uk"]
    start_urls = ["http://www.telegraph.co.uk/archive/"]

    def parse(self, response):
        urls = response.xpath('//div[@class="summary"]//h3/a/@href').extract()
        fullurl = map(response.urljoin, urls)
        for url in fullurl:
            yield scrapy.Request(url=url, callback=self.parse_year)

    def parse_year(self, response):
        urls = response.xpath('//div[@class="summary"]//h3/a/@href').extract()
        fullurl = map(response.urljoin, urls)
        for url in fullurl:
            yield scrapy.Request(url=url, callback=self.parse_month)

    def parse_month(self, response):
        urls = response.xpath('//div[@class="summary"]//h3/a/@href').extract()
        fullurl = map(response.urljoin, urls)
        for url in fullurl:
            yield scrapy.Request(url=url, callback=self.parse_day)

    def parse_day(self, response):
        urls = response.xpath('//div[@class="summary"]//h3/a/@href').extract()
        fullurl = map(response.urljoin, urls)
        for url in fullurl:
            if "culturepicturegalleries" not in url:
                yield scrapy.Request(url=url, callback=self.parse_content)

    def parse_content(self, response):
        if not ("promotions" in response.url or "galleries" in response.url):
            content = response.xpath('//div[@itemprop="articleBody"]//div[@class]/p[not(strong)]/text()').extract()
            content = " ".join(content).encode('ascii', 'replace').strip().translate(string.maketrans("\n\t\r", "   "))
            if (len(content.split()) > 30):
                title = response.xpath('//meta[@name="title"]/@content').extract()
                url = response.url
                section = response.xpath('//meta[@name="keywords"]/@content').extract_first().split()[-1]
                if response.xpath('//meta[@itemprop="datePublished"]/@content').extract():
                    date = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
                else:
                    date = response.xpath('//p[@class="publishedDate"]/text()').extract_first()
                year = re.search("(\d{4})", date).group(1)
                yield ThetelegraphItem(content = content, section = section, date = date, year = year, title = title,
                                                                                           url = url)

