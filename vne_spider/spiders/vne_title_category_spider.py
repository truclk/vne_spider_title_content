import re
from collections import defaultdict

import scrapy

CLEANER = re.compile(
    "[^A-Za-z0-9áàảãạăắằẳẫặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịúùủũụưứừửữựóòỏõọơớờởỡợôốồổỗộýỳỷỹỵđ ]+"
)


class VneTitleCategorySpider(scrapy.Spider):
    downloaded = 0
    visited = []
    visited_page_count = defaultdict(int)
    all_titles = []
    name = "vne_title_category_spider"
    allowed_domains = ["vnexpress.net"]

    custom_settings = {
        # "DOWNLOAD_DELAY": "0.0",
    }

    def start_requests(self):
        urls = [
            # "https://vnexpress.net/thoi-su",
            # "https://vnexpress.net/kinh-doanh",
            # "https://vnexpress.net/the-thao",
            # "https://vnexpress.net/the-gioi",
            # "https://vnexpress.net/giai-tri",
            # "https://vnexpress.net/phap-luat",
            "https://vnexpress.net/giao-duc",
            # "https://vnexpress.net/suc-khoe",
            "https://vnexpress.net/du-lich",
            # "https://vnexpress.net/khoa-hoc",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def clean_title(self, title):
        title = title.lower()
        title = re.sub(CLEANER, "", title)
        return title

    def parse(self, response):
        page = response.url.split("/")[-1].split("?")[0]
        if re.match(".+\-p[0-9]+$", page):
            page = re.sub("\-p[0-9]+$", "", page)
        filename = f"title_data/vne_title"
        file_object = open(filename, "a")
        page_titles = response.css(".item-news")
        with open(filename, "a") as file_object:
            for pg in page_titles:
                page_title = pg.css(".title-news a::attr(title)").get()
                page_content = pg.css(".description a::text").get()
                if not page_title or not page_content:
                    continue
                page_title = self.clean_title(page_title)
                page_content = self.clean_title(page_content)

                if page_title not in self.all_titles:
                    self.all_titles.append(page_title)
                    file_object.write(f"{page_title} {page_content},{page}\n")
        self.visited_page_count[page] += 1
        if self.visited_page_count[page] >= 100:
            return

        for next_page in response.css("#pagination a::attr(href)").getall():
            if next_page == "javascript:;":
                continue
            if next_page not in self.visited:
                self.visited.append(next_page)
                yield response.follow(next_page, self.parse)
        self.log(f"Saved file {filename}")
