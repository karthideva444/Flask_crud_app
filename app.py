from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# Flask-Admin setup
admin = Admin(app, name='User Management', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))

# Index page to display all users
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Create new user
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        address = request.form['address']
        # Data validation
        has_error = False
        if len(phone_number) < 10:
            flash('Error: Phone number must be at least 10 digits long!')
            has_error = True
        # Save user to in-memory storage
        if not has_error:    
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                address=address
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully!')
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                flash('Error: Phone number or email already exists!')                                           
    return render_template('create.html') 

# Update user
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get(id)
    if user is None:
        flash('User not found')
        return redirect(url_for('index'))

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.phone_number = request.form['phone_number']
        user.email = request.form['email']
        user.address = request.form['address']
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('index'))

    return render_template('edit.html', user=user)

# Delete user
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    user = User.query.get(id)
    if user:
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully!')
    else:
        flash('User not found')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
