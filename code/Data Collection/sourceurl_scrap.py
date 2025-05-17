import scrapy
from scrapy.selector import Selector
from google import search
import traceback
import requests
import os
import sqlite3
try:
    from urlparse import urlparse  # Python2
except ImportError:
    from urllib.parse import urlparse  # Python3
    
try:
    from urlparse import urljoin  # Python2
except ImportError:
    from urllib.parse import urljoin  # Python3

class SourceUrlSpider(scrapy.Spider):
    name = "sourceurl"

    def start_requests(self):
        
        url = 'https://www.allsides.com/bias/bias-ratings?field_news_source_type_tid=2&field_news_bias_nid=1&field_featured_bias_rating_value=All&title=&page=2'
        
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        size = len(response.css('td.views-field-title a::text').extract())
        print(size)
        count = 0
        for i in range(0,size):
            news_source = response.css('td.views-field-title a::text')[i].extract()
            bias = response.css('td.views-field-field-bias-image img::attr(title)')[i].extract().split(":")[1].strip()
            
            ns_url = urljoin(response.url, response.css('td.views-field-title a::attr(href)')[i].extract())
            try:
                resp = requests.get(ns_url)
                ns_url_allsides = Selector(text=resp.text).css('div.source-image a::attr(href)').extract_first()
                confidence_level = Selector(text=resp.text).css('div.confidence-level div.span8 ::text').extract_first()
            except:
                traceback.print_exc()
                continue
            
            base_url = ""
            for url in search(news_source, stop=1):
                ### out = urlparse(url) 
                ### base_url = out.scheme + "://" + out.netloc
                break
               
            allsides_netloc = urlparse(ns_url_allsides).netloc 
            actual_netloc = urlparse(url).netloc
            print(actual_netloc)
            print(allsides_netloc)
            if ( allsides_netloc.strip() in actual_netloc.strip().lower() or actual_netloc.strip() in allsides_netloc.strip().lower() ) and allsides_netloc.strip()!="":
                match = "yes"
            else:
                match = "no"
                
            # "yes-o" means the allsides.com does not have any evidence that the base_url is the actual url, but it exists
            # "yes-a" means editorials in newspapers (only 2)
            # Some have both editorial/opinion and news, check for both
            print(match)
           
            if confidence_level != "Not Available":
                db = "/Users/Salvi/news_article_dataset/source_url.db"
                conn = sqlite3.connect(db)
                cur = conn.cursor()  
                try:
                    cur.execute("INSERT INTO source (Id, \
                                source_name, \
                                base_url, \
                                as_url, \
                                bias, \
                                confidence, \
                                match_url)\
                            VALUES(?, ?, ?, ?, ?, ?, ?)",(None, news_source, 
                                                             url,
                                                             ns_url_allsides,
                                                             bias,
                                                             confidence_level,
                                                             match
                                                            ))

                    conn.commit()
                    conn.close()
                except sqlite3.IntegrityError:
                    print('Record already inserted')
                """
                yield{
                    'source': news_source,
                    'base_url': url,
                    'as_url': ns_url_allsides,
                    'bias': bias,
                    'confidence': confidence_level,
                    'match': match
                }
                """
                
                if match == "yes":
                    count += 1
            
        print("Found url for %s outlets" % count)

        next_page = response.css('li.pager-next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
