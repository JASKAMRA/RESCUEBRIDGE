from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize database with pets table
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create pets table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            breed TEXT,
            age TEXT,
            color TEXT,
            vet TEXT,
            last_vet_visit DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users("Email Address")
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

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
                session['user_email'] = email  # Store user email in session
                session['user_role'] = 'user'
                return redirect(url_for('dashboard_user'))
            else:
                flash("Invalid credentials for Individual user")
                return redirect(url_for('login'))

        elif role == 'ngo':
            cursor.execute('SELECT * FROM ngos WHERE "Email"=? AND "Password"=?', (email, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                session['user_email'] = email
                session['user_role'] = 'ngo'
                return redirect(url_for('dashboard_ngo'))
            else:
                flash("Invalid credentials for NGO")
                return redirect(url_for('login'))

        elif role == 'shopkeeper':
            cursor.execute('SELECT * FROM shopkeepers WHERE "Email"=? AND "Password"=?', (email, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                session['user_email'] = email
                session['user_role'] = 'shopkeeper'
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
        
        session['user_email'] = email  # Store user email in session
        session['user_role'] = 'user'
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
        
        session['user_email'] = email
        session['user_role'] = 'ngo'
        return redirect(url_for('dashboard_ngo'))

    return render_template('signup_ngo.html')

@app.route('/user/donate')
def user_donate_with_ngos():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ngos")
    ngos = cursor.fetchall()
    conn.close()
    return render_template('user_donate.html', ngos=ngos)

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
        
        session['user_email'] = email
        session['user_role'] = 'shopkeeper'
        return redirect(url_for('dashboard_shopkeeper'))

    return render_template('signup_shopkeeper.html')

# ------------------- DASHBOARDS -------------------
@app.route('/dashboard/user')
def dashboard_user():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('dashboard_user.html')

@app.route('/dashboard/ngo')
def dashboard_ngo():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))
    return render_template('dashboard_ngo.html')

@app.route('/dashboard/shopkeeper')
def dashboard_shopkeeper():
    if 'user_email' not in session or session.get('user_role') != 'shopkeeper':
        return redirect(url_for('login'))
    return render_template('dashboard_shopkeeper.html')

# ------------------- USER SUBPAGES -------------------
@app.route('/user/report-animal')
def user_report_animal():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('user_report_animal.html')

@app.route('/user/your-pets')
def user_your_pets():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('user_Your_pets.html')

# API endpoint to get user's pets
@app.route('/api/pets', methods=['GET'])
def get_user_pets():
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_email = session['user_email']
    
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pets WHERE user_email = ? ORDER BY created_at DESC', (user_email,))
        pets = cursor.fetchall()
        
        # Convert rows to dictionaries
        pets_list = []
        for pet in pets:
            pets_list.append({
                'id': pet['id'],
                'name': pet['name'] or '',
                'type': pet['type'] or '',
                'breed': pet['breed'] or '',
                'age': pet['age'] or '',
                'color': pet['color'] or '',
                'vet': pet['vet'] or '',
                'lastVet': pet['last_vet_visit'] or ''
            })
        
        return jsonify(pets_list)
        
    except Exception as e:
        print(f"Error fetching pets: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to add a new pet
@app.route('/api/pets', methods=['POST'])
def add_pet():
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_email = session['user_email']
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('type'):
        return jsonify({'error': 'Pet name and type are required'}), 400
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pets (user_email, name, type, breed, age, color, vet, last_vet_visit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_email,
            data.get('name', ''),
            data.get('type', ''),
            data.get('breed', ''),
            data.get('age', ''),
            data.get('color', ''),
            data.get('vet', ''),
            data.get('lastVet', '')
        ))
        
        pet_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'success': True, 'id': pet_id})
        
    except Exception as e:
        print(f"Error adding pet: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to delete a pet
@app.route('/api/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_email = session['user_email']
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        # Only allow deletion of pets belonging to the current user
        cursor.execute('DELETE FROM pets WHERE id = ? AND user_email = ?', (pet_id, user_email))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Pet not found or access denied'}), 404
            
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error deleting pet: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/user/donate')
def user_donate():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('user_donate.html')

@app.route('/user/find-vet')
def user_find_vet():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('user_find_vet.html')

@app.route('/submit-donation', methods=['POST'])
def submit_donation():
    try:
        data = request.get_json()
        print("Received donation data:", data)

        conn = sqlite3.connect('donations.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO donations (
            name, email, phone, amount, purpose,
            recipient, payment_method, anonymous, date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['email'],
        data['phone'],
        data['amount'],
        data['purpose'],
        data['recipient'],
        data['paymentMethod'],
        int(data['anonymous']),
        data['date'],
        data['status']
))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Donation recorded successfully!"})
    
    except Exception as e:
         import traceback
         traceback.print_exc()
         return jsonify({"success": False, "message": "Something went wrong"}), 500

# ------------------- LOGOUT -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ------------------- NGO SUBPAGES -------------------
@app.route('/submit-animal-report', methods=['POST'])
def submit_animal_report():
    try:
        location = request.form['location']
        city = request.form['city']
        landmarks = request.form.get('landmarks', '')
        animal_type = request.form['animalType']
        condition = request.form['condition']
        description = request.form.get('description', '')
        phone = request.form['phone']
        name = request.form['name']
        date = request.form['date']

        # Step 1: Save report
        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reported_animals (
                location, city, landmarks, animal_type,
                condition, description, phone, name, date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            location, city, landmarks, animal_type,
            condition, description, phone, name, date, 'Submitted'
        ))
        report_id = cursor.lastrowid

        # Step 2: Save all uploaded images
        uploaded_files = request.files.getlist('photos')  # 👈 Not request.files['photo']
        for file in uploaded_files:
            if file and file.filename:
                image_data = file.read()
                cursor.execute('''
                INSERT INTO animal_images (report_id, image)
                VALUES (?, ?)
                ''', (report_id, image_data))


        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Report with multiple images saved to DB'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error saving report'}), 500


@app.route('/ngo/marketplace')
def ngo_marketplace():
    return render_template('ngo_marketplace.html')

@app.route('/ngo/medicine-planner')
def adherence_planner():
    return render_template('adherence_planner.html')

@app.route('/ngo/my_purchases')
def ngo_my_purchases():
    return render_template('my_purchases.html')

@app.route('/ngo/dailydoses')
def dailydoses():
    return render_template('dailydoses.html')

@app.route('/shopkeeper/medicine-planner')
def medicine_planner():
    return render_template('shopkeeper_list_medication.html')

@app.route('/shopkeeper/request-planner')
def request_planner():
    return render_template('shopkeeper_list_requests.html')

@app.route('/ngo/donation-records')
def ngo_donation():
    ngo_name = session.get("username", "").strip().lower()

    conn = sqlite3.connect("donations.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM donations")
    all_donations = cur.fetchall()
    conn.close()

    filtered_donations = [
        dict(row) for row in all_donations
        if row["recipient"].strip().lower() == ngo_name
    ]

    return render_template("ngo_donation.html", donations=filtered_donations)

@app.route('/animal-image/<int:image_id>')
def get_animal_image(image_id):
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM animal_images WHERE id = ?", (image_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return result[0], 200, {'Content-Type': 'image/jpeg'}
    else:
        return '', 404


# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)