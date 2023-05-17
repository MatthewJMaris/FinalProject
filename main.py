from flask import Flask, render_template, request, session, url_for, redirect, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, engine, and_
from datetime import datetime

app = Flask(__name__)
app.debug = True
app.secret_key = 'HashAPassword!123'

conn_str = "mysql://root:Lorx3492345!@localhost/companydb"
engine = create_engine(conn_str, echo=True)
connection = engine.connect()


def h(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum


@app.route('/')
def index():
    query = text('select * from Products')
    result = connection.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('customer.html', products=products)


@app.route('/in')
def ind():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Handles the login screen and will redirect you to the appropriate page
# If your account is either an Admin, Customer, or Vendor
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'placholder123!' or password == '!123placholder':
            password = password
        else:
            password = h(password)
        query = text("select * from users where username = :username and password = :password")
        params = {"username": username, "password": password}
        result = connection.execute(query, params)
        user = result.fetchone()
        if user is None:
            return render_template('index.html')
        else:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['full_name'] = user[3]
            session['acc_type'] = user[4]
            session['logged_in'] = True
        if user[4] == 'Admin':
            account = connection.execute("select user_id from users")
            return redirect(url_for('admin', account=account))
        elif user[4] == 'Vendor':
            account = connection.execute(text("select user_id from users"))
            return redirect(url_for('vendor', account=account))
        else:
            account = connection.execute(text("select user_id from users"))
            return redirect(url_for('customer', account=account))
    else:
        return render_template('index.html')


# This handles how you will register for the website
# Currently, you can only register as a 'Customer',
# Both the admins and vendors are hardcoded in the program.
@app.route('/register_account', methods=['POST'])
def registration_account():
    all_id_queries = text("select max(user_id) from users")
    all_id = connection.execute(all_id_queries).fetchone()[0]
    new_id = all_id + 1 if all_id is not None else 1

    username = request.form['username']
    email = request.form['email']
    full_name = request.form['full_name']
    password = request.form['password']
    password = h(password)
    acc_type = 'customer'
    user = connection.execute(text("select * from users where email= :email"), {'email': email}).fetchone()
    if user is not None:
        flash("An account with this email address already exists.")
        return redirect(url_for('register'))
    else:
        query = text("insert into users (user_id, username, email, full_name, password, acc_type) values (:user_id, "
                     ":username, :email, :full_name, :password, :acc_type)")
        params = {"user_id": new_id, "username": username, "email": email, "full_name": full_name, "password": password,
                  "acc_type": acc_type}

        connection.execute(query, params)
        connection.commit()
    return render_template('index.html')


# Handles where you will get registered when you
# Click 'Register Here!' on the main page.
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/admin')
def admin():
    query = text("select * from Products")
    result = connection.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('admin.html', products=products)


@app.route('/add_product', methods=['POST'])
def add_product():
    max_id_query = text("SELECT MAX(product_id) FROM Products")
    max_id = connection.execute(max_id_query).fetchone()[0]
    new_id = max_id + 1 if max_id is not None else 1

    vendor_id = request.form['vendor_id']
    title = request.form['title']
    description = request.form['description']
    image = request.form['image']
    colors = request.form['colors']
    sizes = request.form['sizes']
    stock_total = request.form['stock_total']
    price = request.form['price']

    query = text("INSERT INTO Products (product_id, vendor_id, title, description, image, colors, sizes,"
                 " price, stock_total)"
                 " VALUES (:item_id, :vendor_id, :title, :description, :image, :colors, :sizes, "
                 " :price, :stock)")
    params = {"item_id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "colors": colors, "sizes": sizes, 'stock_total': stock_total}
    connection.execute(query, params)
    connection.commit()

    return url_for('admin')


@app.route('/admin_delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    query = text("DELETE FROM Products WHERE product_id = :product_id")
    connection.execute(query, {"product_id": product_id})
    connection.commit()
    return redirect(url_for('admin'))


@app.route('/admin_edit_product/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        title = request.form['title']
        description = request.form['description']
        image = request.form['image']
        colors = request.form['colors']
        sizes = request.form['sizes']
        stock_total = request.form['stock_total']
        price = request.form['price']
        query = text(
            "UPDATE Products SET vendor_id=:vendor_id, title=:title, description=:description, price=:price, "
            "image=:image, colors=:colors, sizes=:sizes stock_total=:stock_total WHERE product_id=:product_id")
        params = {"vendor_id": vendor_id, "title": title, "description": description,
                  "price": price, "image": image, "colors": colors, "sizes": sizes, 'stock_total': stock_total,
                  'product_id': product_id}
        connection.execute(query, params)
        connection.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin'))
    else:
        query = text("SELECT * FROM Products WHERE product_id=:product_id")
        params = {"product_id": product_id}
        result = connection.execute(query, params)
        product = result.fetchone()
        if product is None:
            flash("Product not found.")
            return redirect(url_for('admin'))
        else:
            return render_template('edit_product.html', product=product)


@app.route('/vendor')
def vendor():
    session_id = session.get('id')
    query = text("SELECT * FROM Products WHERE vendor_id = :session_id")
    result = connection.execute(query, {'session_id': session_id})
    products = []
    for row in result:
        products.append(row)
    return render_template('vendor.html', products=products)


@app.route('/vendor_add_product', methods=['POST'])
def vendor_add_product():
    max_id_query = text("SELECT MAX(product_id) FROM Products")
    max_id = connection.execute(max_id_query).fetchone()[0]
    new_id = max_id + 1 if max_id is not None else 1

    vendor_id = session.id
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    image = request.form['image']
    colors = request.form['colors']
    sizes = request.form['sizes']
    stock_total = request.form['stock_total']

    query = text("INSERT INTO Products (item_id, vendor_id, title, description, image, colors, sizes,"
                 " price, stock_total)"
                 " VALUES (:item_id, :vendor_id, :description, :colors, :sizes, :image,"
                 " :price, :stock_total)")
    params = {"product_id": new_id, "vendor_id": vendor_id, "title": title, "description": description,
              "price": price, "image": image, "colors": colors, "sizes": sizes, 'stock_total': stock_total}
    connection.execute(query, params)
    connection.commit()

    return url_for('vendor')


@app.route('/vendor_edit_product/<int:product_id>', methods=['GET', 'POST'])
def vendor_edit_product(product_id):
    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        title = request.form['title']
        description = request.form['description']
        image = request.form['image']
        colors = request.form['colors']
        sizes = request.form['sizes']
        stock_total = request.form['stock_total']
        price = request.form['price']
        query = text(
            "UPDATE Products SET vendor_id=:vendor_id, title=:title, description=:description, price=:price, "
            "image=:image, colors=:colors, sizes=:sizes stock_total=:stock_total WHERE product_id=:product_id")
        params = {"vendor_id": vendor_id, "title": title, "description": description,
                  "price": price, "image": image, "colors": colors, "sizes": sizes, 'stock_total': stock_total,
                  'product_id': product_id}
        connection.execute(query, params)
        connection.commit()
        flash("Product updated successfully.")
        return redirect(url_for('admin'))
    else:
        query = text("SELECT * FROM Products WHERE product_id=:product_id")
        params = {"product_id": product_id}
        result = connection.execute(query, params)
        product = result.fetchone()
        if product is None:
            flash("Product not found.")
            return redirect(url_for('admin'))
        else:
            return render_template('edit_product.html', product=product)


@app.route('/customer')
def customer():
    query = text("SELECT * FROM Products")
    result = connection.execute(query)
    products = []
    for row in result:
        products.append(row)
    return render_template('customer.html', products=products)


@app.route('/add_to_cart', methods=['POST', 'GET'])
def add_to_cart():
    if request.method == 'POST':
        query = text("select * from Products")
        res = connection.execute(query)
        products = []
        for row in res:
            products.append(row)
        max_id_query = text("select max(cart_id) as max_id FROM Cart")
        result = connection.execute(max_id_query).fetchone()
        max_id = result[0] if result[0] is not None else 1

        max_id = int(max_id)
        new_id = max_id + 1

        cart_id = new_id

        product_id = request.form['id']
        image = request.form['image']
        price = request.form['price']
        amount = request.form['amount']
        shopper_id = session['id']
        status = 'open'

        open_cart_query = text("select cart_id from Cart where shopper_id = :shopper_id AND status = 'open'")
        open_cart_result = connection.execute(open_cart_query, {"shopper_id": shopper_id}).fetchone()
        if open_cart_result:
            cart_id = open_cart_result[0]

            existing_item_query = text("SELECT * FROM Cart WHERE cart_id = :cart_id AND item_id = :item_id")
            existing_item_result = connection.execute(existing_item_query,
                                                      {"cart_id": cart_id, "product_id": product_id}).fetchone()
            if existing_item_result:
                existing_amount = int(existing_item_result[4])
                new_amount = existing_amount + int(amount)

                update_query = text("UPDATE Cart SET amount = :new_amount "
                                    "WHERE cart_id = :cart_id AND product_id = :product_id")
                update_params = {
                    "new_amount": new_amount,
                    "cart_id": cart_id,
                    "product_id": product_id
                }
                connection.execute(update_query, update_params)
                connection.commit()
            else:
                query = text("INSERT INTO Cart (cart_id, product_id, image, price, amount, shopper_id, status) "
                             "VALUES (:cart_id, :product_id, :image, :price, :amount, :shopper_id, :status)")
                params = {
                    "cart_id": cart_id,
                    "product_id": product_id,
                    'image': image,
                    "price": price,
                    "amount": amount,
                    "shopper_id": shopper_id,
                    "status": status
                }
                connection.execute(query, params)
                connection.commit()
        else:
            query = text("INSERT INTO Cart (cart_id, product_id, image, price, amount, shopper_id, status) "
                         "VALUES (:cart_id, :product_id, :image, :price, :amount, :shopper_id, :status)")
            params = {
                "cart_id": cart_id,
                "product_id": product_id,
                'image': image,
                "price": price,
                "amount": amount,
                "shopper_id": shopper_id,
                "status": status
            }
            connection.execute(query, params)
            connection.commit()

        return redirect(url_for('customer'))


@app.route('/acc_info')
def account_info():
    return render_template('acc_info.html')


@app.route('/view_chats')
def view_chats():
    user_id = session.get('id')

    query = text("SELECT c.chat_id, c.sender_id, c.recipient_id, c.text, a.username AS sender_username "
                 "FROM Chats c "
                 "INNER JOIN users a ON c.sender_id = a.id "
                 "WHERE c.sender_id = :user_id OR c.recipient_id = :user_id")
    params = {"user_id": user_id}
    result = connection.execute(query, params)
    messages = []
    for row in result:
        messages.append(row)
    return render_template('chats.html', messages=messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    sender_id = session.get('id')
    recipient_id = request.form['recipient_id']
    message_text = request.form['text']
    chat_id = f"chat_{sender_id}_{recipient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    query = text(
        "INSERT INTO Chat (chat_id, sender_id, recipient_id, text)"
        " VALUES (:chat_id, :sender_id, :recipient_id, :text)")
    params = {"chat_id": chat_id, "sender_id": sender_id, "recipient_id": recipient_id, "text": message_text}
    connection.execute(query, params)
    connection.commit()

    flash("Message sent successfully!")
    return redirect(url_for('view_chats'))


@app.route('/view_cart')
def view_cart():
    if 'id' in session:
        shopper_id = session['id']

        cart_query = text("SELECT * FROM Cart WHERE shopper_id = :shopper_id AND status = 'open'")
        cart_items = connection.execute(cart_query, {"shopper_id": shopper_id}).fetchall()

        cart_query = text("SELECT cart_id FROM Cart WHERE shopper_id = :shopper_id AND status = 'open'")
        cart_result = connection.execute(cart_query, {"shopper_id": shopper_id}).fetchone()
        cart_id = cart_result[0] if cart_result else None

        if cart_id is None:
            update_query = text(
                "INSERT INTO Cart (shopper_id, status) VALUES (:shopper_id, 'open') RETURNING cart_id")
            cart_id = connection.execute(update_query, {"shopper_id": shopper_id}).fetchone()[0]

        return render_template('cart.html', cart_items=cart_items, cart_id=cart_id)


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'id' in session:
        shopper_id = session['id']

        remove_query = text("DELETE FROM Cart WHERE product_id = :product_id AND shopper_id = :shopper_id")
        connection.execute(remove_query, {"product_id": product_id, "shopper_id": shopper_id})
        connection.commit()

        return redirect(url_for('view_cart'))


@app.route('/submit_order/<int:product_id>', methods=['POST'])
def submit_order(cart_id):
    query = text("UPDATE Cart SET status = 'closed' WHERE cart_id = :cart_id")
    connection.execute(query, {"cart_id": cart_id})
    connection.commit()

    flash("Order submitted successfully.")

    return redirect(url_for('customer'))


if __name__ == '__main__':
    app.run(debug=True)
