import feedparser
from pprint import pprint
import sys
import os
import json
import io
from collections import defaultdict
import sqlite3
import string
import urllib
import nltk
import traceback

from newspaper import Article
from scrapy.selector import Selector
from dateutil.parser import parse
from dateutil.parser import parse as date_parser
import newspaper
import re
from datetime import datetime, date

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

from helper_functions import *


class NewsArticleExtractor(object):
    def __init__(self, corpus_dir, url, topic, news_source, event_name, event_date,
                 event_description_allsides, bias,
                 article_genre='prime',
                 datastore_type='file', db_name='news_article_corpus.db'):
        '''change
        Read links and associated categories for specified articles
        in text file seperated by a space

        Args:
            corpus_dir (str): The directory to save the generated corpus
            datastore_type (Optional[str]): Format to save generated corpus.
                                            Specify either 'file' or 'sqlite'.
            db_name (Optional[str]): Name of database if 'sqlite' is selected.
        '''

        self.corpus_dir = corpus_dir
        self.datastore_type = datastore_type
        self.db_name = db_name
        self.url = url
        self.topic = topic
        self.news_source = news_source
        self.bias = bias
        self.event_name = event_name
        self.event_date = event_date

        # To see if articles from allsides or random
        self.article_genre = article_genre

        # To check during checking relevance
        self.event_description_allsides = event_description_allsides

        self._create_corpus_dir(self.corpus_dir)

        self.db = None
        if self.datastore_type == 'sqlite':
            self.db = self.corpus_dir + '/' + self.db_name
            self._set_up_db(self.db)

            # if ex.fetch_add_return() is not None:
            #    print("Fetched the articles, saved them in DB and returning the article informations..")
            # else:
            #    print("Problem with fetching the article, moving on to the next...")

    def check_already_inserted(self):
        conn = sqlite3.connect(self.db)
        with conn:
            cur = conn.cursor()
            try:
                sql_str = "SELECT Id from articles where \
                event_name LIKE \"%s\" \
                and \
                event_date=='%s' \
                and \
                url LIKE '%s'" % (self.event_name, self.event_date, self.url)
                # print(sql_str)
                rows = cur.execute(sql_str) 
                row = [row for row in rows]
                # print("Checking if inserted: %s" % len(row))
                if len(row) > 0:
                    return 1
                else:
                    return 0
            except sqlite3.IntegrityError:
                print("Problem in query")
                input("What Now !!")
                return 0
                
    def fetch_add_return(self, stats):

        if self._fetch_article(self.url, 20) == 1:
            # successful fetch
            print('successful fetch')

            # Building the article object to save and return
            clean_article = {
                'topic': self.topic,
                'event_name': self.event_name,
                'title': self.title,
                'html': self.html,
                'url': self.url,
                'publish_date': self.publish_date,
                'event_date': self.event_date,
                'body': self.body,
                'summary': self.summary,
                'news_source': self.news_source,
                'bias': self.bias,
                'authors': self.authors,
                'genre': self.article_genre
            }

            # To check if it is ok to add
            # check if self.body > 5 sentences
            # Not in db already
            # has actual affiliation with this event

            # `add to DB`/`save` after `checking if it is ok to add`
            if self._check_if_ok_to_add_article_to_db(stats) == 1:
                # self._save_to_db()    # instead of this we are making 2 methods, file or sqlite save
                self._save_article(clean_article)
                # return 1
                return clean_article
            else:
                return None
        
        else:
            print('Problem with fetch')
            # fetch has issues
            # No need to `add to DB` / `save`

            ## return 0
            return None

    def _create_corpus_dir(self, directory):

        if not os.path.exists(directory):
            os.makedirs(directory)

    def _set_up_db(self, db):

        if os.path.exists(db):
            print('Database exists, assume schema does, too.')
        else:
            print('Need to create schema')
            print('Creating schema...')
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("create table articles (\
                        Id INTEGER PRIMARY KEY, \
                        topic default 'None', \
                        event_name default 'None', \
                        title default 'None', \
                        url default 'None', \
                        publish_date default 'None', \
                        event_date default 'None', \
                        body default 'None', \
                        summary default 'None', \
                        news_source default 'None', \
                        bias default 'None', \
                        genre default 'None'\
                        )")
            cur.execute("CREATE UNIQUE INDEX uni_article on articles (title, url, event_date)")

            # For author
            cur.execute("create table authors (\
                        authorId INTEGER PRIMARY KEY, \
                        articleId INTEGER NOT NULL, \
                        author NOT NULL, \
                        FOREIGN KEY (articleId) REFERENCES articles(Id)\
                        )")
            # End the part for author
            
            # For html
            cur.execute("create table htmls (\
                        htmlId INTEGER PRIMARY KEY, \
                        articleId INTEGER NOT NULL, \
                        html default 'None', \
                        FOREIGN KEY (articleId) REFERENCES articles(Id)\
                        )")
            # End the part for html

            conn.close()
    
    
    def _check_similarity(self, news_desc):
        
        # news_desc is an array
        # First doc is the current article body
        # Second doc is the event description
        # Next ones are the prime articles body
        
        print(len(news_desc))
        str0 = get_tokens(self.event_description_allsides)
        str0 = [w + " " for w in str0]
        strJ0 = "".join(str0)
        
        # if len(news_desc) < 4:
        str3 = get_tokens(news_desc[2])
        str3 = [w + " " for w in str3]
        strJ3 = "".join(str3)
        str2 = get_tokens(news_desc[1])
        str2 = [w + " " for w in str2]
        strJ2 = "".join(str2)
        str1 = get_tokens(news_desc[0])
        str1 = [w + " " for w in str1]
        strJ1 = "".join(str1)
        
        if len(news_desc) < 1:
            input("Missing, so interuption, click to continue")
        
        str4 = get_tokens(self.body)
        str4 = [w + " " for w in str4]
        strJ4 = "".join(str4)
        
        vect = TfidfVectorizer(min_df=1)
        
        try:
            if len(news_desc) == 1:
                tfidf = vect.fit_transform([strJ0, strJ1, strJ4])
            elif len(news_desc) == 2:
                tfidf = vect.fit_transform([strJ0, strJ1,strJ2,strJ4])
            elif len(news_desc) == 3:
                tfidf = vect.fit_transform([strJ0, strJ1,strJ2,strJ3,strJ4])
        except:
            traceback.print_exc()
        
        sim = (tfidf * tfidf.T).A 
        
        print("Title: %s " % self.title)
        print("URL: %s " % self.url)
        if sim[1][4] < 0.1 and sim[2][4] < 0.1 and sim[3][4] < 0.1:
            print("Body: %s " % self.body)
            return 0
        
        # if sim < 0.2 for any of the three
        # check the title similarity
        # For dates, we can allow the range the three prime articles are in
        print(sim)
        return 0

    def set_up_additionals(self, prime_article, max_date, min_date):
        self.prime_article = prime_article

        self.max_date = max_date
        self.min_date = min_date
            
    # TODO
    def _check_if_relevant_to_event(self):
        
        # Fetch the prime articles
        prime_article = self.prime_article
        min_date = self.min_date
        max_date = self.max_date
        
        
        # Filter 1 - date range
        try:
            pub_date = parse(str(self.publish_date)).date()
        except:
            traceback.print_exc()
        
        if pub_date >= min_date and pub_date <= max_date:
            print("Within date range")
        else:
            print("Date range out")
            # input("Interuppted to see if correct, later comment out")
            return 0
        
        # Filter 2 - Author check
        
        """
            print(len(row))
            ref_doc = []
            for index in range(0, len(row)):
                ref_doc.append(row[index][1])     # Next ones are the prime articles body
            
            print(len(ref_doc))
            
            self._check_similarity(ref_doc)
            input("Missing, so interuption, click to continue")
        """
            
        """
                # print("Checking if inserted: %s" % len(row))
                if len(row) > 0:
                    return 1
                else:
                    return 0
        """
            
       
        # save their body
        # can create a class for this
        return 0

    def _check_if_ok_to_add_article_to_db(self, stats):
        
        # First we need to check if the description / body is worth storing: have significant length (both prime & substitute)
        sentences = nltk.sent_tokenize(self.body)
        if len(sentences) < 5:  # smaller than 3, no need to store, else continue on to other checks
            print('Not long enough')
            stats['not_long_enough'] += 1
            return 0
        if self.url.endswith('jpg'):
            print('Image File')
            stats['image_file'] += 1
            return 0

        # Backup code - if we can fix this
        self.fix_if_anything_missing()

        # Stories in the Allsides.com story page,
        # so assuming, original (no duplicate in db yet) :: update - unique index on title will take care of it
        # and everything is fine (relevant to this event) :: fix_if_anything_missing() will take care
        # if genre is `prime`, no need to check relevance
        # return true
        if self.article_genre is 'prime':
            return 1
        else:
            # check if already in db : no need, unique index on title will take care of it
            print('sub')
            # check relevance
            self._check_if_relevant_to_event()
            # For checking relevance with body, also check title similarity with 3 prime/base articles
            return 0

    def fix_if_anything_missing(self):

        print("date: %s" % self.publish_date)
        print("authors: %s" % self.authors)
        print("source: %s" % self.news_source)
        print("bias: %s" % self.bias)

        
        DATE_REGEX = r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'
        
        """
        if "newsweek" in self.url:
            html_lines = Selector(text=self.html).xpath('//script[@type="application/ld+json"]').extract()
            print(html_lines)

        if "washingtonpost" in self.url:
            authors = Selector(text=self.html).xpath('//span[@itemprop="name"]//text()').extract()[0]
            if authors:
                print('Author by my search-1 for washingtonpost: %s' % authors)

        if "thehill" in self.url:
            authors = Selector(text=self.html).xpath('//meta[@property="author"]//@content').extract()[0]
            if authors:
                print('Author by my search-2 for thehill.com: %s' % authors)
        
        1. <time class="post__date" datetime="2017-12-18T13:56:53+00:00">
        2. <span itemprop="datePublished" content="2017-12-18T17:00:00.000Z"> 
        3. <time datetime="2017-12-20T11:14:44+00:00" pubdate class="updated">Published: 5 days ago</time>
        4. buzzfeed
        5. <meta itemprop="datePublished" content="2017-12-11T22:40:00.000Z" />
        6. <meta itemprop="datePublished" content="2017-12-11T21:23:08"/>
        7. Huge
        8. <meta itemprop="datePublished" content="2017-12-07T10:52:45+00:00" />
        9. <time class="lb-card-timestamp" datetime="2017-12-12T21:19:00-08:00">  Dec. 12, 2017, 9:19 p.m.          </time>
        10. <meta name="Last-Modified" content="2017-12-02 04:12:49" />
        11. Huge2
        12. Huge3 / bustle.com
        13. <meta itemprop="datePublished" content="2017-09-01T15:17:26-04:00"> msnbc
        14. Huge4 slate
        15 <time class="op-published H" datetime="2017-02-23T05:09:30Z">23 Feb, 2017</time> breitbart.com
        """
        try:
            if "thinkprogress.org" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//time[@class="post__date"]//@datetime').extract_first()
            if "washingtonpost" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//span[@itemprop="datePublished"]//@content').extract_first()
            if "wnd.com" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).css('time::attr(datetime)').extract_first()
            if ("wsj.com" in self.url or "msnbc.com" in self.url)and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//meta[@itemprop="datePublished"]//@content').extract_first()
            if "nydailynews.com" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//meta[@itemprop="datePublished"]//@content').extract_first()  
            if ("bbc.com" in self.url or "cbsnews.com" in self.url or "bustle.com"  in self.url) and self.publish_date is None:
                str_temp = Selector(text=self.html).css('script::text').extract_first().strip()
                arr = json.loads(str_temp)
                self.publish_date = arr['datePublished']
            if "motherjones.com" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//meta[@itemprop="datePublished"]//@content').extract_first()
            # much more correct
            if "latimes" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//time[@class="lb-card-timestamp"]//@datetime').extract_first()
            if "abcnews.go" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//meta[@name="Last-Modified"]//@content').extract_first()
            if ("nbcnews.com" in self.url or "vanityfair.com" in self.url) and self.publish_date is None:
                try:
                    str_temp = Selector(text=self.html).css('script::text').extract()[1].strip()   # 2nd script has date
                    arr = json.loads(str_temp)
                    self.publish_date = arr['datePublished']
                except:
                    self.publish_date = Selector(text=self.html).xpath('//meta[@name="published"]//@content').extract_first() 
            if "time.com" in self.url and self.publish_date is None:
                str_temp = Selector(text=self.html).css('script::text').extract()[0].strip()
                arr = json.loads(str_temp)
                self.publish_date = arr[2]['datePublished']   # 2nd array has date
            if "slate.com" in self.url and self.publish_date is None:
                str_temp = Selector(text=self.html).xpath('//meta[@name="parsely-page"]//@content').extract_first()
                arr = json.loads(str_temp)
                self.publish_date = arr['pub_date']
            if "breitbart.com" in self.url and self.publish_date is None:
                self.publish_date = Selector(text=self.html).xpath('//time[@class="op-published"]//@datetime').extract_first()
              
            
            if self.publish_date is None:     # still
                self.publish_date = Selector(text=self.html).xpath('//meta[@itemprop="datePublished"]//@content').extract_first()
                self.publish_date = Selector(text=self.html).xpath('//script[@type="application/ld+json"]').extract()
                print("Last resort working")
            
               
        except:
            print("Issue with %s" % self.url)
            wtd = input("What to do? :")
        
        if self.publish_date is None:
            print("Here is the url: %s" % self.url)
            date = input("Enter the missing date: ")
            self.publish_date = date

        """
        if len(self.authors) == 0:
            print("Here is the url: %s" % self.url)
            self.authors = []
            author = input("Enter the missing author: ")
            self.authors.append(author)
            more_than_one = input("More authors: (y/n) ")
            while more_than_one == 'y':
                author = input("Enter the missing author: ")
                self.authors.append(author)
                more_than_one = input("More authors: (y/n) ")
        """
        if self.news_source is None:
            print("Here is the url: %s" % self.url)
            source = input("Enter the source: ")
            self.news_source = source


    def _fetch_article(self, url, timeout=20):

        try:
            article = Article(url, request_timeout=timeout)
            article.download()
            self.html = article.html  # saving so later can use this to fill up missing dates or authors

            article.parse()
            article.nlp()

            self.title = article.title
            # self.url
            self.authors = article.authors
            self.publish_date = article.publish_date
            # self.event_name
            # self.event_date
            self.body = article.text
            # self.topic
            ###### self.keywords = article.keywords    (can generate from body whenever necessary)
            self.summary = article.summary
            # self.news_source
            # self.bias

            # return true if any article fetch is succesful, doesn't matter prime or substitute article
            # else return false (in the exception)
            return 1

        except newspaper.article.ArticleException:
            print('%s throws ArticleException' % url)
            return 0

    def _save_article(self, clean_article):

        print("Saving article %s..." % (clean_article['title'].encode("utf-8")))

        if self.datastore_type == 'file':
            self._save_flat_file(clean_article)
        elif self.datastore_type == 'sqlite':
            # self._save_to_db(clean_article)
            self._save_to_db()
        else:
            raise Exception("Unsupported datastore type. Please specify file or sqlite")

    def _remove_punctuations(self, title):
        # TODO optimize for python 3
        # title.translate(title.maketrans("",""), string.punctuation)
        return "".join(char for char in title if char not in string.punctuation)

    def _save_flat_file(self, clean_article):

        directory = self.corpus_dir + '/' + clean_article['topic'] + '/' + clean_article['event_name']

        # create category directory
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = directory + '/' + \
                    self._remove_punctuations(clean_article['title']).replace(" ", "_") + '.json'

        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(str(json.dumps(clean_article, ensure_ascii=False, default=json_serial, indent=4)))

    def _save_to_db(self):

        conn = sqlite3.connect(self.db)
        with conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO articles (Id, \
                        topic, \
                        event_name, \
                        title, \
                        url, \
                        publish_date, \
                        event_date, \
                        body, \
                        summary, \
                        news_source, \
                        bias, \
                        genre)\
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, self.topic, self.event_name,
                                                                  self.title, self.url,
                                                                  self.publish_date, self.event_date, self.body,
                                                                  self.summary,
                                                                  self.news_source, self.bias, self.article_genre))

                last_insert_rowid = cur.execute("SELECT last_insert_rowid()")
                row = [row for row in last_insert_rowid]
                print("Last Article Insert Row Id : %s" % row[0][0])

                for index in range(0, len(self.authors)):
                    cur.execute("INSERT INTO authors ( authorId, \
                            articleId, \
                            author)\
                        VALUES(?, ?, ?)", (None, row[0][0], self.authors[index]))
                    
                cur.execute("INSERT INTO htmls ( htmlId, \
                            articleId, \
                            html)\
                        VALUES(?, ?, ?)", (None, row[0][0], self.html))

            except sqlite3.IntegrityError:
                # stats['not_insert_db'] += 1
                print('Record already inserted with title %s ' % (self.title.encode("utf-8")))


if __name__ == '__main__':
    pass

