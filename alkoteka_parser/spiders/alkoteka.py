import scrapy
import time
from urllib.parse import urljoin

class AlkotekaSpider(scrapy.Spider):
    name = "alkoteka"
    allowed_domains = ["alkoteka.com"]

    def start_requests(self):
        # Подгружаем стартовые урлы
        with open("start_urls.txt", "r", encoding="utf-8") as f:
            start_urls = [url.strip() for url in f if url.strip()]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Ловим все ссылки на продукты на странице
        product_links = response.css("div.product-card a::attr(href)").getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

        # И не забываем про пагинацию
        next_page = response.css('a.pagination__link[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        timestamp = int(time.time())
        title = response.css("h1.product-card-top__title::text").get(default="").strip()

        marketing_tags = response.css(".product-card-top__label::text").getall()
        section = response.css(".breadcrumbs__item a span::text").getall()

        images = response.css(".product-card-gallery__picture img::attr(src)").getall()
        images = [urljoin(response.url, img) for img in images] if images else []
        main_image = images[0] if images else ""

        price_current = self.extract_price(response.css(".product-price .price::text").get())
        price_original = self.extract_price(response.css(".product-price .price-old::text").get()) or price_current

        sale_tag = ""
        if price_original > price_current:
            discount = int(round(100 - (price_current / price_original * 100)))
            sale_tag = f"Скидка {discount}%"

        stock_text = response.css(".product-card-top__availability span::text").get(default="")
        in_stock = "Нет в наличии" not in stock_text

        # Собираем метаданные по кусочкам
        metadata = {}
        for row in response.css(".product-specifications__item"):
            key = row.css(".product-specifications__name::text").get()
            value = row.css(".product-specifications__value::text").get()
            if key and value:
                metadata[key.strip()] = value.strip()

        description = response.css(".product-description__content::text").get(default="").strip()

        yield {
            "timestamp": timestamp,
            "RPC": metadata.get("\u041a\u043e\u0434 \u0442\u043e\u0432\u0430\u0440\u0430", ""),
            "url": response.url,
            "title": self.compose_title(title, metadata),
            "marketing_tags": marketing_tags,
            "brand": metadata.get("\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c", ""),
            "section": section,
            "price_data": {
                "current": price_current,
                "original": price_original,
                "sale_tag": sale_tag
            },
            "stock": {
                "in_stock": in_stock,
                "count": 0  # Количество не парсим, оставляем нолик
            },
            "assets": {
                "main_image": main_image,
                "set_images": images,
                "view360": [],
                "video": []
            },
            "metadata": {"__description": description, **metadata},
            "variants": self.count_variants(metadata)
        }

    def extract_price(self, price_str):
        if price_str:
            # Чистим цену от мусора
            return float(price_str.replace(" ", "").replace(",", "."))
        return 0.0

    def compose_title(self, title, metadata):
        # Склеиваем тайтл с нужными допами, если есть
        addition = []
        for key in ("\u0426\u0432\u0435\u0442", "\u041e\u0431\u044a\u0435\u043c"):
            value = metadata.get(key)
            if value:
                addition.append(value)
        return f"{title}, {', '.join(addition)}" if addition else title

    def count_variants(self, metadata):
        # Если есть разные цвета или объемы — считаем как вариант
        return sum(1 for key in ("\u0426\u0432\u0435\u0442", "\u041e\u0431\u044a\u0435\u043c") if metadata.get(key))
