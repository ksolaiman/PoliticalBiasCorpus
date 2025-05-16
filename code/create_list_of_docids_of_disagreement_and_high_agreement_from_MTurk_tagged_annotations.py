import csv
import os


annotated_worker_response = '/Users/ksolaima/Documents/GitHub/PoliticalBiasCorpus/annotations_raw/Batch_3495104_600 HITS_raw-annotations-tagged_agreeing or conflicting with outlet label.csv' 
# docid2SourceLabel = '/Users/ksolaima/Documents/GitHub/PoliticalBiasCorpus/docid2outletlabel_for_selected_300_articles.csv'

# Output directory for gold label files
output_dir = '../gold/'
os.makedirs(output_dir, exist_ok=True)

# Output file paths
matched_file = os.path.join(output_dir, 'gold_docs_workers_agreed_and_matched_outlet.csv')
center_file = os.path.join(output_dir, 'gold_docs_workers_agreed_labeled_center_conflicted_with_outlet_lr.csv')
conflict_file = os.path.join(output_dir, 'gold_docs_workers_agreed_conflicted_with_outlet.csv')
disagree_file = os.path.join(output_dir, 'gold_docs_workers_disagreed.csv')

# list to save full information on the documents
matched_data = []
workers_agreed_conflicted_with_outlet_data = []
worker_tagged_center_data = []

# Lists to store docids
headers = ['docid', 'outletLabel']
selected_docs = []
selected_docs_center = []
selected_docs_wrong = []
selected_docs_disagreement = []

# Purpose:
# Identify which one's the workers agree on
    # Identify which one's out of those agree with outlet
    # Identify which one's seem 'Centered' to readers but are Left/Right from Outlet Label
# Identify which one's the workers do not agree on (L vs R)

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
            matched_data.append([
                docid,
                row['Input.title'],
                row['Input.event'],
                row['Input.fullDoc'],
                workerLabelorNotAgreeing,
                goldLabel
            ])

            
        ### 🟡 Workers agreed, but labeled article as Center, outlet was Left/Right
        # elif item[43] == "NotByCenter":
        #     selected_docs_center.append(item[44])
        elif goldLabel != 'Center' and  workerLabelorNotAgreeing == 'Center':
            selected_docs_center.append(docid)
            worker_tagged_center_data.append([
                docid,
                row['Input.title'],
                row['Input.event'],
                row['Input.fullDoc'],
                workerLabelorNotAgreeing,
                goldLabel
            ])

        ### ❌ Workers agreed, but label conflicted with outlet bias
        # else:
        #     selected_docs_wrong.append(item[44])
        elif  workerLabelorNotAgreeing != 'X' and goldLabel != workerLabelorNotAgreeing:
            selected_docs_wrong.append(docid)
            workers_agreed_conflicted_with_outlet_data.append([
                docid,
                row['Input.title'],
                row['Input.event'],
                row['Input.fullDoc'],
                workerLabelorNotAgreeing,
                goldLabel
            ])


        ### ❌ ❌  workers disagreeed
        elif  workerLabelorNotAgreeing == 'X':
            selected_docs_disagreement.append(docid)
            
print(len(selected_docs_disagreement))


# Save docid lists to files
def write_list_to_csv(path, docids):
    with open(path, 'w', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(['docid', 'title', 'event', 'full_text', 'human_label', 'outlet_bias'])
        for docid in docids:
            writer.writerow(docid)

# Write to output CSV
write_list_to_csv(matched_file, matched_data)
write_list_to_csv(center_file, worker_tagged_center_data)
write_list_to_csv(conflict_file, workers_agreed_conflicted_with_outlet_data)

# write_list_to_csv(disagree_file, selected_docs_disagreement)              # no need to save the worker conflicted one

# below code was used to just save the doc ids of different types
# with open('correct_docId.txt', 'w') as f:
#     for item in selected_docs:
#         f.write("%s\n" % item)
# with open('incorrect_center_docId.txt', 'w') as f:
#     for item in selected_docs_center:
#         f.write("%s\n" % item)
# with open('disagreement_docId.txt', 'w') as f:
#     for item in selected_docs_disagreement:
#         f.write("%s\n" % item)