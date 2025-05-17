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
from dateutil.parser import parse
import re

try:
    from urlparse import urlparse  # Python2
except ImportError:
    from urllib.parse import urlparse  # Python3

try:
    from urlparse import urljoin  # Python2
except ImportError:
    from urllib.parse import urljoin  # Python3
    
    
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

# add all news sources in this following array like buzzfeed later
stupid_words_cant_be_name = ['Play', 'Facebook', 'Twitter', 'Images', 'Video', 'Buzzfeed', 'Email', 'Invalid',
                             'Photo', 'Sign', 'Up', 'Continue']
# Making names like [Mr. Kelly] to [Kelly]
words_to_shave_off = ['Mr.', 'Mrs.', 'Ms.', 'Mr', 'Mrs', 'Ms', 'mr.', 'mrs.', 'ms.', 'mr', 'mrs', 'ms']


def get_actors(ne_tree):

    from nltk.chunk import conlltags2tree, tree2conlltags
    iob_tagged = tree2conlltags(ne_tree)
    # print(iob_tagged)
    people = []
    i = 0
    index = 0
    while index < len(iob_tagged):
        if 'PERSON' in iob_tagged[index][2]:
            if iob_tagged[index][2].startswith('B'):   # Beginning
                name = iob_tagged[index][0]
                while iob_tagged[index+1][2].startswith('I'):
                    name += (" " + iob_tagged[index+1][0])
                    index += 1
                add_ok, name = ok_to_add(name, people)
                if add_ok == 1:
                    people.append(name)
                    i += 1
        index += 1
    return people

def substract(a, b):
    return "".join(a.rsplit(b))

def ok_to_add(name, name_arr):

    # compatability
    actor_0 = name

    # add all news sources in this following array like buzzfeed later
    # stupid_words_cant_be_name = ['Play', 'Facebook', 'Twitter', 'Images', 'Video', 'Buzzfeed', 'Email', 'Invalid', 'Photo']

    # Making names like [Mr. Kelly] to [Kelly]
    # words_to_shave_off = ['Mr.', 'Mrs.', 'Ms.', 'Mr', 'Mrs', 'Ms']

    if actor_0.endswith("’s"):
        actor_0 = actor_0.strip("’s")

    for word in words_to_shave_off:
        #if word in actor_0:
        if actor_0.startswith(word):
            actor_0 = substract(actor_0, word)
            # Getting rid of extra " "
            actor_0 = actor_0.strip()
            break


    # Delete exact duplicates at least ['Moore', 'Moore'] Not ['Roy Moore', 'Moore'], because we can have this
    # type of NERs - ['Play Facebook Twitter Moore', 'Moore']
    if actor_0 not in name_arr:
        # New idea, we can add some stupid words array, which will have words to remove
        # This will somewhat delete duplicates like ['Play Facebook Twitter Moore']
        # stupid_words_cant_be_name = ['Play', 'Facebook', 'Twitter', 'Images', 'Video', 'Buzzfeed']
        cant_be_name = 0
        # Look through all stupid words
        for word in stupid_words_cant_be_name:
            if word in actor_0:  # not the other way around, coz [Play] is in ['Play Facebook Twitter Moore']
                cant_be_name = 1
        if cant_be_name == 0:
            # clean, can be name
            # Now we can try and eliminate duplicates like this ['Roy Moore', 'Moore']
            # Go through already added names, and if none of them has match then eligible to add
            ok_to_add = 1
            for name in name_arr:
                if actor_0 in name:
                    # duplicate, still have to check for longer name
                    if len(actor_0.split(" ")) < len(name.split(" ")): # Prefer Roy Moore over Moore
                        ok_to_add = 0
            # else, no duplicate, ok to add which is already 1

            if ok_to_add == 1:
                return 1, actor_0

    return 0, ""


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_tokens(text):

    try:
        #text = re.sub(r'[^\w ]', '', text)  # strip special chars
        lowers = text.lower()
        # tokenize sentence to words and punctuations/ stop words
        tokens = nltk.word_tokenize(lowers)

        punctuations = string.punctuation+"\"\'”“—"

        # remove ajaira things from around the tokens
        stripped = [w.strip(punctuations) for w in tokens]

        # remove empty ones
        cleared = [w for w in stripped if not w in '']

        # remove stop words
        filtered = [w for w in stripped if not w in stopwords.words('english')]
        #filtered = [w for w in filtered if not w in stopwords_arr]

        filtered = [w for w in filtered if not w in words_to_shave_off]

        '''
        for w in filtered
        for word in words_to_shave_off:
            if actor_0.startswith(word):
                actor_0 = substract(actor_0, word)
                # Getting rid of extra " "
                actor_0 = actor_0.strip()
        '''

        full_filtered = [w for w in filtered if not w in punctuations]

        full_filtered_spaced = [w + " " for w in full_filtered]

        #### print(full_filtered[0:10])

        # pos tagged
        sentences = nltk.sent_tokenize("".join(full_filtered_spaced))  # important line, without using this pos doesn't work
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        pos_tagged_sentences = sentences[0]

        #### print(pos_tagged_sentences[0:10])

        # lemmatized
        wordnetlemma = WordNetLemmatizer()
        lemmatized = []
        for w in pos_tagged_sentences:
            if w[1].startswith("VB"):
                lemmatized.append(wordnetlemma.lemmatize(w[0], 'v'))
            elif w[1].startswith("JJ"):
                lemmatized.append(wordnetlemma.lemmatize(w[0], 'a'))
            elif w[1].startswith("RB"):
                lemmatized.append(wordnetlemma.lemmatize(w[0], 'r'))
            elif w[1].startswith("NN"):
                lemmatized.append(wordnetlemma.lemmatize(w[0], 'n'))
            else:
                lemmatized.append(w[0])

        #lemmatized = [wordnetlemma.lemmatize(w[0], 'v') for w in pos_tagged_sentences if w[1].startswith("VB")]

        #### print(lemmatized[0:10])

        # porter_stemmer = PorterStemmer()
        # stemmized = [porter_stemmer.stem(w) for w in lemmatized]
        # print(stemmized[0:10])
        stemmized = []
        for w in lemmatized:
            if w.endswith("’s"):
                stemmized.append(w.strip("’s"))
            else:
                stemmized.append(w)
        #### print(stemmized[0:20])

        return stemmized

    except:
        return None
    
    
def remove_outlet_author_info(url, sentence, outlet_name, htmlbody):
    '''
    try:
        resp = requests.get(url)    # direct webpage fetch
        resp.encoding = 'UTF-8'
        body = resp.text    # html text of that webpage
    except:
        body = ""
    '''
    response = Selector(text=htmlbody)
    
    if outlet_name == 'The Hill':
        
        arr = []
        body = ""
        
        bset = response.xpath('//p//text()').extract()
        aset = response.xpath('//span//text()').extract()

        aset_discard = []
        for item in bset:
            if item in aset:
                try:
                    i = aset.index(item)
                    i+=1
                    tstr = ""
                    temp = []
                    if 'MORE' in aset[i:]:
                        while aset[i-1] != 'MORE':
                            temp.append(aset[i])
                            i+=1
                except:
                    continue
                
                aset_discard.append(tstr.join(temp))

        # print(aset_discard)

        for item in aset_discard:
            sentence = sentence.replace(item,'')
        
        # author name paragraph has <em> tag around
        author_name = response.xpath('//p//em//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')

        sentence = sentence.replace('ADVERTISEMENT','')

        sentence = re.sub(r'[Tt][Hh][Ee] [Hh][Ii][Ll][Ll]', r'', sentence)
        
    elif outlet_name == 'CNN (Web News)':
        removals = []
        # <cite class="el-editorial-source">Washington (CNN)</cite>
        editorial_source = response.css("cite.el-editorial-source::text").extract()
        # <q class="el-editorial-note">Douglas Heye is a CNN political commentator and former deputy chief of staff to then-House Majority Leader Eric Cantor. The opinions expressed in this commentary are his own.</q></p></div><div class="el__leafmedia el__leafmedia--sourced-paragraph"><p class="zn-body__paragraph speakable"><cite class="el-editorial-source"> (CNN)</cite>
        editorial_note = response.css("q.el-editorial-note::text").extract()
        
        others = ["Read More"]
        
        removals.append(editorial_source)
        removals.append(editorial_note)
        removals.append(others)
        
        for lists in removals:
            for item in lists:
                sentence = sentence.replace(item.strip(),'')
                
                
        # CNN's Briana Keller - CNN's [A-Z] - capital letter means name
        sentence = re.sub(r'[Cc][Nn][Nn]\'s( [A-Z][^ ]*)+', r'', sentence)
        # CNN poll
        # sentence = re.sub(r'CNN [Pp][Oo][Ll][Ll]', r'', sentence)
        # self quote
        sentence = re.sub(r'[Cc][Nn][Nn][^ ]*', r'', sentence)
        
    elif outlet_name == 'Politico':   
        removals = []
        #advertisement in the middle, the other news urls doesn't stick-out
        source_adv = response.css('aside.story-related p::text').extract()
        ###print(source_adv)
        #<p><i>Eric Wolff, Janosch Delcker, Kalina Oroschakoff and Anca Gurzu contributed to this report.</i></p>
        author = response.xpath('//p//i//text()').extract()
        
        removals.append(source_adv)
        removals.append(author)
        
        #for lists in removals:
        for item in source_adv:
            if item in sentence:
                sentence = sentence.replace(item,'')
        for item in author:
            sentence = sentence.replace(item,'')
                
        sentence = re.sub(r'[Pp][Oo][Ll][Ii][Tt][Ii][Cc][Oo][^ ]*', r'', sentence)
        
    elif outlet_name == 'NPR News': 
        # CNN's Briana Keller - CNN's [A-Z] - capital letter means name
        sentence = re.sub(r'[Nn][Pp][Rr]\'s( [A-Z][^ ]*)+', r'', sentence)
        # others
        sentence = re.sub(r'[Nn][Pp][Rr] [Nn][Ee][Ww][Ss]', r'', sentence) # Didn't test this
        sentence = re.sub(r'[Nn][Pp][Rr][^ ]*', r'', sentence)
    
    elif outlet_name == 'USA TODAY': 
        # <div class="article-print-url">Read or Share this story: http://usat.ly/1F7A4ox</div>
        share_text = response.css('div.article-print-url::text').extract()
        
        for item in share_text:
            sentence = sentence.replace(item,'')
        
        # others
        sentence = re.sub(r'[Uu][Ss][Aa] [Tt][Oo][Dd][Aa][Yy]', r'', sentence)
            
    elif outlet_name == 'Fox News':
        # author name paragraph has <i> tag around
        author_name = response.xpath('//p//i//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')
            
        adv = "Want FOX News First in your inbox every day? Sign up here."
        sentence = sentence.replace(adv,'')
        
        others = "Click here for more from"
        sentence = sentence.replace(others,'')
        
        # <em>[Watch Fox: </em><i><b>President Obama</b></i><em><b> </b>holds a press conference at the G20 Summit in St. Petersburg, Russia in the 9 a.m. ET hour]</em>
        sentence = re.sub(r'\[Watch Fox.*\]', r'', sentence)
        
        # others
        # Sky News - may be a division of fox news
        sentence = re.sub(r'([Ff][Oo][Xx])|([Ss][Kk][Yy])( [Nn][Ee][Ww][Ss])?( Channel \(FNC\))*', r'', sentence)
    
    elif outlet_name == 'Washington Times':
        
        # <div class="bigtext"><p>DELAWARE, Ohio &mdash;
        sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        
        # <p>&bull; <em>Wesley Pruden is editor emeritus of The Washington Times.</em></p>
        # author name paragraph has <em> tag around
        author_name = response.xpath('//p//em//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')
            
        # Special case
        if '•' in sentence:
            sentence = sentence[0:sentence.index('•')]
            
        sentence = re.sub(r'(Washington)( Times)', r'', sentence)
            
    elif outlet_name == 'Townhall':
        # <p>DELAWARE, Ohio &mdash;
        sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        if '_' in sentence:
            sentence = sentence[0:sentence.index('_')]
            
        sentence = re.sub(r'([Tt][Oo][Ww][Nn][Hh][Aa][Ll][Ll])[^ ]*', r'', sentence)
            
    # May need a lil work - in (Ariana Grande/The Washington Post) type thing
    elif outlet_name == 'Washington Post':
        # <p>DELAWARE, Ohio &mdash;
        sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        if '_' in sentence:
            sentence = sentence[0:sentence.index('_')]
            
        sentence = re.sub(r'(The )?(Washington)( Post)', r'', sentence)
        
    elif outlet_name == 'HuffPost':
        # <p>DELAWARE, Ohio &mdash;
        sentence = re.sub(r'^(.* [—|–|-])', r'', sentence)
        if '_' in sentence:
            sentence = sentence[0:sentence.index('_')]
        # author name paragraph has <em> tag around
        '''
        author_info = response.xpath('//p//em//text()').extract()
        for item in author_info:
            sentence = sentence.replace(item,'')
        '''
        sentence = re.sub(r'(HuffPost)[^ ]*', r'', sentence)
        
    # Vox needs not to do anything
    elif outlet_name == 'Vox':
        sentence = re.sub(r'(Vox)[^ ]*', r'', sentence)
    
    elif outlet_name == 'New York Times':
        arr = []
        body = ""
        try:
            flag = 0
        
            actual_body = response.css('p.story-body-text::text').extract()
            if len(actual_body)>1:
                for item in response.xpath('//p//text()').extract():
                    if sentence.startswith(item):
                        break
                    elif actual_body[0].startswith(item[0]) == True and flag == 0:
                        arr.append(item+"\n")
                        flag = 1
                        continue
                    elif flag != 1:
                        continue
                    arr.append(item+"\n")
        except IndexError:
            print("Index Exception")
        sentence = body.join(arr) + sentence
        
        # Now get rid of the extra things
        # <p>DELAWARE, Ohio &mdash;
        sentence = re.sub(r'^(.* [—|–|-])', r'', sentence)
        
        ad = ["Photo", "Newsletter Sign Up Continue reading the main story Please verify you're not a robot by clicking the box. Invalid email address. Please re-enter. You must select a newsletter to subscribe to. Sign Up You agree to receive occasional updates and special offers for The New York Times's products and services. Thank you for subscribing. An error has occurred. Please try again later. View all New York Times newsletters.", "Advertisement","Continue reading the main story"]
        for item in ad:
            sentence = sentence.replace(item.strip(),'')
        
        sentence = re.sub(r'(New York Times)[^ ]*', r'', sentence)
        
        
    # do a final search for outlet name and remove it
    return sentence




   
def remove_known_outlet_author_info(url, sentence, outlet_name, htmlbody):

    response = Selector(text=htmlbody)
    
    if outlet_name == 'The Hill':
        
        arr = []
        body = ""
        
        bset = response.xpath('//p//text()').extract()
        aset = response.xpath('//span//text()').extract()

        aset_discard = []
        for item in bset:
            if item in aset:
                try:
                    i = aset.index(item)
                    i+=1
                    tstr = ""
                    temp = []
                    if 'MORE' in aset[i:]:
                        while aset[i-1] != 'MORE':
                            temp.append(aset[i])
                            i+=1
                except:
                    continue
                
                aset_discard.append(tstr.join(temp))

        # print(aset_discard)

        for item in aset_discard:
            sentence = sentence.replace(item,'')
        
        # author name paragraph has <em> tag around
        author_name = response.xpath('//p//em//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')

        sentence = sentence.replace('ADVERTISEMENT','')

        # sentence = re.sub(r'[Tt][Hh][Ee] [Hh][Ii][Ll][Ll]', r'', sentence)
        
    elif outlet_name == 'CNN (Web News)':
        removals = []
        # <cite class="el-editorial-source">Washington (CNN)</cite>
        editorial_source = response.css("cite.el-editorial-source::text").extract()
        # <q class="el-editorial-note">Douglas Heye is a CNN political commentator and former deputy chief of staff to then-House Majority Leader Eric Cantor. The opinions expressed in this commentary are his own.</q></p></div><div class="el__leafmedia el__leafmedia--sourced-paragraph"><p class="zn-body__paragraph speakable"><cite class="el-editorial-source"> (CNN)</cite>
        editorial_note = response.css("q.el-editorial-note::text").extract()
        
        others = ["Read More"]
        
        removals.append(editorial_source)
        removals.append(editorial_note)
        removals.append(others)
        
        for lists in removals:
            for item in lists:
                sentence = sentence.replace(item.strip(),'')
                
                
        sentence = re.sub(r'(CNN)', r'', sentence)
        
        # CNN's Briana Keller - CNN's [A-Z] - capital letter means name
        # sentence = re.sub(r'[Cc][Nn][Nn]\'s( [A-Z][^ ]*)+', r'', sentence)
        # CNN poll
        # sentence = re.sub(r'CNN [Pp][Oo][Ll][Ll]', r'', sentence)
        # self quote
        # sentence = re.sub(r'[Cc][Nn][Nn][^ ]*', r'', sentence)
        
    elif outlet_name == 'Politico':   
        removals = []
        #advertisement in the middle, the other news urls doesn't stick-out
        source_adv = response.css('aside.story-related p::text').extract()
        ###print(source_adv)
        #<p><i>Eric Wolff, Janosch Delcker, Kalina Oroschakoff and Anca Gurzu contributed to this report.</i></p>
        author = response.xpath('//p//i//text()').extract()
        
        removals.append(source_adv)
        removals.append(author)
        
        #for lists in removals:
        for item in source_adv:
            if item in sentence:
                sentence = sentence.replace(item,'')
        for item in author:
            sentence = sentence.replace(item,'')
                
        # sentence = re.sub(r'[Pp][Oo][Ll][Ii][Tt][Ii][Cc][Oo][^ ]*', r'', sentence)
        
    elif outlet_name == 'NPR News': 
        # CNN's Briana Keller - CNN's [A-Z] - capital letter means name
        # sentence = re.sub(r'[Nn][Pp][Rr]\'s( [A-Z][^ ]*)+', r'', sentence)
        # others
        # sentence = re.sub(r'[Nn][Pp][Rr] [Nn][Ee][Ww][Ss]', r'', sentence) # Didn't test this
        # sentence = re.sub(r'[Nn][Pp][Rr][^ ]*', r'', sentence)
        return sentence
    
    elif outlet_name == 'USA TODAY': 
        # <div class="article-print-url">Read or Share this story: http://usat.ly/1F7A4ox</div>
        share_text = response.css('div.article-print-url::text').extract()    # appears once
        
        for item in share_text:
            sentence = sentence.replace(item,'')
        
        # others
        # sentence = re.sub(r'[Uu][Ss][Aa] [Tt][Oo][Dd][Aa][Yy]', r'', sentence)
            
    elif outlet_name == 'Fox News':
        # author name paragraph has <i> tag around
        author_name = response.xpath('//p//i//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')
            
        adv = "Want FOX News First in your inbox every day? Sign up here."
        sentence = sentence.replace(adv,'')
        
        others = "Click here for more from"
        sentence = sentence.replace(others,'')
        
        # <em>[Watch Fox: </em><i><b>President Obama</b></i><em><b> </b>holds a press conference at the G20 Summit in St. Petersburg, Russia in the 9 a.m. ET hour]</em>
        sentence = re.sub(r'\[Watch Fox.*\]', r'', sentence)
        
        # others
        # Sky News - may be a division of fox news
        # sentence = re.sub(r'([Ff][Oo][Xx])|([Ss][Kk][Yy])( [Nn][Ee][Ww][Ss])?( Channel \(FNC\))*', r'', sentence)
    
    elif outlet_name == 'Washington Times':
        
        # <div class="bigtext"><p>DELAWARE, Ohio &mdash;
        ############ sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        
        # <p>&bull; <em>Wesley Pruden is editor emeritus of The Washington Times.</em></p>
        # author name paragraph has <em> tag around
        author_name = response.xpath('//p//em//text()').extract()
        for item in author_name:
            sentence = sentence.replace(item,'')
            
        # Special case
        if '•' in sentence:
            sentence = sentence[0:sentence.index('•')]
            
        # sentence = re.sub(r'(Washington)( Times)', r'', sentence)
            
    elif outlet_name == 'Townhall':
        # <p>DELAWARE, Ohio &mdash;
        ############## sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        # if '_' in sentence:
        #    sentence = sentence[0:sentence.index('_')]
            
        # sentence = re.sub(r'([Tt][Oo][Ww][Nn][Hh][Aa][Ll][Ll])[^ ]*', r'', sentence)
        
        return sentence
            
    # May need a lil work - in (Ariana Grande/The Washington Post) type thing
    elif outlet_name == 'Washington Post':
        # <p>DELAWARE, Ohio &mdash;
        ######## sentence = re.sub(r'^(.* [—|–])', r'', sentence)
        # if '_' in sentence:
        #     sentence = sentence[0:sentence.index('_')]
            
        # sentence = re.sub(r'(The )?(Washington)( Post)', r'', sentence)
        return sentence
        
    elif outlet_name == 'HuffPost':
        # <p>DELAWARE, Ohio &mdash;
        ######## sentence = re.sub(r'^(.* [—|–|-])', r'', sentence)
        # if '_' in sentence:
        #     sentence = sentence[0:sentence.index('_')]
        # author name paragraph has <em> tag around
        '''
        author_info = response.xpath('//p//em//text()').extract()
        for item in author_info:
            sentence = sentence.replace(item,'')
        '''
        # sentence = re.sub(r'(HuffPost)[^ ]*', r'', sentence)
        
        return sentence
        
    # Vox needs not to do anything
    elif outlet_name == 'Vox':
        # sentence = re.sub(r'(Vox)[^ ]*', r'', sentence)
        return sentence
    
    elif outlet_name == 'New York Times':
        arr = []
        body = ""
        try:
            flag = 0
        
            actual_body = response.css('p.story-body-text::text').extract()
            if len(actual_body)>1:
                for item in response.xpath('//p//text()').extract():
                    if sentence.startswith(item):
                        break
                    elif actual_body[0].startswith(item[0]) == True and flag == 0:
                        arr.append(item+"\n")
                        flag = 1
                        continue
                    elif flag != 1:
                        continue
                    arr.append(item+"\n")
        except IndexError:
            print("Index Exception")
        sentence = body.join(arr) + sentence
        
        # Now get rid of the extra things
        # <p>DELAWARE, Ohio &mdash;
        ######### sentence = re.sub(r'^(.* [—|–|-])', r'', sentence)
        
        ad = ["Photo", "Newsletter Sign Up Continue reading the main story Please verify you're not a robot by clicking the box. Invalid email address. Please re-enter. You must select a newsletter to subscribe to. Sign Up You agree to receive occasional updates and special offers for The New York Times's products and services. Thank you for subscribing. An error has occurred. Please try again later. View all New York Times newsletters.", "Advertisement","Continue reading the main story"]
        for item in ad:
            sentence = sentence.replace(item.strip(),'')
        
        # sentence = re.sub(r'(New York Times)[^ ]*', r'', sentence)
        
        
    # do a final search for outlet name and remove it
    return sentence
