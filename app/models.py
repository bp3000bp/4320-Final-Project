from . import db

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(50), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(100), unique=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())


class Admin(db.Model):
    __tablename__ = 'admins'

    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)