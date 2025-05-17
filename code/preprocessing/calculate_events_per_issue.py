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
with open("../../docs/socially_filtered_filelist.pkl", "rb") as file:
    filelist = pickle.load(file)

import xml.etree.ElementTree as ET
tree = ET.parse('../../docs/metadata/article_metadata.xml')
root = tree.getroot()


etree = ET.parse('../../docs/metadata/event_metadata.xml')
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

# print(issuelist)
print("Total issues in full dataset: " + str(sum(issuelist.values())))

print(eventDetails)
