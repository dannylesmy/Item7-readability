# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

class ThetelegraphPipeline(object):
    def open_spider(self, spider):
        self.file = open(r'FILE.csv', 'w')
        self.file_writer = csv.writer(self.file)

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        row = ([item['date'], item["year"], item["title"], item["section"], item["url"], item["content"]])
        self.file_writer.writerow(row)

        return item

