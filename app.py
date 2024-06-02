import pymysql
from flask import Flask, request, jsonify, url_for, render_template_string, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import re
import uuid

hostname = 'localhost'
user = 'root'
password = ''

db = pymysql.connections.Connection(
    host=hostname,
    user=user,
    password=password
)

cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS ANS_db")

cursor.close()
db.close()

app = Flask(__name__)

# Configuring the Flask app to connect to the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/ANS_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating an instance of the SQLAlchemy class
db = SQLAlchemy(app)
bcrypt = Bcrypt()

# Configure Flask-Mail for Outlook
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ashesinavigationsystem@gmail.com'
app.config['MAIL_PASSWORD'] = 'mgdm zmub gvpo tifs'
app.config['MAIL_DEFAULT_SENDER'] = 'ashesinavigationsystem@gmail.com'

mail = Mail(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum('Active', 'Inactive'), nullable=False, default='Inactive')
    role = db.Column(db.String(50), nullable=False, default='User')
    activation_token = db.Column(db.String(36), unique=True, nullable=True)

    def __init__(self, email, password=None, status='Inactive', role='User'):
        self.email = email
        self.password_hash = None
        self.status = status
        self.role = role
        self.activation_token = str(uuid.uuid4())

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class BuildingCategory(db.Model):
    __tablename__ = 'building_category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Building(db.Model):
    __tablename__ = 'building'
    building_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    historical_information = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('building_category.category_id'))
    category = db.relationship('BuildingCategory', backref='buildings')



class RoomType(db.Model):
    __tablename__ = 'room_type'
    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Room(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.building_id'))
    type_id = db.Column(db.Integer, db.ForeignKey('room_type.type_id'))
    room_number = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    building = db.relationship('Building', backref='rooms')
    room_type = db.relationship('RoomType', backref='rooms')

class Event(db.Model):
    __tablename__ = 'event'
    event_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))
    name = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    room = db.relationship('Room', backref='events')



with app.app_context():
    db.create_all()


@app.route('/activate/<token>', methods=['GET'])
def activate_user(token):
    user = User.query.filter_by(activation_token=token).first()
    

    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400

    # user.status = 'Active'
    # user.activation_token = None
    # db.session.commit()


    return render_template('set_password.html', token=token)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Check if email and password fields are provided
    if not data or 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400

    email = data.get('email')
    role = data.get('role', 'User')

    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return jsonify({'message': 'Invalid email format'}), 400

    # Check if a user with the given email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User with this email already exists'}), 400

        # If the user does not exist, create a new user
    user = User(email=email, role=role)
    db.session.add(user)
    db.session.commit()

    mail_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email</title>
        <style>
            .email-container {
                max-width: 600px;
                margin: auto;
                padding: 20px;
                font-family: Arial, sans-serif;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
            .email-header {
                text-align: center;
                margin-bottom: 20px;
            }
            .email-logo {
                max-width: 100px;
            }
            .email-body {
                text-align: center;
            }

            .email-body h2{
                color: #AA3B3E;
            }
            
            .email-footer {
                text-align: center;
                margin-top: 20px;
                color: #888;
                font-size: 12px;
            }
            .activation-button {
                background-color: #AA3B3E;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <img src="{{url_for('static', filename="logo.png")}}" alt="Logo" class="email-logo">
            </div>
            <div class="email-body">
                <h2>Verify Your Email</h2>
                <p>Thank you for registering. Please click the button below to verify your email address and activate your account:</p>
                <a href="{{ activation_url }}" class="activation-button">Activate Your Account</a>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="email-footer">
                <p>If you didn't request this, you can safely ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    '''


    token = user.activation_token
    activation_url = url_for('activate_user', token=token, _external=True)
    msg = Message('Account Activation', sender='ashesinavigationsystem@gmail.com', recipients=[email])
    msg.html = render_template_string(mail_html, activation_url=activation_url)
    mail.send(msg)

    return jsonify({'message': 'User created successfully. Please check email to activate account.'}), 201



@app.route('/set-password', methods=['POST'])
def set_password():
    token = request.form['token']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User.query.filter_by(activation_token=token).first()
    if user:
        user.password_hash = hashed_password
        user.activation_token = None  # Clear the token after use
        user.status = 'Active'
        db.session.commit()
        return render_template('password_successful.html')
        
    else:
        #To-do
        return jsonify({"message": "Invalid or expired token"})




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()


    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'})

    email = data.get('email')
    password = data.get('password')

    # Check if the user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Invalid email'}), 401

    # Verify the password
    if not user.check_password(password):
        return jsonify({'message': 'Invalid password'}), 401

        # Check if the user is active
    if user.status != 'Active':
        return jsonify({'message': 'User account is not active'}), 403
    
    return jsonify({'message': 'Login successful'}), 200


@app.route('/buildings', methods=['GET'])
def get_buildings():
    buildings = Building.query.all()
    results = []

    for building in buildings:
        building_info = {
            'name': building.name,
            'description': building.description,
            'category': building.category.name,
            'history': building.historical_information,
            'latitude': building.latitude,
            'longitude': building.longitude,
            'rooms': [
                {
                    'room_number': room.room_number,
                    'type': room.room_type.name,
                    'building': room.building.name,
                    'capacity': room.capacity
                }
                for room in building.rooms
            ]
        }
        results.append(building_info)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)