from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
app = Flask(__name__)

conn_str = "mysql://root:Lorx3492345!@localhost/companydb"
engine = create_engine(conn_str, echo=True)
connection = engine.connect()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def create_boats():
    connection.execute(text("insert into companydb values (:id, :username, :password, :email, :full_name, :type)"), request.form)
    connection.commit()
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
