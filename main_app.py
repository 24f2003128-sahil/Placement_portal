from flask import Flask, render_template, request, redirect, session, url_for
from models import Student, Company, Drive, Application, db
import os

print('this app is running on port 5000')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'resumes')

db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if not Student.query.filter_by(email='admin@gmail.com').first():
        admin = Student(
            name='Admin',
            email='admin@gmail.com',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

    Student.query.filter(
        Student.email != 'admin@gmail.com',
        Student.role == 'admin'
    ).update({'role': 'student'}, synchronize_session=False)
    db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    from routes.auth import login
    return login()


@app.route('/logout')
def logout_route():
    from routes.auth import logout
    return logout()


@app.route('/register_student', methods=['GET', 'POST'])
def register_student_route():
    from routes.auth import register_student
    return register_student()


@app.route('/register_company', methods=['GET', 'POST'])
def register_company_route():
    from routes.auth import register_company
    return register_company()


@app.route('/dashboard')
def dashboard():
    if 'user_role' not in session:
        return redirect(url_for('login_route'))

    role = session['user_role']

    if role == 'admin':
        admin_user = Student.query.get(session.get('user_id'))
        if not admin_user or admin_user.role != 'admin':
            session.clear()
            return redirect(url_for('login_route'))

        total_students = Student.query.count()
        total_companies = Company.query.count()
        total_drives = Drive.query.count()
        total_applications = Application.query.count()
        pending_companies = Company.query.filter_by(approved=False, blacklisted=False).all()
        pending_drives = Drive.query.filter_by(status='Pending').all()

        return render_template(
            'admin_dashboard.html',
            total_students=total_students,
            total_companies=total_companies,
            total_drives=total_drives,
            total_applications=total_applications,
            pending_companies=pending_companies,
            pending_drives=pending_drives
        )

    elif role == 'company':
        company = Company.query.get(session['company_id'])
        drives = Drive.query.filter_by(company_id=company.id).all()
        return render_template('company_dashboard.html', company=company, drives=drives)

    else:
        student = Student.query.get(session.get('user_id'))
        if not student:
            session.clear()
            return redirect(url_for('login_route'))

        approved_drives = Drive.query.filter_by(status='Approved').all()
        applications = (
            Application.query.filter_by(student_id=student.id)
            .order_by(Application.applied_date.desc())
            .all()
        )
        applied_drive_ids = {application.drive_id for application in applications}
        past_placements = [application for application in applications if application.status == 'Placed']

        return render_template(
            'student_dashboard.html',
            student=student,
            approved_drives=approved_drives,
            applications=applications,
            applied_drive_ids=applied_drive_ids,
            past_placements=past_placements,
        )


@app.route('/apply_drive', methods=['POST'])
def apply_drive():
    if session.get('user_role') != 'student':
        return redirect(url_for('login_route'))

    student = Student.query.get(session.get('user_id'))
    if not student:
        session.clear()
        return redirect(url_for('login_route'))

    drive_id = request.form.get('drive_id', type=int)
    if not drive_id:
        return redirect(url_for('dashboard'))

    drive = Drive.query.filter_by(id=drive_id, status='Approved').first()
    if not drive:
        return redirect(url_for('dashboard'))

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()

    if not existing_application:
        application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status='Applied'
        )
        db.session.add(application)
        db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if session.get('user_role') != 'student':
        return redirect(url_for('login_route'))

    student = Student.query.get(session.get('user_id'))
    if not student:
        session.clear()
        return redirect(url_for('login_route'))

    if request.method == 'POST':
        student.name = request.form.get('name', student.name).strip() or student.name
        student.phone = request.form.get('phone', student.phone)

        resume = request.files.get('resume')
        if resume and resume.filename:
            filename = f"student_{student.id}_{os.path.basename(resume.filename)}"
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)
            student.resume = f"uploads/resumes/{filename}"

        db.session.commit()
        return redirect(url_for('student_profile'))

    return render_template('student_profile.html', student=student)


@app.route('/admin/company/<int:company_id>/approve')
def approve_company(company_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login_route'))

    company = Company.query.get_or_404(company_id)
    company.approved = True
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/admin/company/<int:company_id>/reject')
def reject_company(company_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login_route'))

    company = Company.query.get_or_404(company_id)
    company.blacklisted = True
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/admin/drive/<int:drive_id>/approve')
def approve_drive(drive_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login_route'))

    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/admin/drive/<int:drive_id>/reject')
def reject_drive(drive_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login_route'))

    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/create_drive', methods=['GET', 'POST'])
def create_drive():
    if session.get('user_role') != 'company':
        return redirect(url_for('login_route'))

    company = Company.query.get(session.get('company_id'))
    if not company:
        session.clear()
        return redirect(url_for('login_route'))

    if request.method == 'POST':
        drive = Drive(
            company_id=company.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            eligibility=request.form.get('eligibility'),
            deadline=request.form.get('deadline'),
            status='Pending'
        )
        db.session.add(drive)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('create_drive.html')

@app.route('/edit_drive/<int:drive_id>', methods=['GET', 'POST'])
def edit_drive(drive_id):
    if session.get('user_role') != 'company':
        return redirect(url_for('login_route'))

    company = Company.query.get(session.get('company_id'))
    if not company:
        session.clear()
        return redirect(url_for('login_route'))

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    if request.method == 'POST':
        drive.title = request.form.get('title')
        drive.description = request.form.get('description')
        drive.eligibility = request.form.get('eligibility')
        drive.deadline = request.form.get('deadline')
        drive.status = 'Pending'
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_drive.html', drive=drive)

@app.route('/close_drive/<int:drive_id>')
def close_drive(drive_id):
    from routes.company import close_drive
    return close_drive(drive_id)

@app.route('/delete_drive/<int:drive_id>')
def delete_drive(drive_id):
    from routes.company import delete_drive
    return delete_drive(drive_id)




@app.route('/view_applications/<int:drive_id>', methods=['GET', 'POST'])
def view_applications(drive_id):
    if session.get('user_role') != 'company':
        return redirect(url_for('login_route'))

    company = Company.query.get(session.get('company_id'))
    if not company:
        session.clear()
        return redirect(url_for('login_route'))

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    if request.method == 'POST':
        application_id = request.form.get('application_id', type=int)
        status = request.form.get('status')
        comments = request.form.get('comments')

        application = Application.query.filter_by(id=application_id, drive_id=drive.id).first_or_404()
        application.status = status
        application.comments = comments
        db.session.commit()
        return redirect(url_for('view_applications', drive_id=drive.id))

    applications = Application.query.filter_by(drive_id=drive.id).order_by(Application.applied_date.desc()).all()
    return render_template('view_applications.html', drive=drive, applications=applications)



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)













