from flask import Flask, render_template, request, redirect, url_for, session, flash

application = Flask(__name__)
application.secret_key = 'super-secret-key-change-in-production'

# Hardcoded credentials
USERS = {
    "admin": "password123",
    "user": "mypassword"
}


@application.route('/')
def index():
    return redirect(url_for('login'))


@application.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


@application.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])


@application.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)
