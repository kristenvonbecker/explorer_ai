import scrapy
# from scrapy.crawler import CrawlerProcess

# from scrapy.utils.project import get_project_settings
# settings = get_project_settings()


def extract(query, response):
    return response.xpath(query).get(default='').replace(u'\xa0', u' ').strip()


def extracts(query, response):
    return [item.replace(u'\xa0', u' ').strip() for item in response.xpath(query).getall()]


def extracts_merge(query, response):
    return ' '.join(extracts(query, response))


class GalleriesSpider(scrapy.Spider):
    name = "galleries"
    start_urls = ['https://www.exploratorium.edu/visit/galleries']

    def parse(self, response):
        galleries_page_links = response.xpath('//h2[text()="Museum Galleries"]/following-sibling::div//h5/a/@href')
        yield from response.follow_all(galleries_page_links, self.parse_gallery)

    def parse_gallery(self, response):
        kwargs = {
          'id': response.url.split('/')[-1],
          'title': extract('//div[@id="main-content"]//h1/text()', response),
          'tagline': extract('//div[@id="main-content"]//h3/text()', response),
          'description': extract('//div[@id="main-content"]//h3/following-sibling::p/text()', response),
          'curator_url': extract('//div[@id="main-content"]//p/a/@href', response),
        }
        url = response.urljoin(kwargs['curator_url'])
        yield scrapy.Request(url, self.parse_curator, cb_kwargs=kwargs)

    def parse_curator(self, response, **kwargs):
        kwargs['curator_statement'] = extracts_merge('//div[@id="main-content"]' +
                                                     '//div[@class="field-items"]//p//text()', response)
        yield kwargs


# process = CrawlerProcess(settings)
# process.crawl(GalleriesSpider)
# process.start()
