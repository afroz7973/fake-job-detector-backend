import pandas as pd
import re
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# Load dataset
df = pd.read_csv("fake_job_postings.csv")

# Create text column
df['text'] = (
    df['title'].fillna('') + ' ' +
    df['company_profile'].fillna('') + ' ' +
    df['description'].fillna('') + ' ' +
    df['requirements'].fillna('') + ' ' +
    df['benefits'].fillna('')
)

# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

df['text'] = df['text'].apply(clean_text)

# Features and target
X = df['text']
y = df['fraudulent']

# TF-IDF
vectorizer = TfidfVectorizer(
    stop_words='english',
    max_features=5000
)
X_tfidf = vectorizer.fit_transform(X)

# Balance classes with SMOTE
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_tfidf, y)

# Train test split on balanced data
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced,
    y_balanced,
    test_size=0.2,
    random_state=42
)

# Train with class weight
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_train, y_train)

predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

os.makedirs('../ml/saved_models', exist_ok=True)
joblib.dump(model, '../ml/saved_models/scam_model.pkl')
joblib.dump(vectorizer, '../ml/saved_models/vectorizer.pkl')
print("Model saved successfully")