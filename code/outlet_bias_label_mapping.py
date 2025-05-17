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

selected_docs = []
with open("../docs/outlet_derived_labels/selected_article_file_v2_900.txt", "r") as file:                     # this file has all 900 articles, 
                                                                            # below cleaned up the comment/<> lines i inserted in this file
    doclist = file.readlines()
    doclist = [item.strip(" !\n") for item in doclist if item.strip() != "" and item[0] != "<"]
    
    for doc in doclist:
        selected_docs.append(doc)

docid2SourceLabel = '../gold/docid2outletlabel_900.csv'                      # created the outlet labels for the 300 docs
import csv

headers = ['docid', 'finerLabel', 'outletLabel']
mydata = []
mydata.append(headers)

for doc in selected_docs:
            if docDetails[doc]['bias'] == 'Lean Left' or docDetails[doc]['bias'] == 'Left':
                label = 'Left'
            elif docDetails[doc]['bias'] == 'Lean Right' or docDetails[doc]['bias'] == 'Right':
                label = 'Right'
            else:
                print('problem')
            mydata.append([doc, docDetails[doc]['bias'], label])

# print(mydata)
with open(docid2SourceLabel, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(mydata)

# to access just first 300
# mydata[0:301]


#### To match the MTurk annotation results id orders, we can use the code below instead going through all the docids in 
# selected_article_file_v2.txt. 
#
# filename = '/Users/ksolaima/Documents/GitHub/PoliticalBiasCorpus/annotations_raw/Batch_3495104_600 HITS_raw-annotations-tagged_agreeing or conflicting with outlet label.csv' 
# with open(filename, newline='', encoding='ISO-8859-1') as f:
#     reader = csv.reader(f)
#     i = 0 
#     for item in reader:
#         if i == 0:
#             i+=1
#             continue
#         if i%2 != 0:
#             if docDetails[item[27]]['bias'] == 'Lean Left' or docDetails[item[27]]['bias'] == 'Left':
#                 label = 'Left'
#             elif docDetails[item[27]]['bias'] == 'Lean Right' or docDetails[item[27]]['bias'] == 'Right':
#                 label = 'Right'
#             else:
#                 print('problem')
#             mydata.append([item[27], label])
#         else:
#             mydata.append([item[27], ''])
#         i+=1
        