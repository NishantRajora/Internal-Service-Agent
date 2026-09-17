import bcrypt

def hash_password(password: str):
    """
    Securely hash a password using bcrypt.
    """
    # Convert password to bytes
    pwd_bytes = password.encode('utf-8')
    # Generate salt and hash
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    # Return as a decoded string for easy storage in SQLite
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify a plain password against a hashed password.
    """
    try:
        # Convert both to bytes
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # Check if the password matches
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False
