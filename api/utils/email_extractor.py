import re

def extract_email(text):
    emails = re.findall(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )

    return emails[0] if emails else None


def get_domain(email):
    if not email:
        return None

    return email.split("@")[1]