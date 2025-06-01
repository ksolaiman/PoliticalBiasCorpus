
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

# === Load Data ===
matched_df = pd.read_csv("../../gold/gold_docs_workers_agreed_and_matched_outlet.csv")
conflicted_df = pd.read_csv("../../gold/gold_docs_workers_agreed_conflicted_with_outlet.csv")
center_conflicted_df = pd.read_csv("../../gold/gold_docs_workers_agreed_labeled_center_conflicted_with_outlet_lr.csv")

# === Label Data ===
matched_df['match'] = 1
conflicted_df['match'] = 0
center_conflicted_df['match'] = 0

# === Combine and Clean ===
df = pd.concat([matched_df, conflicted_df, center_conflicted_df], ignore_index=True)
df = df[df['full_text'].notna() & (df['full_text'].str.strip() != "")]
df = df[['full_text', 'match']].rename(columns={'full_text': 'text', 'match': 'label'})

# === Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['label'], test_size=0.2, random_state=42
)

# === TF-IDF Vectorization ===
tfidf = TfidfVectorizer(max_features=1000)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# === Train Logistic Regression Model ===
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_tfidf, y_train)

# === Evaluate Model ===
y_pred = clf.predict(X_test_tfidf)
report = classification_report(y_test, y_pred)
print("Classification Report:")
print(report)
