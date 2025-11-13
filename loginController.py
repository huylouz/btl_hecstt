from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_very_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:118203@localhost/account'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class AccountManage(db.Model):
    __tablename__ = 'account_manage'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False, default='user')

    def __repr__(self):
        return f'<Account {self.user_name}>'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        gender = request.form['gender']

        existing_user = AccountManage.query.filter(
            (AccountManage.user_name == username) | (AccountManage.email == email)
        ).first()

        if existing_user:
            flash('Tên đăng nhập hoặc email đã tồn tại.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = AccountManage(
            user_name=username,
            password=hashed_password,
            email=email,
            address=address,
            phone_number=phone_number,
            gender=gender
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['user_name']
        password = request.form['password']

        user = AccountManage.query.filter_by(user_name=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.user_name

            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
            return redirect(url_for('login'))

    return render_template('signin.html')


@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Bạn cần đăng nhập để xem trang này.', 'warning')
        return redirect(url_for('login'))

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)

    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)