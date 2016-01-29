from flask import (render_template, redirect, url_for)
from flask import session
from flask_login import (login_required, logout_user)

from app.main import main


@main.route('/sign-out', methods=(['GET']))
@login_required
def sign_out():
    if session.get('service_name', None):
        session.pop('service_name')
    logout_user()
    return redirect(url_for('main.index'))
