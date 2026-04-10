from sqlalchemy import or_

from flask import redirect, render_template, request, session, url_for

from models import Application, Company, Drive, Student, db


def _require_admin():
    if session.get('user_role') != 'admin':
        return False

    admin_user = Student.query.get(session.get('user_id'))
    return bool(admin_user and admin_user.role == 'admin')


def approve_company(company_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    company = Company.query.get_or_404(company_id)
    company.approved = True
    company.blacklisted = False
    db.session.commit()
    return redirect(url_for('dashboard'))


def reject_company(company_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    company = Company.query.get_or_404(company_id)
    company.blacklisted = True
    db.session.commit()
    return redirect(url_for('dashboard'))


def approve_drive(drive_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    return redirect(url_for('dashboard'))


def reject_drive(drive_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('dashboard'))


def view_all_drives():
    if not _require_admin():
        return redirect(url_for('login_route'))

    drives = Drive.query.order_by(Drive.created_at.desc()).all()
    return render_template('admin_drives.html', drives=drives)


def view_all_applications():
    if not _require_admin():
        return redirect(url_for('login_route'))

    applications = Application.query.order_by(Application.applied_date.desc()).all()
    return render_template('admin_applications.html', applications=applications)


def search_students():
    if not _require_admin():
        return redirect(url_for('login_route'))

    query = request.args.get('q', '').strip()
    students_query = Student.query.filter(Student.role == 'student')

    if query:
        filters = [
            Student.name.ilike(f'%{query}%'),
            Student.email.ilike(f'%{query}%'),
            Student.phone.ilike(f'%{query}%'),
        ]
        if query.isdigit():
            filters.append(Student.id == int(query))
        students_query = students_query.filter(or_(*filters))

    students = students_query.order_by(Student.id.asc()).all()
    return render_template('admin_students.html', students=students, query=query)


def search_companies():
    if not _require_admin():
        return redirect(url_for('login_route'))

    query = request.args.get('q', '').strip()
    companies_query = Company.query

    if query:
        companies_query = companies_query.filter(Company.name.ilike(f'%{query}%'))

    companies = companies_query.order_by(Company.id.asc()).all()
    return render_template('admin_companies.html', companies=companies, query=query)


def toggle_student_status(student_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    student = Student.query.get_or_404(student_id)
    if student.role == 'admin':
        return redirect(url_for('admin_students'))

    student.blacklisted = not student.blacklisted
    db.session.commit()
    return redirect(url_for('admin_students'))


def toggle_company_status(company_id):
    if not _require_admin():
        return redirect(url_for('login_route'))

    company = Company.query.get_or_404(company_id)
    company.blacklisted = not company.blacklisted
    db.session.commit()
    return redirect(url_for('admin_companies'))
