import os

from flask import current_app, redirect, render_template, request, session, url_for

from models import Application, Drive, Student, db


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

    existing_application = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if not existing_application:
        application = Application(student_id=student.id, drive_id=drive.id, status='Applied')
        db.session.add(application)
        db.session.commit()

    return redirect(url_for('dashboard'))


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
            resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)
            student.resume = f"uploads/resumes/{filename}"

        db.session.commit()
        return redirect(url_for('student_profile'))

    return render_template('student_profile.html', student=student)
