from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score, f1_score
import pandas as pd
import matplotlib.pyplot as plt
import os


output_dir = '../gold/'

# Output file paths
df1 = pd.read_csv(os.path.join(output_dir, 'gold_docs_workers_agreed_and_matched_outlet.csv'))
df2 = pd.read_csv(os.path.join(output_dir, 'gold_docs_workers_agreed_labeled_center_conflicted_with_outlet_lr.csv'))
df3 = pd.read_csv(os.path.join(output_dir, 'gold_docs_workers_agreed_conflicted_with_outlet.csv'))

df_all = pd.concat([df1, df2, df3], ignore_index=True)

# Compute metrics
y_true = df_all['outlet_bias']
y_pred = df_all['human_label']


print("Accuracy: "  + str(accuracy_score(y_true, y_pred)))
print("Micro F1: "  + str(f1_score(y_true, y_pred, average='micro')))
print("Macro F1: "  + str(f1_score(y_true, y_pred, average='macro')))
print("Weighted F1: "  + str(f1_score(y_true, y_pred, average='weighted')))

report = classification_report(y_true, y_pred, labels=['Left', 'Right', 'Center'], output_dict=True)
report_df = pd.DataFrame(report).transpose()

cm = confusion_matrix(y_true, y_pred, labels=['Left', 'Right', 'Center'])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Left', 'Right', 'Center'])
disp.plot(cmap='Blues', values_format='d')
plt.title("Confusion Matrix: Human Label vs Outlet Bias (270 Docs)")
plt.grid(False)
plt.tight_layout()
plt.show()


# Result:
# Accuracy: 0.5333333333333333
# Micro F1: 0.5333333333333333
# Macro F1: 0.40972222222222215
# Weighted F1: 0.6157921810699588