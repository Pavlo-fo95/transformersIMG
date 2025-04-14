from utils.security import hash_password

passwords = {
    "user123": "secret",
    "user2": "hello456",
    "user3": "qwerty789",
    "user4": "admin2025"
}

for username, plain_pw in passwords.items():
    hashed = hash_password(plain_pw)
    print(f"UPDATE users SET password_hash = '{hashed}' WHERE login = '{username}';")