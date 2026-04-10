from models import Student, db
from main_app import app

#with app.app_context():
#    user = Student(name="sahil", email="sahil@gmail.com", password="12345" , role="student")
#    db.session.add(user)
#    db.session.commit()
#
#    print("User added!")

from main_app import app
from models import db, Student

with app.app_context():
    # check if admin already exists
    existing = Student.query.filter_by(email="admin@gmail.com").first()

    if not existing:
        admin = Student(
            name="Admin",
            email="admin@gmail.com",
            password="admin123",
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created")
    else:
        print("⚠️ Admin already exists")

    # check if student already exists
    existing = Student.query.filter_by(email="sahil@gmail.com").first()

    if not existing:
        db.session.add(Student(name="sahil", email="sahil@gmail.com", password="12345", role="student"))
        db.session.commit()
        print("✅ Student created")
    else:
        print("Email already exists")