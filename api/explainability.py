import numpy as np
from .ml_analyzer import model, vectorizer, clean_text

def get_top_contributing_words(title, content, top_n=5, min_score=0.01):
    full_text = f"{title} {content}"
    cleaned = clean_text(full_text)
    
    vectorized = vectorizer.transform([cleaned])
    feature_names = vectorizer.get_feature_names_out()
    coefficients = model.coef_[0]
    
    word_indices = vectorized.nonzero()[1]
    
    word_scores = []
    for idx in word_indices:
        word = feature_names[idx]
        tfidf_value = vectorized[0, idx]
        weight = coefficients[idx]
        contribution = tfidf_value * weight
        word_scores.append((word, contribution))
    
    word_scores.sort(key=lambda x: x[1], reverse=True)
    
    top_scam_words = [w for w, score in word_scores if score > min_score][:top_n]
    
    return top_scam_words