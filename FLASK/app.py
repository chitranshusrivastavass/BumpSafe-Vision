from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt, checkpw
import folium
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Speed bump detector model setup
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 32 * 32, 128)
        self.fc2 = nn.Linear(128, 2)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, kernel_size=2, stride=2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, kernel_size=2, stride=2)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Initialize model and transform
model = SimpleCNN()
checkpoint = torch.load(r'C:\Users\rahul\OneDrive\Desktop\BumpSafe-Vision\FLASK\speed_bump_detector.pth', map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Define the same transform used during training
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

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
    detection_result = None
    marker_added = False

    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lon = float(request.form['longitude'])
        except ValueError:
            return render_template('mapinput.html', error="Invalid coordinates", map_html=None)

        # Handle image upload and detection
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                # Process the image
                image = Image.open(image_file)
                image_tensor = transform(image).unsqueeze(0)
                
                with torch.no_grad():
                    outputs = model(image_tensor)
                    _, predicted = torch.max(outputs.data, 1)
                    is_speed_bump = predicted.item() == 1
                    detection_result = "Speed Bump Detected!" if is_speed_bump else "No Speed Bump Detected"
                    marker_added = is_speed_bump  # Only set marker_added to True if speed bump is detected

    # Create the map using Folium
    coords = (lat, lon)
    my_map = folium.Map(location=coords, zoom_start=17)
    
    if marker_added:
        # Add a custom marker for speed bump detection
        folium.Marker(
            location=coords,
            popup="Speed Bump Detected Here!",
            icon=folium.Icon(color='red', icon='warning-sign', prefix='fa')  # Using FontAwesome warning icon
        ).add_to(my_map)
    else:
        # Add a default marker if no speed bump detected or no detection performed
        folium.Marker(
            location=coords,
            popup="Location"
        ).add_to(my_map)

    map_html = my_map._repr_html_()

    return render_template('mapinput.html', map_html=map_html, 
                         latitude=lat, longitude=lon,
                         detection_result=detection_result)

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
