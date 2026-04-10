


from flask import render_template, request, redirect, session, url_for
from models import Student, Company, db


def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        student = Student.query.filter_by(email=email).first()
        if student and student.password == password:
            if student.blacklisted:
                return render_template('login.html', error='Account blocked. Contact admin.')
            session.clear()
            session['user_id'] = student.id
            session['user_role'] = student.role if student.role == 'admin' else 'student'
            return redirect(url_for('dashboard'))

        company = Company.query.filter_by(email=email).first()
        if company and company.password == password:
            if company.blacklisted:
                return render_template('login.html', error='Company blocked. Contact admin.')
            if not company.approved:
                return render_template('login.html', error='Company not approved by admin yet.')
            session.clear()
            session['company_id'] = company.id
            session['user_role'] = 'company'
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')


def logout():
    session.clear()
    return redirect(url_for('login_route'))


def register_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')

        if Student.query.filter_by(email=email).first() or Company.query.filter_by(email=email).first():
            return render_template('register_student.html', error='Email already registered.')

        student = Student(name=name, email=email, password=password, phone=phone, role='student')
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('login_route'))

    return render_template('register_student.html')


def register_company():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        description = request.form.get('description')

        if Company.query.filter_by(email=email).first() or Student.query.filter_by(email=email).first():
            return render_template('register_company.html', error='Email already registered.')

        company = Company(
            name=name,
            email=email,
            password=password,
            hr_contact=hr_contact,
            website=website,
            description=description,
            approved=False,
        )
        db.session.add(company)
        db.session.commit()
        return redirect(url_for('login_route'))

    return render_template('register_company.html')
