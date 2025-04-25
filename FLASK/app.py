'''from flask import Flask, render_template, request, redirect, url_for, session
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
    return render_template('tailwind_index.html')

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
        return redirect(url_for('tailwind_signup.html'))
    

@app.route('/login' , methods=['POST', 'GET']) 
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() or User.query.filter_by(username=email).first()
        if user:
            if user.checkpassword(password):
                session['user'] = user.username
                return redirect(url_for('/home.html'))#dashboard
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')




if __name__=='__main__':
    app.run(debug=True)
    
    
import folium
import os   
from flask import Flask, render_template,request
app=Flask(__name__)

@app.route('/')
def home():
    return render_template('tailwind_index.html')

@app.route('/signup')
def signup():
    return render_template('tailwind_signup.html')

@app.route('/register')
def register():
    return render_template('tailwind_register.html')

@app.route('/about')
def about():
    return render_template('tailwind_about.html')

@app.route('/contact')
def contact():
    return render_template('tailwind_contact.html')

#@app.route('/BSV')
#def BSV():
 #   return render_template('tailwind_BSV.html')

@app.route('/BSV')
def map():
    return render_template('index.html')


if __name__=='__main__':
    app.run(debug=True)
    
    
 #folium code   
    
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lon = float(request.form['longitude'])
            coords = (lat, lon)

            # Generate Folium map
            my_map = folium.Map(location=coords, zoom_start=17)
            folium.Marker(location=coords, popup="Your Location").add_to(my_map)
            my_map.save('templates/map.html')

            return render_template('index.html', show_map=True)
        except ValueError:
            return render_template('index.html', error="Invalid coordinates", show_map=False)
    return render_template('index.html', show_map=False)
    
@app.route('/map')
def map_view():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    ###############################
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt, checkpw
import folium

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# -------------------- Models --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def checkpassword(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template('tailwind_index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return render_template('signup.html', error='User already exists')
        hashed_pw = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        user = User(email=email, username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() or User.query.filter_by(username=email).first()
        if user and user.checkpassword(password):
            session['user'] = user.username
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# -------------------- Map Input --------------------
@app.route('/mapinput', methods=['GET', 'POST'])
def mapinput():
    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lon = float(request.form['longitude'])
            coords = (lat, lon)

            # Generate Folium map
            my_map = folium.Map(location=coords, zoom_start=17)
            folium.Marker(location=coords, popup="Your Location").add_to(my_map)
            my_map.save('templates/map.html')

            return redirect(url_for('map_view'))
        except ValueError:
            return render_template('mapinput.html', error="Invalid coordinates")
    return render_template('mapinput.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

# -------------------- Other Static Pages --------------------
@app.route('/register')
def register():
    return render_template('tailwind_register.html')

@app.route('/about')
def about():
    return render_template('tailwind_about.html')

@app.route('/contact')
def contact():
    return render_template('tailwind_contact.html')


# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(debug=True)
'''

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt, checkpw
import folium
import os

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# -------------------- User Model --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def checkpassword(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template('tailwind_index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return render_template('signup.html', error='User already exists')
        hashed_pw = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        user = User(email=email, username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('tailwind_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() or User.query.filter_by(username=email).first()
        if user and user.checkpassword(password):
            session['user'] = user.username
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# -------------------- Map Input and Display --------------------
@app.route('/mapinput', methods=['GET', 'POST'])
def mapinput():
    map_html = None
    lat = 26.8467   # default latitude (Lucknow)
    lon = 80.9462   # default longitude

    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lon = float(request.form['longitude'])
        except ValueError:
            return render_template('mapinput.html', error="Invalid coordinates", map_html=None)

    # Create the map using Folium
    coords = (lat, lon)
    my_map = folium.Map(location=coords, zoom_start=17)
    folium.Marker(location=coords, popup="Your Location").add_to(my_map)
    map_html = my_map._repr_html_()  # returns HTML representation

    return render_template('mapinput.html', map_html=map_html, latitude=lat, longitude=lon)

# -------------------- Other Pages --------------------
@app.route('/register')
def register():
    return render_template('tailwind_register.html')

@app.route('/about')
def about():
    return render_template('tailwind_about.html')

@app.route('/contact')
def contact():
    return render_template('tailwind_contact.html')

# -------------------- Run the App --------------------
if __name__ == '__main__':
    app.run(debug=True)
