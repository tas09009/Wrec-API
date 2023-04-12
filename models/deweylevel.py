from db import db

class DeweyDecimalSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class DeweyLevel_1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    description = db.Column(db.String(500))
    value = 4
    dewey_decimal_system_id = db.Column(db.Integer, db.ForeignKey('dewey_decimal_system.id'))
    level_2 = db.relationship('DeweyLevel_2', backref='dewey_level_1', lazy=True)

class DeweyLevel_2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    description = db.Column(db.String(500))
    value = 3
    dewey_decimal_system_id = db.Column(db.Integer, db.ForeignKey('dewey_decimal_system.id'))
    level_1_id = db.Column(db.Integer, db.ForeignKey('dewey_level_1.id'))
    level_3 = db.relationship('DeweyLevel_3', backref='dewey_level_2', lazy=True)

class DeweyLevel_3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    description = db.Column(db.String(500))
    value = 2
    dewey_decimal_system_id = db.Column(db.Integer, db.ForeignKey('dewey_decimal_system.id'))
    level_2_id = db.Column(db.Integer, db.ForeignKey('dewey_level_2.id'))
