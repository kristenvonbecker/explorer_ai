from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class TextPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if spider.name == 'exhibits':
            if adapter.get('title'):
                if adapter.get('id') in ['es', 'zht', 'fil']:
                    raise DropItem(f'Non-English language in {item}')
            else:
                raise DropItem(f"Missing title in {item}")
            return item
        elif spider.name == 'galleries':
            if adapter.get('title'):
                del adapter['curator_url']
                return item
            else:
                raise DropItem(f"Missing title in {item}")
