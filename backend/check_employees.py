import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path to import models if needed, 
# but for simple check we can use raw SQL or just setup basic connection
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal

def check_employees():
    db = SessionLocal()

    try:
        print("Checking employees table...")
        result = db.execute(text("SELECT * FROM employees"))
        employees = result.fetchall()
        
        print(f"Found {len(employees)} employees:")
        for emp in employees:
            print(f"ID: {emp.employee_id}, No: {emp.employee_no}, Name: {emp.name}, Active: {emp.is_active}")
            
        print("\nChecking specifically for 'admin':")
        admin_result = db.execute(text("SELECT * FROM employees WHERE employee_no = 'admin' OR name = 'admin'"))
        admins = admin_result.fetchall()
        if admins:
            for admin in admins:
                print(f"Found admin match: ID: {admin.employee_id}, No: {admin.employee_no}, Name: {admin.name}")
        else:
            print("No employee found with employee_no='admin' or name='admin'")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_employees()
