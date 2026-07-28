import re

PATRON_EMAIL = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")

def formato_email_valido(email: str) -> bool:
    return bool(PATRON_EMAIL.match(email.strip().lower()))