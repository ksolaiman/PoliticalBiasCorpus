import csv


annotated_worker_response = '/Users/ksolaima/Documents/GitHub/PoliticalBiasCorpus/annotations_raw/Batch_3495104_600 HITS_raw-annotations-tagged_agreeing or conflicting with outlet label.csv' 
docid2SourceLabel = '/Users/ksolaima/Documents/GitHub/PoliticalBiasCorpus/docid2outletlabel_for_selected_300_articles.csv'

headers = ['docid', 'outletLabel']
selected_docs = []
selected_docs_center = []
selected_docs_wrong = []
selected_docs_disagreement = []

# Purpose:
# Identify which one's the workers agree on
    # Identify which one's out of those agree with outlet
    # Identify which one's seem 'Centered' to readers but are Left/Right from Outlet Label
# Identify which one's the workers do not agree on

with open(annotated_worker_response, newline='', encoding='ISO-8859-1') as f:
    reader = csv.DictReader(f)
    # print(reader.fieldnames)  # This will print all column headers

    for row in reader:
        goldLabel = row['outletLabel']
        workerLabelorNotAgreeing = row['agreeornot']            # L,R,C or X (if not agreeing)
        docid = row["docid"]
        
        # both goldLabel and workerLabel appears on same row, otherwise it's blank for both
        if not goldLabel.strip() or not workerLabelorNotAgreeing.strip():
            continue
        
        ### 🟢 Workers agreed and matched outlet bias
        # if item[43] == "Correct":
            # selected_docs.append(item[44])
        elif goldLabel == workerLabelorNotAgreeing:
            selected_docs.append(docid)

        ### 🟡 Workers agreed, but labeled article as Center, outlet was Left/Right
        # elif item[43] == "NotByCenter":
        #     selected_docs_center.append(item[44])
        elif goldLabel != 'Center' and  workerLabelorNotAgreeing == 'Center':
            selected_docs_center.append(docid)

        ### ❌ Workers agreed, but label conflicted with outlet bias
        elif  workerLabelorNotAgreeing != 'X' and goldLabel != workerLabelorNotAgreeing:
            selected_docs_wrong.append(docid)
        # else:
        #     selected_docs_wrong.append(item[44])

        ### ❌ ❌  workers disagreeed
        elif  workerLabelorNotAgreeing == 'X':
            selected_docs_disagreement.append(docid)
            
print(len(selected_docs_disagreement))

# with open('correct_docId.txt', 'w') as f:
#     for item in selected_docs:
#         f.write("%s\n" % item)
# with open('incorrect_center_docId.txt', 'w') as f:
#     for item in selected_docs_center:
#         f.write("%s\n" % item)
# with open('incorrect_docId.txt', 'w') as f:
#     for item in selected_docs_wrong:
#         f.write("%s\n" % item)