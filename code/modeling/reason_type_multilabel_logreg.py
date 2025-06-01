
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import numpy as np

# === Load MTurk annotations ===
df = pd.read_csv("../../mturk_annotations_raw/Batch_3495104_batch_results_600 HITS.csv", encoding="ISO-8859-1")

# === Clean and parse reason codes ===
def parse_reason_codes(reason_str):
    if pd.isna(reason_str):
        return []
    items = reason_str.lower().replace("other", "7").split('|')
    codes = []
    for item in items:
        try:
            code = int(item.strip())
            if 0 <= code <= 7:
                codes.append(code)
        except ValueError:
            continue
    return list(set(codes))

df['parsed_reasons'] = df['Answer.reason[]'].apply(parse_reason_codes)

# === Map to bias type labels ===
def map_bias_types(codes):
    directional = any(code in [0, 1, 2] for code in codes)
    structural = any(code in [3, 4, 5] for code in codes)
    neutral_or_other = any(code in [6, 7] for code in codes)
    return pd.Series([int(directional), int(structural), int(neutral_or_other)])

df[['label_directional', 'label_structural', 'label_neutral_other']] = df['parsed_reasons'].apply(map_bias_types)

# === Clean and prepare inputs ===
df = df[df['Input.fullDoc'].notna() & (df['Input.fullDoc'].str.strip() != "")]
X = df['Input.fullDoc']
Y = df[['label_directional', 'label_structural', 'label_neutral_other']]

# === TF-IDF vectorization ===
vectorizer = TfidfVectorizer(max_features=1000)
X_tfidf = vectorizer.fit_transform(X)

# === Train-test split ===
X_train, X_test, Y_train, Y_test = train_test_split(X_tfidf, Y, test_size=0.2, random_state=42)

# === Train and evaluate one model per label ===
for label in Y.columns:
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, Y_train[label])
    preds = clf.predict(X_test)
    print(f"\n=== Classification Report for {label} ===")
    print(classification_report(Y_test[label], preds))
