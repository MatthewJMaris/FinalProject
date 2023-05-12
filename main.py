from flask import Flask, render_template, request, session, url_for, redirect, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, engine, and_

app = Flask(__name__)

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


# Handles the login screen and will redirect you to the appropriate page
# If your account is either an Admin, Customer, or Vendor
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'placholder' or password == 'Placeholder':
            password = password
        else:
            password = h(password)
        query = text("select * from customers where username = :username and password = :password")
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
    all_id_queries = text("select max(id) from customers")
    all_id = connection.execute(all_id_queries).fetchone()[0]
    new_id = all_id + 1 if all_id is not None else 1

    username = request.form['username']
    email = request.form['email']
    full_name = request.form['full_name']
    password = request.form['password']
    password = h(password)
    type = 'customer'
    user = connection.execute(text("select * from users where email= :email"), {'email': email}).fetchone()
    if user is not None:
        flash("An account with this email address already exists.")
        return redirect(url_for('register'))
    else:
        query = text("insert into users (user_id, username, email, full_name, password, type) values (:user_id, "
                     ":username, :email, :full_name, :password, :type)")
        params = {"id": new_id, "username": username, "email": email, "fullname": full_name, "password": password, "type": type}

        connection.execute(query, params)
        connection.commit()
    return render_template('index.html')


# Handles where you will get registered when you
# Click 'Register Here!' on the main page.
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
