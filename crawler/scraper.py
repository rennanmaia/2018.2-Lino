import scrapy
import pdfx
import json
from tabula import convert_into
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

DOWNLOAD_PATH = './downloads/'
OUTPUT_PATH = './outputs/'

class TheCrawler():
    def __init__(self):
        self.process = CrawlerProcess(get_project_settings())

    def runCrawler(self):
        self.process.crawl('RU')
        self.process.start()  # the script will block here until the crawling is finished

class JsonReader():
    def __init__(self):
        with open('result.json') as f:
            self.body = json.load(f)

class PdfReader():
    def __init__(self):
        self.data = JsonReader()
    
    def downloadMenu(self, campus):
        data = self.data
        n = 0
        for item in data.body:
            if campus in item['text']:
                pdf = pdfx.PDFx(item['url'])
                pdf.download_pdfs(DOWNLOAD_PATH)
                name = campus + str(n)
                n += 1
                fileName = item['url'].split('/')
                fileName = fileName.pop()
                convert_into(
                    f'{DOWNLOAD_PATH}{fileName}',
                    f'{OUTPUT_PATH}{name}.tsv',
                    output_format='tsv')

crawl = TheCrawler()
crawl.runCrawler()
p = PdfReader()
p.downloadMenu('FGA')
