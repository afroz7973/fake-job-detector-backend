import re
import socket
import whois
from datetime import datetime, timezone

def extract_email_domain(content):
    email_pattern = r'[\w\.-]+@([\w\.-]+\.\w+)'
    match = re.search(email_pattern, content)
    return match.group(1) if match else None

def check_domain_exists(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def check_mx_records(domain):
    import dns.resolver
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except Exception:
        return False

def get_domain_age_days(domain):
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return None
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - creation_date).days
        return age
    except Exception:
        return None

def verify_company_domain(content):
    domain = extract_email_domain(content)
    
    if not domain:
        return {
            "domain_found": False,
            "trust_score": 0,
            "flags": ["No company email domain found in post"]
        }
    
    free_email_providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    flags = []
    trust_score = 50
    
    if domain.lower() in free_email_providers:
        flags.append(f"Uses free email provider ({domain}) instead of company domain")
        trust_score -= 30
    
    exists = check_domain_exists(domain)
    if not exists and domain.lower() not in free_email_providers:
        flags.append(f"Domain '{domain}' does not exist or is unreachable")
        trust_score -= 40
    
    has_mx = check_mx_records(domain)
    if not has_mx and domain.lower() not in free_email_providers:
        flags.append(f"Domain '{domain}' has no valid mail server records")
        trust_score -= 20
    
    age_days = get_domain_age_days(domain)
    if age_days is not None:
        if age_days < 90:
            flags.append(f"Domain registered only {age_days} days ago - very new")
            trust_score -= 30
        elif age_days < 365:
            flags.append(f"Domain registered {age_days} days ago - relatively new")
            trust_score -= 10
    
    trust_score = max(0, min(100, trust_score))
    
    if not flags:
        flags.append(f"Domain '{domain}' appears legitimate")
    
    return {
        "domain_found": True,
        "domain": domain,
        "trust_score": trust_score,
        "flags": flags
    }