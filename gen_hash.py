from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
hash_value = pwd_context.hash("admin123")
print(f"Password hash for 'admin123':")
print(hash_value)
print(f"\nSQL statement:")
print(f"INSERT INTO employees (employee_no, name, password_hash, is_active, user) VALUES ('admin', 'Administrator', '{hash_value}', TRUE, 'system');")
