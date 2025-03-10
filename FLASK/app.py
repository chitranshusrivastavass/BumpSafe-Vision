from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt, checkpw




app=Flask(__name__)

app.secret = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
    
    def checkpassword(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
with app.app_context():
    db.create_all()
    
    




@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        try:
            exist = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()
            if exist:
                return render_template('signup.html', error='User already exists')
        except:
            pass
        user = User(email, username, password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    

@app.route('/login' , methods=['POST', 'GET']) 
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() or User.query.filter_by(username=email).first()
        if user:
            if user.checkpassword(password):
                session['user'] = user.username
                return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')




if __name__=='__main__':
    app.run(debug=True)