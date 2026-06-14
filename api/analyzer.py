import re

UPFRONT_PAYMENT = [
    r'registration fee', r'pay.*deposit', r'send.*money',
    r'upfront.*payment', r'processing fee', r'training fee'
]

URGENCY_WORDS = [
    r'urgent', r'immediately', r'limited seats',
    r'apply now', r'today only', r'last chance'
]

SUSPICIOUS_SALARY = [
    r'earn \d{4,}.*daily', r'\d+ lakh.*month',
    r'50000.*week', r'guaranteed income'
]

SUSPICIOUS_CONTACT = [
    r'whatsapp only', r'telegram only',
    r'contact on whatsapp', r'dm on telegram'
]

NO_COMPANY_PATTERNS = [
    r'our company', r'a reputed firm',
    r'confidential company', r'undisclosed company'
]

def check_patterns(text, patterns):
    text = text.lower()
    matched = []
    for pattern in patterns:
        if re.search(pattern, text):
            matched.append(pattern)
    return matched

def analyze_job_post(title, content):
    full_text = f"{title} {content}".lower()
    reasons = []
    score = 0

    # Check upfront payment
    if check_patterns(full_text, UPFRONT_PAYMENT):
        reasons.append("Upfront payment detected")
        score += 35

    # Check urgency
    if check_patterns(full_text, URGENCY_WORDS):
        reasons.append("Urgency language found")
        score += 20

    # Check suspicious salary
    if check_patterns(full_text, SUSPICIOUS_SALARY):
        reasons.append("Unrealistic salary mentioned")
        score += 20

    # Check suspicious contact
    if check_patterns(full_text, SUSPICIOUS_CONTACT):
        reasons.append("Contact via WhatsApp/Telegram only")
        score += 15

    # Check no company name
    if check_patterns(full_text, NO_COMPANY_PATTERNS):
        reasons.append("No legitimate company name")
        score += 10

    # Cap score at 100
    score = min(score, 100)

    # Determine risk level
    if score >= 70:
        risk = "High"
    elif score >= 40:
        risk = "Medium"
    else:
        risk = "Low"

    if not reasons:
        reasons.append("No suspicious patterns detected")

    return {
        "score": score,
        "risk": risk,
        "reasons": reasons
    }