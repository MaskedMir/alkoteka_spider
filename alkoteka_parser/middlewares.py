import random
from scrapy import signals
from alkoteka_parser import settings

class ProxyMiddleware:
    def process_request(self, request, spider):
        if settings.PROXIES:
            request.meta['proxy'] = random.choice(settings.PROXIES)

class BaseMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")

class AlkotekaParserSpiderMiddleware(BaseMiddleware):
    pass

class AlkotekaParserDownloaderMiddleware(BaseMiddleware):
    pass
