from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
@app.route('/user/donate')
def user_donate_with_ngos():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))

    user_email = session.get('user_email')

    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ngos")
    ngos = cursor.fetchall()
    conn.close()

    return render_template('user_donate.html', ngos=ngos, user_email=user_email)


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

    user_email = session['user_email']

    # 1. Stray reports this month
    conn1 = sqlite3.connect('reports.db')
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT COUNT(*) FROM reported_animals WHERE name = ?", (user_email,))
    stray_reports = cursor1.fetchone()[0]
    conn1.close()

    # 2. Your Registered Pets
    conn2 = sqlite3.connect('users.db')
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT COUNT(*) FROM pets WHERE user_email = ?", (user_email,))
    registered_pets = cursor2.fetchone()[0]
    conn2.close()

    # 3. Animals Helped (via Donations)
    conn3 = sqlite3.connect('donations.db')
    cursor3 = conn3.cursor()
    cursor3.execute("SELECT COUNT(*) FROM donations WHERE email = ?", (user_email,))
    animals_helped = cursor3.fetchone()[0]
    conn3.close()

    return render_template(
        'dashboard_user.html',
        stray_reports=stray_reports,
        registered_pets=registered_pets,
        animals_helped=animals_helped
    )

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

    user_name = session.get("user_email")  # Get name from session
    return render_template('user_report_animal.html', user_name=user_name)


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
    
    user_email = session.get('user_email')  # session se email lo
    return render_template('user_donate.html', user_email=user_email)


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
            data['recipient'],  # This should be NGO email now
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
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))
    return render_template('ngo_marketplace.html')

@app.route('/ngo/medicine-planner')
def adherence_planner():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))
    return render_template('adherence_planner.html')

@app.route('/ngo/my_purchases')
def ngo_my_purchases():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))
    return render_template('my_purchases.html')

@app.route('/ngo/dailydoses')
def dailydoses():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))
    return render_template('dailydoses.html')

@app.route('/shopkeeper/medicine-planner')
def medicine_planner():
    if 'user_email' not in session or session.get('user_role') != 'shopkeeper':
        return redirect(url_for('login'))
    return render_template('shopkeeper_list_medication.html')

@app.route('/shopkeeper/request-planner')
def request_planner():
    if 'user_email' not in session or session.get('user_role') != 'shopkeeper':
        return redirect(url_for('login'))
    return render_template('shopkeeper_list_requests.html')

# ------------------- FIXED NGO DONATION RECORDS -------------------
@app.route('/ngo/donation-records')
def ngo_donation():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return redirect(url_for('login'))

    from datetime import datetime, timedelta

    ngo_email = session['user_email']  # NGO's email from session

    # Step 1: Fetch NGO name from users.db
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('SELECT "NGO Name" FROM ngos WHERE "Email" = ?', (ngo_email,))
    ngo_result = cursor.fetchone()
    conn.close()

    if not ngo_result:
        flash("NGO not found.")
        return redirect(url_for('login'))

    ngo_name = ngo_result[0].strip().lower()

    # Step 2: Fetch all donations from donations.db for this NGO
    conn = sqlite3.connect("donations.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM donations
        WHERE LOWER(TRIM(recipient)) = ?
        ORDER BY date DESC
    ''', (ngo_name,))
    donations = cursor.fetchall()
    conn.close()

    # Step 3: Compute stats
    total_amount = 0
    week_amount = 0
    month_amount = 0
    donation_dates = []
    donations_list = []

    today = datetime.today()
    week_ago = today - timedelta(days=7)
    
    month_ago = today - timedelta(days=30)
    

    for row in donations:
        donation = dict(row)
        amount = float(donation.get('amount', 0))
        total_amount += amount
        

        # Parse and format donation date
        try:
            donation_date =datetime.strptime(donation['date'], '%m/%d/%Y, %I:%M:%S %p')
            donation['formatted_date'] = donation_date.strftime('%d %b %Y')
            donation_dates.append(donation_date)
           

            if donation_date >= week_ago:
                week_amount += amount
            if donation_date >= month_ago:
                month_amount += amount
        except:
            donation['formatted_date'] = donation.get('date', 'Unknown')

        # Add default values
        donation.setdefault('donor', donation.get('name', 'Anonymous'))
        donation.setdefault('phone', donation.get('phone', 'N/A'))
        donation.setdefault('amount', amount)
        donation.setdefault('purpose', donation.get('purpose', 'General'))
        donation.setdefault('status', donation.get('status', 'Completed'))
        donation.setdefault('method', donation.get('payment_method', 'Online'))

        donations_list.append(donation)

    # Average donation
    average_donation = round(total_amount / len(donations_list), 2) if donations_list else 0

    # Step 4: Render the template with all values
    return render_template(
        "ngo_donation.html",
        donations=donations_list,
        ngo_name=ngo_name.title(),
        total_amount=round(total_amount, 2),
        week_amount=round(week_amount, 2),
        month_amount=round(month_amount, 2),
        average_donation=average_donation
    )

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

@app.route('/user/users_chatbot.html')
def user_chatbot():
    if 'user_email' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))
    return render_template('users_chatbot.html')

@app.route("/api/chat", methods=["POST"])
def chat_api():
    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    user_message = data.get("message", "")

    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

        final_prompt = f"""
You are an AI assistant on the RescueBridge platform.

Site Features:
- Report Animal
- Manage Pets
- Donate to NGOs
- Find Vets

User asked: {user_message}
Please reply based on these features.
"""

        response = model.generate_content(final_prompt)

        if hasattr(response, "text") and response.text.strip():
            reply_text = response.text.strip()
        elif hasattr(response, "parts") and response.parts:
            reply_text = response.parts[0].text.strip()
        else:
            reply_text = "⚠️ No response from Gemini. Please try again."

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"error": f"Gemini error: {str(e)}"}), 500
    

# Add these routes to your app.py file

# Initialize NGO pets database on startup
def init_ngo_pets_db():
    conn = sqlite3.connect('ngo_pets.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ngo_pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ngo_email TEXT NOT NULL,
            name TEXT NOT NULL,
            breed TEXT NOT NULL,
            injury TEXT NOT NULL,
            medication TEXT NOT NULL,
            type TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            days_left INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ngo_email) REFERENCES ngos("Email")
        )
    ''')
    conn.commit()
    conn.close()

# Call this function after your existing init_db() call
init_ngo_pets_db()

# API endpoint to get NGO's pets
@app.route('/api/ngo-pets', methods=['GET'])
def get_ngo_pets():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 401
    
    ngo_email = session['user_email']
    
    try:
        conn = sqlite3.connect('ngo_pets.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ngo_pets WHERE ngo_email = ? ORDER BY created_at DESC', (ngo_email,))
        pets = cursor.fetchall()
        
        # Convert rows to dictionaries
        pets_list = []
        for pet in pets:
            pets_list.append({
                'id': pet['id'],
                'name': pet['name'],
                'breed': pet['breed'],
                'injury': pet['injury'],
                'medication': pet['medication'],
                'type': pet['type'],
                'dosage': pet['dosage'],
                'frequency': pet['frequency'],
                'daysLeft': pet['days_left']
            })
        
        return jsonify(pets_list)
        
    except Exception as e:
        print(f"Error fetching NGO pets: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to add a new pet for NGO
@app.route('/api/ngo-pets', methods=['POST'])
def add_ngo_pet():
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 401
    
    ngo_email = session['user_email']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'breed', 'injury', 'medication', 'type', 'dosage', 'frequency', 'daysLeft']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        conn = sqlite3.connect('ngo_pets.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ngo_pets (ngo_email, name, breed, injury, medication, type, dosage, frequency, days_left)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ngo_email,
            data['name'],
            data['breed'],
            data['injury'],
            data['medication'],
            data['type'],
            data['dosage'],
            data['frequency'],
            int(data['daysLeft'])
        ))
        
        pet_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'success': True, 'id': pet_id})
        
    except Exception as e:
        print(f"Error adding NGO pet: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to delete an NGO pet
@app.route('/api/ngo-pets/<int:pet_id>', methods=['DELETE'])
def delete_ngo_pet(pet_id):
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 401
    
    ngo_email = session['user_email']
    
    try:
        conn = sqlite3.connect('ngo_pets.db')
        cursor = conn.cursor()
        # Only allow deletion of pets belonging to the current NGO
        cursor.execute('DELETE FROM ngo_pets WHERE id = ? AND ngo_email = ?', (pet_id, ngo_email))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Pet not found or access denied'}), 404
            
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error deleting NGO pet: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to update pet days left (for tracking)
@app.route('/api/ngo-pets/<int:pet_id>/days', methods=['PUT'])
def update_pet_days(pet_id):
    if 'user_email' not in session or session.get('user_role') != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 401
    
    ngo_email = session['user_email']
    data = request.get_json()
    
    if 'daysLeft' not in data:
        return jsonify({'error': 'daysLeft is required'}), 400
    
    try:
        conn = sqlite3.connect('ngo_pets.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ngo_pets 
            SET days_left = ? 
            WHERE id = ? AND ngo_email = ?
        ''', (int(data['daysLeft']), pet_id, ngo_email))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Pet not found or access denied'}), 404
            
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating pet days: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/find-vet', methods=['GET'])
def find_vet_nearby():
    pincode = request.args.get('pincode')
    radius = request.args.get('radius')  # in meters
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not pincode or not radius:
        return jsonify({"error": "Missing pincode or radius"}), 400

    try:
        # Geocode API
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={pincode}&key={api_key}"
        geo_response = requests.get(geo_url).json()

        if geo_response['status'] != 'OK':
            return jsonify({"error": "Invalid pincode"}), 400

        location = geo_response['results'][0]['geometry']['location']
        lat, lng = location['lat'], location['lng']

        # Places API
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius={radius}&type=veterinary_care&key={api_key}"
        )
        places_response = requests.get(places_url).json()

        if places_response['status'] != 'OK':
            return jsonify({"error": "Failed to fetch places"}), 500

        vets = [
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "location": place.get("geometry", {}).get("location", {}),
                "place_id": place.get("place_id")
            }
            for place in places_response.get("results", [])
        ]

        return jsonify({"results": vets})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)