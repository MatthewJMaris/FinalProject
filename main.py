from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)

conn_str = "mysql://root:Lorx3492345!@localhost/companydb"
engine = create_engine(conn_str, echo=True)
connection = engine.connect()


@app.route('/')
def index():
    return render_template('index.html')


class Customer:
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=False)


@app.route('/register', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        if not (username and password and email and full_name):
            return "Please fill in all the fields"
        try:
            # connection.execute(text("INSERT INTO customers (user_id, username, password, email, full_name,
            # ) VALUES (" ":user_id, :username, :password, :email, :full_name)"), {'user_id': user_id, 'username':
            # username, 'password': password, 'email': email, 'full_name': full_name})
            new_customer = Customer(user_id=user_id, username=username, password=password, email=email, full_name=full_name)
            connection.add(new_customer)
            connection.commit()
            print()
            return "Registration successful"
        except Exception as e:
            print(e)
            return "Registration failed"
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
