import re
from .utils.email_extractor import extract_email, get_domain

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

COMMISSION_INCOME= [
    r'refer to a friend', r'share into your whatsapp group',
    r'add more of your friends'
]

FREE_TRAINING = [
    r'you will get paid after internship', r'you will learn with us',
    r'we will promote you'
]

REMOTE_WORK = [
    r'startup company', r'focused on future',
    r'you will get share'
]

REGISTRATION_FEES = [
    r'registration fee', r'application fee',
    r'processing fee', r'security deposit',
    r'pay.*before interview', r'interview fee'
]

WHATSAPP_TELEGRAM_SCAMS = [
    r'contact on whatsapp', r'message on whatsapp',
    r'join our telegram', r'telegram group',
    r'whatsapp recruiter', r'chat on telegram'
]

UNREALISTIC_SALARY = [
    r'earn.*per day', r'earn.*daily',
    r'guaranteed income', r'work.*2 hours.*day',
    r'earn.*without experience', r'high salary.*no experience'
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
    email = extract_email(content)
    domain = get_domain(email)

    print("Email:", email)
    print("Domain:", domain)
    
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
    
    if check_patterns(full_text, REGISTRATION_FEES):
        reasons.append("Registration/application fee detected")
        score += 40

    if check_patterns(full_text, WHATSAPP_TELEGRAM_SCAMS):
        reasons.append("Suspicious contact method detected")
        score += 15

    if check_patterns(full_text, UNREALISTIC_SALARY):
        reasons.append("Unrealistic salary promise detected")
        score += 25    

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
        "reasons": reasons,
        "email": email,
        "domain": domain
    }
    
