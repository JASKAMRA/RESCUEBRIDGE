@app.route("/ngo/marketplace")
def ngo_marketplace():
    if "user_email" not in session:
        return redirect("/login")

    ngo_email = session["user_email"]

    # Connect to medicine.db and fetch shopkeeper medicines
    conn = sqlite3.connect("medicine.db")
    cursor = conn.cursor()
    cursor.execute("SELECT medicine_name, shopkeeper_email, price_per FROM medicines")
    all_medicines = cursor.fetchall()
    conn.close()
    products = []
    for i in all_medicines:
    # Connect to users.db to get NGO name
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT [Shop Name] FROM shopkeepers WHERE email = ?", (i[1],))
        ngo_name_result = cursor.fetchone()
        conn.close()

        shopkeeper_name = ngo_name_result[0] if ngo_name_result else "Unknown NGO"
        products.append({
                "name":i[0],
                "shopkeer_name": shopkeeper_name,
                "price": i[2],
                "category": "medicine",
                "image": "💊",
            })

        # Prepare product data
    return render_template("ngo_marketplace.html", products=products)