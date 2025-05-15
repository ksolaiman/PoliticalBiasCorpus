import csv


filename = '/Users/ksolaima/Downloads/BiasLab/datasets/MTurk Labelling/annotation/work/bias-HITS-results (worker selection + original bias tagging task)/main-HITs-result-and-gold-tagging/Batch_3495104_batch_results_600 HITS_manual annotation by me_agreeing or conflicting with outlet label.csv' 
filename2 = 'docid2outletlabel_for_selected_300_articles.csv'

headers = ['docid', 'outletLabel']
selected_docs = []
selected_docs_center = []
selected_docs_wrong = []

with open(filename, newline='', encoding='ISO-8859-1') as f:
    reader = csv.reader(f)
    # for row in reader:
    i = 0
    for item in reader:
        if item[43] == "Correct":
            selected_docs.append(item[44])
        elif item[43] == "NotByCenter":
            selected_docs_center.append(item[44])
        else:
            selected_docs_wrong.append(item[44])
            
print(i)

# with open('correct_docId.txt', 'w') as f:
#     for item in selected_docs:
#         f.write("%s\n" % item)
# with open('incorrect_center_docId.txt', 'w') as f:
#     for item in selected_docs_center:
#         f.write("%s\n" % item)
# with open('incorrect_docId.txt', 'w') as f:
#     for item in selected_docs_wrong:
#         f.write("%s\n" % item)