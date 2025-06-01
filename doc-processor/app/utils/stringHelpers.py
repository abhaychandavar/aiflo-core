import secrets
import string

def generate_password(length=16):
    if length < 12:
        raise ValueError("Password should be at least 12 characters for security.")

    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

__all__ = ['generate_password']