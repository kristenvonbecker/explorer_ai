from exploratorium.items import ImageItem
import scrapy
import hashlib


def file_path(self, request, response=None, info=None, *, item=None):
    image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
    image_description = request.url.split('/')[-1].split('.jpg')[0]
    # replace spaces, etc. with hypthens
    # remove image size
    # split on "Photo courtesy of"
    image_filename = f'{image_url_hash}_{image_description}.jpg'
    return image_filename


class ImageSpider(scrapy.Spider):
    name = "imagespider"
    start_urls = ['https://www.exploratorium.edu/exhibits/all']

    def parse(self, response):
        for elem in response.xpath("//img"):
            img_url = elem.xpath("@src").extract_first()
            yield {'image_urls': [img_url]}
