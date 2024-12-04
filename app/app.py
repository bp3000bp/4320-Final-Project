from flask import Flask, request, flash, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from .models import Reservation, Admin

def create_app():
    app = Flask(__name__, template_folder='../templates')  
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
    with app.app_context():
        # Create a seating chart (default is 'Available')
        seating_chart = [['Available' for _ in range(4)] for _ in range(12)]

        # Query the database for existing reservations
        reservations = db.session.query(Reservation).all()

        # Update the seating chart with reserved seats
        for res in reservations:
            seating_chart[res.seatRow - 1][res.seatColumn - 1] = 'Reserved'

        if request.method == 'POST':
            passengerName = request.form['passengerName']
            seatRow = int(request.form['seatRow'])
            seatColumn = int(request.form['seatColumn'])

            # Check if the selected seat is already reserved
            existing_reservation = db.session.query(Reservation).filter_by(
                seatRow=seatRow, seatColumn=seatColumn).first()

            if existing_reservation:
                # Display error if seat is taken
                flash("Seat already reserved. Please choose another seat.")
                return render_template('reserve.html', seating_chart=seating_chart, enumerate=enumerate)

            # Generate an eTicketNumber for the new reservation
            eTicketNumber = f"{seatRow}{seatColumn}{passengerName[:4]}"

            # Add the new reservation to the database
            new_reservation = Reservation(
                passengerName=passengerName,
                seatRow=seatRow,
                seatColumn=seatColumn,
                eTicketNumber=eTicketNumber
            )
            db.session.add(new_reservation)
            db.session.commit()

            # Success message
            flash(f"Reservation successful! Your eTicket number: {eTicketNumber}")
            return redirect(url_for('index'))

        # Render the form with the updated seating chart
        return render_template('reserve.html', seating_chart=seating_chart, enumerate=enumerate)




@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = db.session.query(Admin).filter_by(username=username, password=password).first()
        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials")
            return render_template('login.html')

    return render_template('login.html')

def calculate_total_sales():
    cost_matrix = [[100, 75, 50, 100] for _ in range(12)]
    
    reservations = db.session.query(Reservation).all()
    total_sales = sum(
        cost_matrix[res.seatRow - 1][res.seatColumn - 1] for res in reservations
    )
    return total_sales


@app.route('/admin_dashboard')
def admin_dashboard():
    seating_chart = [['Available' for _ in range(4)] for _ in range(12)]

    reservations = db.session.query(Reservation).all()

    for res in reservations:
        seating_chart[res.seatRow - 1][res.seatColumn - 1] = 'Reserved'

    total_sales = calculate_total_sales()

    return render_template('admin_dash.html', seating_chart=seating_chart, total_sales=total_sales)



if __name__ == '__main__':
    app.run(debug=True)
