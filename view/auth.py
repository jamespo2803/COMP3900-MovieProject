from flask import Blueprint, redirect, render_template, flash, request, session, url_for
from flask_login import login_required, logout_user, current_user, login_user
from view.forms import LoginForm, SignupForm
from view import login_manager
from db.db import is_existing_account, create_connection, create_account, get_account, get_email_account


auth_bp = Blueprint('auth_bp',__name__)

#User sign-up page
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        conn = create_connection("db/movies.db")
        existing_user = is_existing_account(conn, email=form.email.data)
        if existing_user == False:
            user = create_account(conn, form.name.data, form.password.data, form.email.data)
            
            login_user(user)  # Log in as newly created user
            session['userid'] = userid=current_user.id
            conn.close
            return redirect(url_for('routes_bp.home'))
        conn.close
        flash('A user already exists with that email address.')
    return render_template(
        'pages/signup.html',
        title='Create an Account.',
        form=form,
        template='signup-page',
        body="Sign up for a user account."
    )

#Log-in page for registered users
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('routes_bp.home'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        conn = create_connection("db/movies.db")
        if not is_existing_account(conn, email=form.email.data):
            flash('No account is registered with that email')
            return redirect(url_for('auth_bp.login'))
        
        user = get_email_account(conn, form.email.data)
        conn.close
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('routes_bp.home'))
        flash('Invalid email/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(
        'pages/login.html',
        form=form,
        title='Log in.',
        template='login-page',
        body="Log in with your User account."
    )

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    current_user.authenticated = False
    logout_user()
    return redirect(url_for('routes_bp.home'))

@login_manager.user_loader
def load_user(user_id):
    #Check if user is logged-in on every page load
    if user_id is not None:
        return get_account(create_connection("db/movies.db"), user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    #Redirect unauthorized users to Login page
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))
