from app.database import SessionLocal
from app.models.employee import Employee
from app.utils.auth import get_password_hash

def create_initial_user():
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.employee_no == "admin").first()

        if not employee:
            employee = Employee(
                employee_no="admin",
                name="Administrator",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                user="system"
            )
            db.add(employee)
            print("Created admin user with password 'admin123'")
        else:
            employee.password_hash = get_password_hash("admin123")
            print("Updated admin user password to 'admin123'")

        db.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_user()
