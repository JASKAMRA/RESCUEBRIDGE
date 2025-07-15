from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Login Page
@app.route('/login')
def login():
    return render_template('login.html')

# Signup Pages
@app.route('/signup/user')
def signup_user():
    return render_template('signup_user.html')

@app.route('/signup/shopkeeper')
def signup_shopkeeper():
    return render_template('signup_shopkeeper.html')

@app.route('/signup/ngo')
def signup_ngo():
    return render_template('signup_ngo.html')

# Dashboard example for user (can be separate for each role)
@app.route('/dashboard/user')
def dashboard_user():
    return render_template('dashboard_user.html')

# You can add POST handling or DB integration later
# Example form handling (stub)
@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    # You can access form data like:
    # name = request.form['name']
    return redirect(url_for('dashboard_user'))

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
