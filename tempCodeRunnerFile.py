from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'


# ------------------- HOME -------------------
@app.route('/')
def index():
    return render_template('index.html')


# ------------------- LOGIN -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        if role == 'user':
            cursor.execute('SELECT * FROM users WHERE "Email Address"=? AND "Password"=?', (email, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                return redirect(url_for('dashboard_user'))
            else:
                flash("Invalid credentials for Individual user")
                return redirect(url_for('login'))

        elif role == 'ngo':
            cursor.execute('SELECT * FROM ngos WHERE "Email"=? AND "Password"=?', (email, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                return redirect(url_for('dashboard_ngo'))
            else:
                flash("Invalid credentials for NGO")
                return redirect(url_for('login'))

        elif role == 'shopkeeper':
            cursor.execute('SELECT * FROM shopkeepers WHERE "Email"=? AND "Password"=?', (email, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                return redirect(url_for('dashboard_shopkeeper'))
            else:
                flash("Invalid credentials for Shopkeeper")
                return redirect(url_for('login'))

        else:
            flash("Invalid role selected")
            return redirect(url_for('login'))

    return render_template('login.html')


# ------------------- SIGNUP ROUTES -------------------
@app.route('/signup/user', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        data = request.form
        full_name = data['full_name']
        age = data['age']
        gender = data['gender']
        email = data['email']
        phone = data['phone']
        password = data['password']
        confirm_password = data['confirm_password']
        address = data['address']
        city = data['city']
        pincode = data['pincode']

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for('signup_user'))

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users ("Full Name", "Age", "Gender", "Email Address", "Phone Number", "Password", "Address", "City", "Pincode")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, age, gender, email, phone, password, address, city, pincode))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard_user'))

    return render_template('signup_user.html')


@app.route('/signup/ngo', methods=['GET', 'POST'])
def signup_ngo():
    if request.method == 'POST':
        data = request.form
        ngo_name = data['ngo_name']
        email = data['email']
        phone = data['phone']
        address = data['address']
        registration = data['registration_no']
        password = data['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ngos ("NGO Name", "Email", "Phone Number", "Address", "NGO Registration Number", "Password")
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ngo_name, email, phone, address, registration, password))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard_ngo'))

    return render_template('signup_ngo.html')


@app.route('/signup/shopkeeper', methods=['GET', 'POST'])
def signup_shopkeeper():
    if request.method == 'POST':
        data = request.form
        shop_name = data['shop_name']
        owner_name = data['owner_name']
        email = data['email']
        phone = data['phone']
        address = data['address']
        password = data['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shopkeepers ("Shop Name", "Owner Name", "Email", "Phone Number", "Shop Address", "Password")
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (shop_name, owner_name, email, phone, address, password))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard_shopkeeper'))

    return render_template('signup_shopkeeper.html')


# ------------------- DASHBOARDS -------------------
@app.route('/dashboard/user')
def dashboard_user():
    return render_template('dashboard_user.html')


@app.route('/dashboard/ngo')
def dashboard_ngo():
    return render_template('dashboard_ngo.html')


@app.route('/dashboard/shopkeeper')
def dashboard_shopkeeper():
    return render_template('dashboard_shopkeeper.html')


# ------------------- USER SUBPAGES -------------------
@app.route('/user/report-animal')
def user_report_animal():
    return render_template('user_report_animal.html')


@app.route('/user/your-pets')
def user_your_pets():
    return render_template('user_Your_pets.html')


@app.route('/user/donate')
def user_donate():
    return render_template('user_donate.html')


@app.route('/user/find-vet')
def user_find_vet():
    return render_template('user_find_vet.html')


# ------------------- NGO SUBPAGES -------------------
@app.route('/ngo/donation-records')
def ngo_donation():
    return render_template('ngo_donation.html')


@app.route('/ngo/marketplace')
def ngo_marketplace():
    return render_template('ngo_marketplace.html')


@app.route('/ngo/medicine-planner')
def adherence_planner():
    return render_template('adherence_planner.html')
@app.route('/ngo/my-purchases')
def ngo_my_purchases():
    return render_template('my_purchase.html')  # ✅ corrected filename



# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)
