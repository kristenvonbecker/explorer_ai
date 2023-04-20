import scrapy
# from scrapy.crawler import CrawlerProcess
#
# from scrapy.utils.project import get_project_settings
# settings = get_project_settings()


class ExhibitsSpider(scrapy.Spider):
    name = "exhibits"
    start_urls = ['https://www.exploratorium.edu/exhibits/all']

    def parse(self, response):
        exhibit_page_links = response.xpath('//div[@class="grid-70"]/h5/a/@href')
        yield from response.follow_all(exhibit_page_links, self.parse_exhibit)
        pagination_links = response.xpath('//li[@class="pager-next last"]/a/@href')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_exhibit(self, response):
        def extract(query):
            return response.xpath(query).get(default='').strip().replace(u'\xa0', u' ')

        def extracts(query):
            return response.xpath(query).getall()

        def extracts_join(query):
            extract_list = extracts(query)
            return ' '.join([item.strip().replace(u'\xa0', u' ') for item in extract_list])

        def extract_slugs(query):
            extract_list = extracts(query)
            return [item.split('/')[-1] for item in extract_list]

        yield {
            'id': response.url.split('/')[-1],
            'title': extract('//h1[@class="title"]/text()'),
            'aliases': extract('//span[text()="Aliases:"]/following-sibling::text()'),
            'location': extracts_join('//div[@class="where"]' +
                                      '/descendant-or-self::*/text()').partition(':')[2].strip(),
            'byline': extracts_join('//div[@class="byline"]' +
                                    '/descendant-or-self::*/text()').partition(':')[2].strip(),
            'collection_id': extract_slugs('//span[text()="Collections:"]/following-sibling::a/@href'),
            'related_id': extract_slugs('//h3[text()="Related exhibits"]/following-sibling::div/div/a/@href'),
            'tagline': extracts_join('//h2[@class="subtitle"]/descendant-or-self::*/text()'),
            'description': extracts_join('//div[@class="description"]/descendant-or-self::*/text()'),
            'whats_going_on': extracts_join('//div[@class="detail grid-parent"]' +
                                            '/h3[contains(text(),"going on")]' +
                                            '/following-sibling::div/p/descendant-or-self::*/text()'),
            'going_further': extracts_join('//div[@class="detail grid-parent"]' +
                                           '/h3[contains(text(),"Going further")]' +
                                           '/following-sibling::div/p/descendant-or-self::*/text()'),
            'details': extracts_join('//div[@class="detail grid-parent"]/h3[not(text())]' +
                                     '/following-sibling::div/p/descendant-or-self::*/text()'),
            'phenomena': extracts('//span[text()="Phenomena:"]/following-sibling::a/text()'),
            'keywords': extracts('//span[text()="Keywords:"]/following-sibling::a/text()'),
        }


# process = CrawlerProcess(settings)
# process.crawl(ExhibitsSpider)
# process.start()
