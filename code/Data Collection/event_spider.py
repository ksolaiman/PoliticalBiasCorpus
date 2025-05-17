
# coding: utf-8

import scrapy
import json
import requests
from scrapy.selector import Selector
import newspaper
import os
from collections import defaultdict
import sqlite3
from NewsArticleExtractor import *
import matplotlib.pyplot as plt
import numpy as np
import csv
#from google import search
from dateutil.parser import parse
from helper_functions import *


import xml.etree.cElementTree as ET
import uuid
import os.path

try:
    from urlparse import urlparse  # Python2
except ImportError:
    from urllib.parse import urlparse  # Python3

try:
    from urlparse import urljoin  # Python2
except ImportError:
    from urllib.parse import urljoin  # Python3

class EventScraper(object):
    """
    story (all sides interpretation) and event (our interpretation) is used as similar things
    scrapes stories/events from allsides story-list
    * if duplicate event is found not added 
    """
    def __init__(self, corpus_dir='db', db_name='event_corpus.db'):
        name = "event"
        self.corpus_dir = corpus_dir
        
        self._create_corpus_dir(self.corpus_dir)
        
        self.db_name = db_name
        self.stats = dict()
        
        self.db = None
        self.db = self.corpus_dir + '/' + self.db_name
        self._set_up_db(self.db)
        
        self.stats['already_inserted'] = 0
        self.stats['not_long_enough'] = 0
        self.stats['image_file'] = 0  
        self.stats['fetch_issue'] = 0
        self.stats['correctly_inserted'] = 0
        self.stats['not_insert_db'] = 0
    
        # url = 'https://www.allsides.com/story-list'
        # self.parse(url)
       
    def parse(self, url):
        resp = requests.get(url)    # direct webpage fetch
        body = resp.text    # html text of that webpage
        response = Selector(text=body)
            
        months_script = response.css('div.allsides-daily-topic-container')
        for month_script in months_script:
            month = month_script.css('h3.story-title::text').extract_first().strip()
            stories_script = month_script.css('div.story-list-row')
            for story_script in stories_script:
                story_title = story_script.css('a::text').extract_first().strip()
                story_title = story_title.replace("\"","\'")   # For query purpose
                # print(story_title)
                story_url = urljoin(resp.url, story_script.css('a::attr(href)').extract_first().strip())
                story_date = story_script.css('span.date-display-single::text').extract_first().strip()
                story_date_formatted = story_script.css('span.date-display-single::attr(content)').extract_first().strip() 
                
                if self.check_if_in_db(story_title, story_date_formatted) == 1:
                    continue     # Don't go any further, go to the next event
    
                story_resp = requests.get(story_url)    # direct webpage fetch
                body = story_resp.text    # html text of that webpage
                topic = Selector(text=body).css('div.news-topic a::text').extract_first()    # topic
                print("topic: %s " % topic)
                    
                description = Selector(text=body).xpath('//meta[@name="description"]//@content').extract()
                if len(description) != 0:
                    description = description[0]
                else:
                    description = ""

                # Building the event object to save and return
                clean_event = {
                    'month': month,
                    'name': story_title,
                    'url': story_url,
                    'topic': topic,
                    'description': description,
                    'story_body_html': body,
                    'date': story_date_formatted,
                    'parsed': 0
                }

                self._save_to_db(clean_event)
                

    def _create_corpus_dir(self,directory):

        if not os.path.exists(directory):
            os.makedirs(directory)
            
    def _set_up_db(self,db):

        if os.path.exists(db):
            print('Database exists, assume schema does, too.')
        else:
            print('Need to create schema')
            print('Creating schema...')
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("create table events (\
                        Id INTEGER PRIMARY KEY, \
                        event_name default 'None', \
                        url default 'None', \
                        topic default 'None', \
                        month deafult 'None', \
                        event_date default 'None', \
                        description default 'None', \
                        story_body_html default 'None', \
                        parsed INTEGER default 0\
                        )")   
            cur.execute("CREATE UNIQUE INDEX uni_event on events (event_name, event_date)")  
            
            conn.close()


    def _save_to_db(self, event):
        
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()  
        try:
            cur.execute("INSERT INTO events (Id, \
                        event_name, \
                        url, \
                        topic, \
                        month, \
                        event_date, \
                        description, \
                        story_body_html, \
                        parsed)\
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",(None, event['name'], 
                                                     event['url'],
                                                     event['topic'],
                                                     event['month'],
                                                     event['date'],
                                                    event['description'],
                                                     event['story_body_html'],
                                                    event['parsed']
                                                    ))
                
            conn.commit()
            conn.close()
            return 1
            
        except sqlite3.IntegrityError:
            self.stats['not_insert_db'] += 1
            print('Record already inserted with title %s ' %(event['name'].encode("utf-8")))
            return 0

    def get_stats(self):
        return self.stats
    
    def _remove_punctuations(self, title):
        # TODO optimize for python 3
        # title.translate(title.maketrans("",""), string.punctuation)
            
        return "".join(char for char in title if char not in string.punctuation)


    def check_if_in_db(self, event_name, event_date):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        try:
            sql_str = "SELECT Id from events where event_name LIKE \"%s\" and event_date=='%s'" % (event_name, event_date)
            # print(sql_str)
            rows = cur.execute(sql_str)
            row = [row for row in rows]
            if len(row) != 0:
                return 1
            else:
                return 0
        except sqlite3.IntegrityError:
            print("Problem in query")
            input("What Now !!")

        curr.close()
        conn.close()

    def parse_allsides_page(self):

        parsed_event_id = []
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        # Some of the allsides.com story is absent, topic is NULL for those, just ignore those
        rows = cur.execute("Select event_name, topic, event_date, description, story_body_html, parsed, Id  from events where topic != 'NULL' order by topic")
        for row in rows:

            # New event, 2/3 articles each
            # get information
            event_name = row[0]
            topic = row[1]
            event_date = row[2]
            description = row[3]
            parsed = row[5]
            event_id = row[6]

            # check if already parsed for prime articles, then continue to next event, if even one article is remaining,go in
            if parsed == 1:
                continue

            # New event, 2/3 articles each , so have to save the articles in articles table
            i = 0
            for element in Selector(text=row[4]).css('div.quicktabs-views-group'):
                print("---------------Starting to Fetch----------------------")
                try:
                    news_source = element.xpath('//div[@class="source-area"]//div[@class="news-source"]//a[@href]/text()')[i].extract()
                    bias = element.xpath('//div[@class="source-area"]//div[@class="bias-image"]//img//@title')[i].extract()
                    if bias is not None:
                        bias = bias.split(":")[1].strip()

                    url = element.xpath('//div[@class="news-title"]//a//@href')[i].extract()

                    # Doing this here because we are collecting these news-source, bias and url from the allsides.com page
                    # later doing it means scraping same page twice
                    # Need to make a new NewsArticleExtractor for each article
                    naex = NewsArticleExtractor(self.corpus_dir,
                                                url, topic,
                                                news_source,
                                                event_name,    # event_name
                                                event_date,    # event_date
                                                description,
                                                bias,
                                                article_genre='prime',   # sure about these articles, so prime
                                                datastore_type='sqlite')

                    if naex.check_already_inserted() == 1:
                        # already inserted, continue
                        self.stats['already_inserted'] += 1
                        continue
                    else:
                        article = naex.fetch_add_return(self.stats)
                        if article is not None:
                            print("Fetched the articles, saved them in DB and returning the article informations..")
                            self.stats['correctly_inserted'] += 1
                        else:
                            print("Problem with fetching the article, moving on to the next...")
                            self.stats['fetch_issue'] += 1

                    i += 1
                except:
                    continue

            """
            input("Go to next?")
            # Done with all 3, now update events table parsed = 1, meaning parsed for prime article\
            u_rows = cur.execute("UPDATE events \
                                SET parsed= 1 \
                                WHERE \
                                Id = %s;\
                                " % event_id)
            """
            parsed_event_id.append(event_id)

        cur.close()
        conn.close()
        return parsed_event_id
    
    
    def plotTopicDensity(self):

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        # try:
        # Some of the allsides.com story is absent, topic is NULL for those, just ignore those
        rows = cur.execute("Select topic,  count(*) as freq from events \
                                    where topic != 'NULL' \
                                    group by topic")
        # having freq > 10")

        X_topic = []
        Y = []
        X = []
        color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        i = 0
        for row in rows:
            X_topic.append(row[0])
            Y.append(row[1])
            X.append(i)
            i+=3


        plt.figure()
        plt.xticks(X, X_topic)
        plt.xticks(X, X_topic, rotation=90, fontsize=7) #writes strings with 45 degree angle
        plt.title("Topic vs Event-Frequency")
        plt.xlabel("Topic")
        plt.ylabel("No of Events")
        plt.xlim(-3,i+5)

        for index in range(0, len(X)):
            # plt.text(X[index], Y[index]+5, Y[index], fontsize=7, rotation=90)
            plt.bar(X[index], Y[index], width = 1.5, color=color[index%7]) #, label=X_topic[index],)

        plt.legend(loc="upper right")
        plt.savefig("Topic vs Event-Frequency")

        plt.show()

        # saving to a file
        with open('Topic_Frequency.csv', 'w+') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(("Topic", "Event_Frequency"))
            for index in range(0, len(X)):
                wr.writerow((X_topic[index], Y[index]))

        cur.close()
        conn.close()
        return 1 
    
    
    
    def plotNewsOutletDensity(self, db):

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        # try:
        # Some of the allsides.com story is absent, topic is NULL for those, just ignore those
        rows = cur.execute("select news_source, count(*) as freq from articles group by news_source having freq > 10")

        X_topic = []
        Y = []
        X = []
        color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        i = 0
        for row in rows:
            X_topic.append(row[0])
            Y.append(row[1])
            X.append(i)
            i+=3


        plt.figure()
        plt.xticks(X, X_topic)
        plt.xticks(X, X_topic, rotation=90, fontsize=7) #writes strings with 45 degree angle
        plt.title("News-outlet vs article-Frequency")
        plt.xlabel("News-outlet")
        plt.ylabel("No of Articles")
        plt.xlim(-3,i+5)

        for index in range(0, len(X)):
            # plt.text(X[index], Y[index]+5, Y[index], fontsize=7, rotation=90)
            plt.bar(X[index], Y[index], width = 1.5, color=color[index%7]) #, label=X_topic[index],)

        plt.legend(loc="upper right")
        plt.savefig("News-outlet vs article-Frequency")

        plt.show()

        # saving to a file
        with open('newsOutletArticle_Frequency.csv', 'w+') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(("News Source", "No of articles"))
            for index in range(0, len(X)):
                wr.writerow((X_topic[index], Y[index]))

        cur.close()
        conn.close()
        return
    
    
    def upload_data_to_zaphod(self):
        
        # udz-1
        event_metadata_file = "event_metadata.xml"
        article_metadata_file = "article_metadata.xml"

        # convert to 3 class categorize
        target_names = ['Left','Center','Right']

        def categorize(target_arr):
            # temp = []
            for i in range(0, len(target_arr)):
                if target_arr == 'Left' or target_arr == 'Lean Left':
                    return 'Left'
                elif target_arr == 'Right' or target_arr == 'Lean Right':
                    return 'Right'
                else:    # Center
                    return 'Center'
            return temp


        def read_article(event_name, topic, event_date):

            db = 'db/news_article_corpus.db'
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            try:
                # ignoring Mixed, Not Rated and None bias
                sql_str = "select Id, topic, event_name, title, publish_date, body, bias, news_source, url, html from articles, htmls \
            where bias != 'Mixed' and bias != 'Not Rated' and bias != 'None' \
            and event_name like \"%s\" \
            and topic like \"%s\" \
            and event_date like \"%s\" \
            and articles.Id == htmls.articleId \
            order by publish_date desc" %(event_name, topic, event_date)

                # print(sql_str)
                rows = cur.execute(sql_str)
                article_row = [row for row in rows]

            except sqlite3.IntegrityError:
                print("Problem in query")
                input("What Now !!")

            cur.close()
            conn.close()
            return article_row

    
        # read the event from database
        event_db = 'db/event_corpus.db'
        conn = sqlite3.connect(event_db)
        cur = conn.cursor()
        try:
            # ignoring Mixed, Not Rated and None bias
            sql_str = "select topic, event_name, event_date, description, parsed, Id from events \
                        where parsed != 0 and topic != 'NULL'\
                        order by event_date desc"

            # print(sql_str)
            rows = cur.execute(sql_str)
            row_event = [row for row in rows]

        except sqlite3.IntegrityError:
            print("Problem in query")
            input("What Now !!")

        cur.close()
        conn.close()



        if os.path.exists(event_metadata_file) == False:
            root = ET.Element("data")
        else:
            temp_tree = ET.parse(event_metadata_file)
            root = temp_tree.getroot()

        # If file already exists just parse and get the root
        if os.path.exists(article_metadata_file) == True:
            temp_tree = ET.parse(article_metadata_file)
            article_root = temp_tree.getroot()
        # else create
        else:
            article_root = ET.Element("data")

        # for each row in row_event array, partial or full
        for line in row_event:

            # if you want to run older files, have to comment this if, delete the older xml and doc files and run again
            if line[4] == 2:                                         # parsed == 2
                 continue

            # Get unique id, make the xml file 
            unique_event_id = str(uuid.uuid4())

            # create event element
            event = ET.SubElement(root, "event", id = unique_event_id)

            # Fill in event attributes
            ET.SubElement(event, "name").text = line[1]
            ET.SubElement(event, "date-of-publication").text = line[2]
            ET.SubElement(event, "type").text = line[0]
            ET.SubElement(event, "description").text = line[3]


            # Get the articles of this event from database
            article_row = read_article(line[1], line[0], line[2])
            # print(len(article_row))

            for item in article_row:

                bias = categorize(item[6])
                url = item[8]
                document = item[5]
                news_source = item[7]
                html = item[9]
                document = remove_known_outlet_author_info(url, document, news_source, html)

                # Get unique id, make the xml file 
                unique_article_id = str(uuid.uuid4())

                # create event element
                article = ET.SubElement(article_root, "article", id = unique_article_id, database_id = str(item[0]))

                # Fill in event attributes
                ET.SubElement(article, "title").text = item[3]
                ET.SubElement(article, "date-of-publication").text = item[4]
                ET.SubElement(article, "news-source").text = news_source
                ET.SubElement(article, "news-source-bias").text = bias
                ET.SubElement(article, "url").text = item[8]
                ET.SubElement(article, "event").text = unique_event_id

                # append this article ET at the end of article_root, 
                # article_root.append(article), no need, parse kore read korai enough

                # save the document in the 'docs' folder
                textfile = open('docs/'+unique_article_id+'.txt', 'w')
                textfile.write(document)
                textfile.close()

            ET.SubElement(event, "no-articles").text = str(len(article_row))

            # root.append(event), no need, parse kore read korai enough

            a_tree = ET.ElementTree(article_root)
            a_tree.write(article_metadata_file, encoding="unicode")

            tree = ET.ElementTree(root)
            tree.write(event_metadata_file, encoding="unicode")

            # Update the event 'parsed' attribute in db
            conn = sqlite3.connect('db/event_corpus.db')
            cur = conn.cursor()
            u_rows = cur.execute("UPDATE events \
                                            SET parsed= 2 \
                                            WHERE \
                                            Id = %s\
                                            " % line[5])
            cur.close()
            conn.commit()
            conn.close()
    
    # TODO: Handle all consecutive events, if possible make it automated
    def temporal_analysis(self, month):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rows = cur.execute("select Id, event_name, topic, month, event_date, description from events\
        where topic is not NULL and month = '%s'\
        order by event_date desc" % month)
        row = [row for row in rows]
        
        e_date = []
        topic = []
        e_id = []
        event_name = []
        temp = []
        for index in range(0, len(row)):
            e_id.append(row[index][0])
            e_date.append(parse(row[index][4]).date())
            topic.append(row[index][2])
            event_name.append(row[index][1])
            
        # print(e_date)
        # print(topic)
        color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        
        '''
        plt.figure()
        for index in range(0, len(e_date)):
            plt.plot(e_date[index], topic[index], width = 1.5, color=color[index%7])
        plt.show()
        '''
        
        
        event_map = []
        i = 0
        for index in range(0, len(row)-1):
            if topic[index] == topic[index+1]:
                print(event_name[index])
                print(event_name[index+1])
                add_or_not = input("Are these same events?:")
                if add_or_not is "y":
                    event_map.append( (event_name[index], (e_id[index], e_id[index]+1)) )
            elif topic[index] == topic[index-1]:
                print("Already_added")
            else:
                event_map.append((event_name[index], e_id[index]))
            
        print(event_map)
    
    def set_up_additionals(self, event_name, event_date, topic):
        
        db = 'db/news_article_corpus.db'
        # read the 'prime' articles of this event from the DB
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        try:
            sql_str = "SELECT publish_date, body from articles where \
                event_name LIKE \"%s\" \
                and \
                event_date=='%s' \
                and \
                topic LIKE '%s' \
                and \
                genre LIKE 'prime' " % (event_name, event_date, topic)
            
            rows = cur.execute(sql_str) 
            
            prime_article = []
            for row in rows:
                date_string = row[0]
                dt = parse(date_string)
                # print(dt.date())
                prime_article.append((dt.date(), row[1]))
                
            # row = [row for row in rows]
            return prime_article
            
        except sqlite3.IntegrityError:
            print("Problem in query")
            # input("What Now !!")
            return 0

    def calculate_additionals(self, event_name, event_date, description, prime_article):
        
        max_date = parse(event_date).date()
        min_date = max_date
        for index in range(0, len(prime_article)):
            if prime_article[index][0] < min_date:
                min_date = prime_article[index][0]
            elif prime_article[index][0] > max_date:
                max_date = prime_article[index][0]
                
        ne_tree = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(event_name)))
        actors = get_actors(ne_tree)
        print(actors)
        
        ne_tree = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(description)))
        actors = get_actors(ne_tree)
        print(actors)
        
        for index in range(0, len(prime_article)):
            ne_tree = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize( prime_article[index][1] )))
            actors = get_actors(ne_tree)
            print(actors)
            
        return max_date, min_date
    
    def parse_google_results(self, begin_id, end_id):

        parsed_event_id = []
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        rows = cur.execute("Select event_name, topic, event_date, description, story_body_html, parsed, Id  \
        from events where    topic != 'NULL' and \
        Id between %s and %s" % (begin_id, end_id))
        # order by topic")
        
        for row in rows:

            # New event, 2/3 articles each
            # get information
            event_name = row[0]
            topic = row[1]
            event_date = row[2]
            description = row[3]
            parsed = row[5]
            event_id = row[6]
            
            prime_articles = self.set_up_additionals(event_name, event_date, topic)
            max_date, min_date = self.calculate_additionals(event_name, event_date, description, prime_articles)
            
            # check if already parsed for subs. articles, then continue to next event :: not that necessary after using begin and end index
            if parsed == 2:
                continue
                
            search_text = event_name
            
            src_url_db = "db/source_url.db"
            conn2 = sqlite3.connect(src_url_db)
            cur2 = conn2.cursor()
            
            # Google search
            for url in search(search_text, stop=80):
                
                print(url)
                
                # Getting news_source and bias(if any)
                out = urlparse(url)
                link = out.scheme + "://" + out.netloc + "/%"
                    
                url_rows = cur2.execute("Select*  \
                from source where match_url != 'no' \
                and base_url like '%s' \
                or as_url like '%s' " % (link, link))
                
                news_source = None
                bias = None
                
                u0 = url.split(":")[1].strip('/')
                
                for urow in url_rows:
                    u1 = urow[3].split(":")[1].strip('/')
                    u2 = urow[2].split(":")[1].strip('/')
                    if u0.strip().startswith(u1.strip()):     # urow['as_url']
                        news_source = urow[1]
                        bias = urow[4]
                        break
                    elif u0.strip().startswith(u2.strip()):     # urow['base_url']
                        news_source = urow[1]
                        bias = urow[4]
                        break
                        
                        
                if news_source is None:
                    try:
                        outlet = newspaper.build(url)
                        news_source = outlet.brand
                    except:
                        print("Error in parsing news source")
                        news_source = u0.split("/")[0]
                
                        
                print("---------------Starting to Fetch----------------------")
                try:
                    naex = NewsArticleExtractor(self.corpus_dir,
                                                url, topic,
                                                news_source,
                                                event_name,    # event_name
                                                event_date,    # event_date
                                                description,
                                                bias,
                                                article_genre='sub',   # sure about these articles, so prime
                                                datastore_type='sqlite')

                    if naex.check_already_inserted() == 1:
                        # already inserted, continue
                        print("Already in the DB")
                        self.stats['already_inserted'] += 1
                        continue
                    else:
                        if prime_articles != 0:
                            naex.set_up_additionals(prime_articles, max_date, min_date)
                            
                            article = naex.fetch_add_return(self.stats)
                            if article is not None:
                                print("Fetched the articles, saved them in DB and returning the article informations..")
                                self.stats['correctly_inserted'] += 1
                            else:
                                print("Problem with fetching the article, moving on to the next...")
                                self.stats['fetch_issue'] += 1
                except:
                    continue

            """
            input("Go to next?")
            # Done with all 3, now update events table parsed = 1, meaning parsed for prime article\
            u_rows = cur.execute("UPDATE events \
                                SET parsed= 1 \
                                WHERE \
                                Id = %s;\
                                " % event_id)
            """
            parsed_event_id.append(event_id)

        cur.close()
        conn.close()
        return parsed_event_id


        # TODO: IF NEEDED
    def get_all_events(self):
        '''
        Opens the file and read all the events
        Returns the event list with all information
        '''
        filename = getattr(self, 'filename', None)
        if filename is not None:
            f = open(filename,"r+")
        else:
            f = open("event_list.jl","r+")
        arr = []
        for line in f:
            arr.append( json.loads(line))

        f.close()
        return arr


    def get_stats(self):
        return self.stats

if __name__ == '__main__':
    pass

es = EventScraper()

url = 'https://www.allsides.com/story-list'
# Parse the above url
es.parse(url)
# Plot topic vs event-density
#### es.plotTopicDensity()

# parse allsides.com story page
print(es.get_stats())
parsed_event_id = es.parse_allsides_page()    # might have to input dates manually for some/ fix_if_missing()
print(es.get_stats())

# Updating id for already parsed event for allsides page
print(parsed_event_id)
conn = sqlite3.connect('db/event_corpus.db')
cur = conn.cursor()
for eid in parsed_event_id:
    u_rows = cur.execute("UPDATE events \
                                    SET parsed= 1 \
                                    WHERE \
                                    Id = %s\
                                    " % eid)
cur.close()
conn.commit()
conn.close()

es.upload_data_to_zaphod()
# es.plotNewsOutletDensity('/Users/Salvi/news_article_dataset/news_article_corpus.db')
### es.temporal_analysis('December 2017')
# es.parse_google_results(2, 3)
