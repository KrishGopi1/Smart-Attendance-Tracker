from app import create_app, db
from app.models import Student
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    students = []
    for i in range(1,1501):
        phone = f'+100000{10000 + i}'
        students.append(Student(name=f'Student {i}', roll=f'R{i:04d}', phone=phone, class_name='12A'))
    db.session.bulk_save_objects(students)
    db.session.commit()
    print('Seeded 1500 students')
