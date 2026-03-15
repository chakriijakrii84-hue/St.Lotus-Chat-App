import os, base64
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Folder မရှိရင် ဆောက်မယ်
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# SocketIO ကို CORS error မတက်အောင် ပြင်ဆင်ထားပါတယ်
socketio = SocketIO(app, cors_allowed_origins="*")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        user = User.query.filter_by(phone=phone).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        flash('ဖုန်းနံပါတ် ရှာမတွေ့ပါ။ အကောင့်အရင်ဖွင့်ပါ။')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        username = request.form.get('username')
        if User.query.filter_by(phone=phone).first():
            flash('ဒီဖုန်းနံပါတ်နဲ့ အကောင့်ရှိပြီးသားပါ။')
        else:
            new_user = User(phone=phone, username=username)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template('register.html')

@socketio.on('message')
def handle_message(data):
    emit('message', {'user': current_user.username, 'message': data['message']}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5000)
