# alkoteka_parser/settings.py
import scrapy_splash
from scrapy.settings.default_settings import SPIDER_MIDDLEWARES, DOWNLOADER_MIDDLEWARES

BOT_NAME = "alkoteka_parser"

SPIDER_MODULES = ["alkoteka_parser.spiders"]
NEWSPIDER_MODULE = "alkoteka_parser.spiders"

DOWNLOAD_DELAY = 0.5

# Включаем использование cookies для фиксации города
COOKIES_ENABLED = True

# Подставляем куки для региона "Краснодар"
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Cookie": "city_id=38; city_name=%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%BE%D0%B4%D0%B0%D1%80"
}


FEED_EXPORT_ENCODING = "utf-8"


FEEDS = {
    "result.json": {
        "format": "json",
        "overwrite": True
    }
}

# Попробовал сделать подключение через локальный сервер Docker

SPLASH_URL = 'http://localhost:8050'

DOWNLOADER_MIDDLEWARES.update({
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
})


SPIDER_MIDDLEWARES.update({
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
})

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'


SPLASH_DISABLE_X_DOMAINS = True
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
SPLASH_COOKIES_DEBUG = True
DOWNLOAD_TIMEOUT = 90
SPLASH_SLOT_POLICY = scrapy_splash.SlotPolicy.PER_DOMAIN
