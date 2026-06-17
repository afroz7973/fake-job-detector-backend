import joblib
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '../ml/saved_models/scam_model.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, '../ml/saved_models/vectorizer.pkl')

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def ml_analyze(title, content):
    full_text = f"{title} {content}"
    cleaned = clean_text(full_text)
    vectorized = vectorizer.transform([cleaned])
    prediction = model.predict(vectorized)[0]
    probability = model.predict_proba(vectorized)[0]
    
    scam_probability = probability[1]
    score = int(scam_probability * 100)
    
    if score >= 70:
        risk = "High"
    elif score >= 40:
        risk = "Medium"
    else:
        risk = "Low"
    
    return {
        "score": score,
        "risk": risk,
        "reasons": [
            f"ML model confidence: {score}%",
            "Trained on 17,000+ real job postings"
        ],
        "method": "ml"
    }