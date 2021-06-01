import re

import scrapy


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


class VneSpider(scrapy.Spider):
    downloaded = 0
    visited = []
    name = "vne_english_spider"
    allowed_domains = ["e.vnexpress.net"]

    custom_settings = {
        "DOWNLOAD_DELAY": "0.5",
    }

    def start_requests(self):
        urls = [
            "https://e.vnexpress.net/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-1].split("?")[0]
        filename = f"data_english/vne-{page}"
        if page.endswith(".html"):
            self.downloaded += 1
            with open(filename, "w") as f:
                for content in response.css("p.Normal").getall():
                    f.write(cleanhtml(content))
        if self.downloaded >= 500:
            return
        for next_page in response.xpath(".//a/@href"):
            next_url = next_page.extract()
            if self.downloaded >= 500:
                return
            if next_url not in self.visited and (
                next_url.startswith("https://e.vnexpress.net/")
                or next_url.startswith("/")
            ):
                self.visited.append(next_url)
                yield response.follow(next_url, self.parse)
        self.log(f"Saved file {filename}")
