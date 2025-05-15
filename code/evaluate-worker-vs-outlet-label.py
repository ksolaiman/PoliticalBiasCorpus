from sklearn import metrics
import csv


filename = '/Users/ksolaima/Downloads/BiasLab/datasets/MTurk Labelling/annotation/work/bias-HITS-results (worker selection + original bias tagging task)/main-HITs-result-and-gold-tagging/Batch_3495104_batch_results_600 HITS_manual annotation by me_agreeing or conflicting with outlet label.csv' 
filename2 = 'docid2outletlabel_for_selected_300_articles.csv'

predicted = []
test_target = []

i=0
with open(filename, newline='', encoding='ISO-8859-1') as f:
    reader = csv.reader(f)
    for item in reader:
        if i > 600:
            continue
        if i%2 != 0:
            # print(item[41], item[42], item[44])
            if item[44] == "acf1b79e-3649-4285-899c-a1e37018581a":
                i+=1
                continue
            if item[41] == "X" or item[41] == "Center":
                item[41] = "Incorrect"
                #i+=1
                #continue
            predicted.append(item[41])
            test_target.append(item[42])
        i+=1
    '''
        if item[43] == "Correct":
            selected_docs.append(item[44])
        elif item[43] == "NotByCenter":
            selected_docs_center.append(item[44])
        else:
            selected_docs_wrong.append(item[44])
    '''
            

print(metrics.accuracy_score(test_target, predicted))

print(metrics.classification_report(test_target, predicted))

print(metrics.confusion_matrix(test_target, predicted))

print(metrics.f1_score(test_target, predicted, average='micro'))
print(metrics.f1_score(test_target, predicted, average='macro'))
print(metrics.f1_score(test_target, predicted, average='weighted'))