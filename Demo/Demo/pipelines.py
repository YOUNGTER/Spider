# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import openpyxl
import pymysql


class MysqlPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        host = crawler.settings['HOST']
        port = crawler.settings['PORT']
        user = crawler.settings['USER']
        password = crawler.settings['PASSWORD']
        database = crawler.settings['DATABASE']
        charset = crawler.settings['CHARSET']
        s = cls(host, port, user, password, database, charset)
        return s

    def __init__(self, host, port, user, password, database, charset):
        self.conn = pymysql.connect(host=host, port=port, user=user,
                                    password=password, database=database, charset=charset)
        self.cursor = self.conn.cursor()
        self.data = list()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        if len(self.data) > 0:
            self.executemany()
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        self.data.append(dict_to_tuple(item))
        if len(self.data) == 128:
            self.executemany()
        return item

    def executemany(self):
        self.cursor.executemany(
            'INSERT INTO movie (title, ranking, inq, duration, intro) VALUES (%s, %s, %s, %s, %s)',
            self.data
        )
        self.data.clear()


class ExcelPipeline:
    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = 'Top250'
        self.worksheet.append(('title', 'rank', 'subject', 'duration', 'intro'))

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.workbook.save('movie.xlsx')

    def process_item(self, item, spider):
        self.worksheet.append(dict_to_tuple(item))
        return item


def dict_to_tuple(item):
    title = item.get('title', '')
    rank = item.get('rank', '')
    subject = item.get('subject', '')
    duration = item.get('duration', '')
    intro = item.get('intro', '')
    return title, rank, subject, duration, intro
