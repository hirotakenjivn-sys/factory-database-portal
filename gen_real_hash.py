from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
h = pwd_context.hash("admin123")
with open("hash_output.txt", "w") as f:
    f.write(h)
print("Done")
