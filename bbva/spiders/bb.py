import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bbva.items import Article


class BbSpider(scrapy.Spider):
    name = 'bb'
    start_urls = ['https://www.bbva.com/en/latest-news/']

    def parse(self, response):
        categories = response.xpath('//ul[@class="tagsLinks"]/li/a/@href').getall()
        yield from response.follow_all(categories, self.parse_category)

    def parse_category(self, response):
        links = response.xpath('//h2[@class="notTitulo"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="article-title"]/text()').get()
        if title:
            title = title.strip()

        date = " ".join(response.xpath('//span[@class="date"]/text()').get().split()[-3:])
        if date:
            date = datetime.strptime(date.strip(), '%d %b %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="detContText"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        category = response.xpath('//div[@class="detAreaDate rs_skip"]/a/text()').get()
        author = response.xpath('//div[@class="dataAuthor"]//span/text()').get()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)
        item.add_value('category', category)

        return item.load_item()
