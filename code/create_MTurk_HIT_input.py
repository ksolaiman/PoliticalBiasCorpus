#### Outlets by inherent bias

# Neutral - ABC News, BBC News, AP, 'Reuters',
# Left - 'HuffPost', Daily Kos, AlterNet, 'ThinkProgress', Democracy Now, Mother Jones, Jacobin
# Right - 'Fox News', 'Fox News Editorial', 'National Review', 'Breitbart News', 
# Infowars, The Daily Wire, Red State, 'Washington Times', (American Spectator)

Center = ['BBC News', 'Bloomberg', 'Business Insider', 'The Hill', 'USA TODAY', ]
Left = ['HuffPost', 'ThinkProgress',
        'MSNBC', 'New York Magazine', # 'New York Daily News', 
        'Daily Kos', 'AlterNet', 'Democracy Now', 'Mother Jones', 'Jacobin']
Right = ['Fox News', 'Fox News Editorial', 'National Review', 'Breitbart News', 'Washington Times', 
         'The Daily Caller',
        'InfoWars', 'The Daily Wire', 'Red State', 'American Spectator', 'TheBlaze.com']


import pickle
with open("../docs/socially_filtered_filelist.pkl", "rb") as file:
    filelist = pickle.load(file)

import xml.etree.ElementTree as ET
tree = ET.parse('../docs/metadata/article_metadata.xml')
root = tree.getroot()


etree = ET.parse('../docs/metadata/event_metadata.xml')
eroot = etree.getroot()


# Find all events and issues in dataset

eventDetails = {}
issuelist = {}
for event in eroot.iter("event"):
    eid = event.get("id")
    src = event.get("source")
    date = event.find("date-of-publication").text
    name = event.find("name").text
    num = int(event.find("no-articles").text)
    issue = event.find("type").text
    if issue not in issuelist:
        issuelist[issue] = 1
    else:
        issuelist[issue] += 1
    details = event.find("description").text
    eventDetails[eid] = {'eid':eid, 'src':src, 'date':date, 'name':name, 'noArticles':num, 
                         'details':details, 'issue':issue}
    

# Find all the documents for each event

docDetails = {}
for article in root.iter("article"):
    docId = article.get("id")
    dbId = article.get("database_id")
    title = article.find("title").text
    date = article.find("date-of-publication").text
    event  = article.find("event").text
    bias = article.find("news-source-bias").text
    outlet = article.find("news-source").text
    docDetails[docId] = {'docId':docId, 'title':title, 'date':date, 'event':event, 'bias':bias, 'outlet':outlet}
    if 'docs' not in eventDetails[event]:
        eventDetails[event]['docs'] = []
    if docId in filelist:
        if outlet in Left or outlet in Right:
            eventDetails[event]['docs'].append(docId)
    if 'refDocs' not in eventDetails[event]:
        eventDetails[event]['refDocs'] = {}
    if dbId is not None:
        eventDetails[event]['refDocs'][docId] = docDetails[docId]

#########


#### can ignore for now, as all 900 articles were already prepared
# count = 0
# a = []
# with open("selected_story_file_v2_414.txt", "r") as file: # huh, 414 curated stories
#     eventlist = file.readlines()
#     eventlist = [item.strip(" !\n") for item in eventlist if item.strip() != "" and item[0] != "<"]
    
#     for event in eventlist:
#         # a.append(eventDetails[event]['eid'])
#         if len(eventDetails[event]['docs']) == 0:
#             continue
#         # pp.pprint(eventDetails[event])
#         #count += 1 #eventDetails[event]['noArticles']
#         for item in eventDetails[event]['docs']:
#             if item not in selected_docs:# and item in eventDetails[event]['refDocs']:
#                 # print(eventDetails[event]['docs'])
#                 count += 1
#                 print(docDetails[item])
#         """
#         for item in eventDetails[event]['docs']:
#             if item not in selected_docs:
#                 print(docDetails[item]['title'])
#                 print(docDetails[item]['date'])
#                 print(docDetails[item]['outlet'])
#                 includeDoc = input("include Doc: ")
#                 #if includeDoc == 'y':
#                     #selected_docs.append(docDetails[item]['docId'])
#                     #with open("selected_article_file_v2.txt", "a+") as file:
#                     #    file.write(docDetails[item]['docId']) + file.write("\n")
#         """

# print(count)

# for item in selected_docs:
#     print(docDetails[item]['title'])


# Prepare data for the Bias Detection HIT (for all 900 curated articles)
selected_docs = []
with open("../docs/selected_article_file_v2_900.txt", "r") as file:                     # this file has all 900 articles, 
                                                                            # below cleaned up the comment/<> lines i inserted in this file
    doclist = file.readlines()
    doclist = [item.strip(" !\n") for item in doclist if item.strip() != "" and item[0] != "<"]
    
    for doc in doclist:
        # a.append(eventDetails[event]['eid'])
        selected_docs.append(doc)


# created the "MTurk HIT gold inputs" with (docid, title, snippet 1, snippet 2, snippet 3, fullDoc, event) for all 900 documents

headers = ['docid','title','snippet1','snippet2','snippet3','fullDoc','event']
mydata = []
mydata.append(headers)

special_chars = ['💔', '🇵' ,'🇷', '🍁', '🦅', '💯', '🙂', '🖊', '🗒', '🔴', '🏻', '🚨', '🤮']

for doc in selected_docs:
    docid = docDetails[doc]['docId']
    title = docDetails[doc]['title'] # delete thinkprogress title
    if '– ThinkProgress' in title:
        title = title.replace('– ThinkProgress', '')
    # Conservatives Seize On Report To Argue Obamacare Is A Job Killer — But The Author Says They’re Wrong – ThinkProgress
    with open("/Users/Salvi/perspective_compatibility/embeddings/docs/"+doc+".txt", "r") as file:
        full = file.read()
        for item in special_chars:
            if item in full:
                full = full.replace(item, "")
        
        para = full.split("\n\n")
        para = [item.strip() for item in para if item.strip()!='']
        if len(para)>=1:
            para0 = para[0].strip()
        if len(para)>=2:
            para1 = para[1].strip()
        else:
            para1 = 'None'
        if len(para)>=3:
            last_para = para[len(para)-1].strip()
        else:
            last_para = 'None'
        seperator = '</p> <p>'
        full_doc = '<p>' + seperator.join(para) + '</p>'
    event = eventDetails[docDetails[doc]['event']]['details']
    if event is None:
        event = eventDetails[docDetails[doc]['event']]['name']
        '''
        refDocs = eventDetails[docDetails[doc]['event']]['refDocs']
        for k, v in refDocs.items():
            if v['bias'] == 'Center': # change here, only include real 'center' articles, else keep it empty
                event = v['title']
        '''
        
    mydata.append([docid, title, para0, para1, last_para, full_doc, event])
    
    


# saved the "MTurk HIT gold inputs" with (docid, title, snippet 1, snippet 2, snippet 3, fullDoc, event)

import csv 

with open('../gold/HIT_inputs/mturk_input_300.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(mydata[0:301]) # Next should be 301 to 601
