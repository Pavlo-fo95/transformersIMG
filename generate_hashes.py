from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

passwords = ["adminpass1", "adminpass2", "adminpass3", "adminpass4"]

for i, pw in enumerate(passwords, start=1):
    hash_pw = pwd_context.hash(pw)
    print(f"-- admin{i}:", hash_pw)
