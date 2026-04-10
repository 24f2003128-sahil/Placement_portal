from flask import redirect, render_template, request, session, url_for

from models import Application, Company, Drive, db


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
            status='Pending',
        )
        db.session.add(drive)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('create_drive.html')


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


def delete_drive(drive_id):
    if session.get('user_role') != 'company':
        return redirect(url_for('login_route'))

    drive = Drive.query.get_or_404(drive_id)

    db.session.delete(drive)
    db.session.commit()

    return redirect(url_for('dashboard'))



def close_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.status = "Closed"
    db.session.commit()

    return redirect(url_for('dashboard'))













    applications = (
        Application.query.filter_by(drive_id=drive.id)
        .order_by(Application.applied_date.desc())
        .all()
    )
    return render_template('view_applications.html', drive=drive, applications=applications)
