import scrapy
from scrapy.http import HtmlResponse

from Demo.items import MovieItem


class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["movie.douban.com"]

    # start_urls = ["https://movie.douban.com/top250"]

    def start_requests(self):
        for page in range(10):
            yield scrapy.Request(f'https://movie.douban.com/top250?start={25 * page}&filter=')

    def parse(self, response: HtmlResponse, **kwargs):
        selector = scrapy.Selector(response)

        list_items = selector.css('div.article > ol > li')
        for list_item in list_items:
            movie_item = MovieItem()
            movie_item['title'] = list_item.css('span.title::text').extract_first()
            movie_item['rank'] = list_item.css('span.rating_num::text').extract_first()
            movie_item['subject'] = list_item.css('span.inq::text').extract_first() or ''
            detail_url = list_item.css('div.info > div.hd > a::attr(href)').extract_first()
            # yield movie_item
            yield scrapy.Request(
                url=detail_url, callback=parse_detail, cb_kwargs={'item': movie_item}
            )

        # hrefs_list = selector.css('div.paginator > a::attr(href)')
        # for href in hrefs_list:
        #     url = response.urljoin(href.extract())
        #     yield Request(url)


def parse_detail(response, **kwargs):
    selector = scrapy.Selector(response)

    movie_item = kwargs['item']
    movie_item['duration'] = selector.css('span[property="v:runtime"]::attr(content)').extract_first()
    movie_item['intro'] = selector.css('span[property="v:summary"]::text').extract_first() or ''
    yield movie_item
