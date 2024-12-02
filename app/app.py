from flask import Flask, request, flash, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from .models import Reservation, Admin

# Configure the Flask app and explicitly set the templates folder
def create_app():
    app = Flask(__name__, template_folder='../templates')  # Explicitly set the templates folder location
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
    db = SQLAlchemy(app)
    return app, db

app, db = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve_seat():
    if request.method == 'POST':
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        row = int(request.form['row'])
        column = int(request.form['column'])

        # Generate reservation code
        reservation_code = f"{row}{column}{first_name[:2]}{last_name[:2]}"

        # Check if seat is already reserved
        existing_reservation = db.session.query(Reservation).filter_by(row=row, column=column).first()
        if existing_reservation:
            flash("Seat already reserved. Please choose another seat.")
            return render_template('reserve.html')

        # Add new reservation
        new_reservation = Reservation(
            first_name=first_name,
            last_name=last_name,
            row=row,
            column=column,
            reservation_code=reservation_code
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f"Reservation successful! Your code is {reservation_code}")
        return render_template('index.html')

    return render_template('reserve.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate credentials
        admin = db.session.query(Admin).filter_by(username=username, password=password).first()
        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials")
            return render_template('login.html')

    return render_template('login.html')

def calculate_total_sales():
    # Example pricing: $100 for row 1, $75 for row 2, etc.
    cost_matrix = [[100, 75, 50, 100] for _ in range(12)]
    reservations = db.session.query(Reservation).all()
    total_sales = sum(cost_matrix[res.row - 1][res.column - 1] for res in reservations)
    return total_sales

@app.route('/admin_dashboard')
def admin_dashboard():
    seating_chart = [['Available' for _ in range(4)] for _ in range(12)]
    reservations = db.session.query(Reservation).all()
    for res in reservations:
        seating_chart[res.row - 1][res.column - 1] = 'Reserved'
    total_sales = calculate_total_sales()
    return render_template('admin_dashboard.html', seating_chart=seating_chart, total_sales=total_sales)

if __name__ == '__main__':
    app.run(debug=True)
